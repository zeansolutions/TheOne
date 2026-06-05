import Levenshtein
from typing import List, Dict, Any, Tuple
from src.utils.logger import logger

class DataValidator:
    """
    Rule-based validator for the graph database.
    Performs fuzzy deduplication, flags logical contradictions, and purges low-confidence facts.
    """
    def __init__(self, graph_handler):
        self.gh = graph_handler

    def _normalize_text(self, text: str) -> str:
        """Normalizes text for comparison, with specialized Arabic character alignment."""
        text = text.strip().lower()
        # Arabic character normalization
        for char in ['أ', 'إ', 'آ']:
            text = text.replace(char, 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ى', 'ي')
        return text

    def run_validation(self, confidence_threshold: float = 0.3, similarity_threshold: float = 0.92) -> Dict[str, Any]:
        """
        Executes validation pipelines on the active graph.
        Returns a summary report of findings and corrections.
        """
        report = {
            "low_confidence_purged": 0,
            "duplicates_merged": 0,
            "contradictions_detected": 0,
            "details": []
        }

        # 1. Purge low-confidence edges
        edges_to_remove = []
        for u, v, key, data in list(self.gh.graph.edges(data=True, keys=True)):
            confidence = data.get("confidence", 1.0)
            if confidence < confidence_threshold:
                edges_to_remove.append((u, v, key))

        for u, v, key in edges_to_remove:
            self.gh.graph.remove_edge(u, v, key=key)
            report["low_confidence_purged"] += 1
            report["details"].append(f"Purged edge: {u} -> {v} due to low confidence.")

        # 2. Fuzzy Deduplication: Find similar concepts
        nodes = list(self.gh.graph.nodes)
        nodes_to_merge = []
        visited = set()

        for i, node1 in enumerate(nodes):
            if node1 in visited:
                continue
            norm1 = self._normalize_text(node1)
            for node2 in nodes[i+1:]:
                if node2 in visited:
                    continue
                
                norm2 = self._normalize_text(node2)
                # Compute Normalized Levenshtein similarity on normalized text
                max_len = max(len(norm1), len(norm2))
                if max_len == 0:
                    continue
                dist = Levenshtein.distance(norm1, norm2)
                sim = 1.0 - (dist / max_len)

                if sim >= similarity_threshold:
                    nodes_to_merge.append((node1, node2))
                    visited.add(node2)
            visited.add(node1)

        # Merge similar concepts
        for keep, discard in nodes_to_merge:
            self._merge_concepts(keep, discard)
            report["duplicates_merged"] += 1
            report["details"].append(f"Merged duplicate concepts: '{discard}' merged into '{keep}'.")

        # 3. Detect Contradictions
        # e.g., opposite properties or same subject-predicate with opposite mod/polarity
        contradictions = self._detect_contradictions()
        report["contradictions_detected"] = len(contradictions)
        for c in contradictions:
            report["details"].append(f"Contradiction detected: {c}")

        logger.info(f"Validation run completed. Purged: {report['low_confidence_purged']}, Merged: {report['duplicates_merged']}, Contradictions: {report['contradictions_detected']}")
        return report

    def _merge_concepts(self, keep: str, discard: str):
        """Merges two concepts in the graph, transferring edges and labels."""
        # 1. Update labels of keep node
        keep_data = self.gh.graph.nodes[keep]
        discard_data = self.gh.graph.nodes[discard]
        
        keep_labels = set(keep_data.get("labels", [keep]))
        discard_labels = set(discard_data.get("labels", [discard]))
        
        # Update keep labels in SQLite
        self.gh.graph.add_node(
            keep, 
            labels=list(keep_labels.union(discard_labels)),
            category=keep_data.get("category", discard_data.get("category")),
            confidence=max(keep_data.get("confidence", 1.0), discard_data.get("confidence", 1.0))
        )

        # 2. Move out-edges from discard to keep
        for _, target, key, data in list(self.gh.graph.out_edges(discard, data=True, keys=True)):
            # If the same edge already exists on keep, update confidence, else add new
            self.gh.graph.add_edge(keep, target, **data)

        # 3. Move in-edges from discard to keep
        for source, _, key, data in list(self.gh.graph.in_edges(discard, data=True, keys=True)):
            self.gh.graph.add_edge(source, keep, **data)

        # 4. Remove discard node (which removes its SQLite records automatically)
        self.gh.graph.remove_node(discard)

    def _detect_contradictions(self) -> List[str]:
        """Scans the active graph for structural/logical contradictions."""
        contradictions = []
        # Check for opposite properties on the same subject
        # e.g. Subject is_a X and Subject is_not_a X
        for u in self.gh.graph.nodes:
            negations = set()
            assertions = set()
            for _, target, data in self.gh.graph.out_edges(u, data=True):
                relation = data.get("relation", "")
                if relation in ["is_not_a", "not_a", "not_capable_of"]:
                    negations.add(target)
                elif relation in ["is_a", "capable_of", "can_do"]:
                    assertions.add(target)
            
            intersection = assertions.intersection(negations)
            if intersection:
                for target in intersection:
                    contradictions.append(f"Subject '{u}' both asserted and negated relation with '{target}'.")
        return contradictions
