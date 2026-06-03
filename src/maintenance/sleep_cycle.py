import re
import time
from typing import Dict, Any, List

def normalize_arabic(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Remove diacritics
    text = re.sub(r"[\u064B-\u0652]", "", text)
    # Normalize Alef
    text = re.sub(r"[أإآ]", "ا", text)
    # Normalize Teh Marbuta
    text = re.sub(r"ة", "eh", text) # Let's match to a normalized letter so they equate correctly
    text = re.sub(r"ة", "ه", text)
    # Normalize Yeh
    text = re.sub(r"[ى]", "ي", text)
    return text.strip()

def calculate_levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return calculate_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

class CognitiveSleepCycle:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def run_sleep_cycle(self) -> Dict[str, Any]:
        """
        Runs the full Cognitive Sleep Cycle.
        Returns statistics of the run.
        """
        start_time = time.perf_counter()
        stats = {
            "synonyms_linked": 0,
            "edges_strengthened": 0,
            "edges_pruned": 0,
            "noise_nodes_cleaned": 0
        }

        # Stage 1: Linguistic Synonym Merge & Grouping
        stats["synonyms_linked"] = self.merge_similar_nodes()

        # Stage 2: Weak Edge Pruning
        stats["edges_pruned"] = self.remove_low_confidence_edges(threshold=0.1)

        # Stage 3: Triangle/Path Strengthening
        stats["edges_strengthened"] = self.strengthen_transitive_paths()

        # Stage 4: Cognitive Hygiene (Isolated nodes cleanup)
        stats["noise_nodes_cleaned"] = self.flag_and_clean_isolated_nodes()

        # Stage 5: Save Databases to file
        self.handler.save_databases()

        elapsed = (time.perf_counter() - start_time) * 1000.0
        stats["elapsed_ms"] = elapsed
        return stats

    def merge_similar_nodes(self) -> int:
        """
        Merges concept nodes that are spelling variants.
        Uses exact normalized match or Levenshtein distance <= 1 for nodes of length > 4.
        """
        graph = self.handler.graph
        nodes = list(graph.nodes())
        merged_count = 0
        
        # We will scan pairs of nodes
        processed = set()
        
        for i in range(len(nodes)):
            node_A = nodes[i]
            if not graph.has_node(node_A):
                continue
            if graph.nodes[node_A].get("type") != "concept":
                continue
                
            for j in range(i + 1, len(nodes)):
                node_B = nodes[j]
                if not graph.has_node(node_B):
                    continue
                if graph.nodes[node_B].get("type") != "concept":
                    continue
                    
                pair = tuple(sorted([node_A, node_B]))
                if pair in processed:
                    continue
                processed.add(pair)
                
                # Check normalized equivalence
                norm_A = normalize_arabic(node_A)
                norm_B = normalize_arabic(node_B)
                
                is_duplicate = False
                if norm_A == norm_B:
                    is_duplicate = True
                else:
                    # Levenshtein check
                    dist = calculate_levenshtein(norm_A, norm_B)
                    if dist <= 1 and len(norm_A) > 4 and len(norm_B) > 4:
                        is_duplicate = True
                
                if is_duplicate and graph.has_node(node_A) and graph.has_node(node_B):
                    # Keep the one with higher degree
                    deg_A = graph.degree(node_A)
                    deg_B = graph.degree(node_B)
                    
                    canonical = node_A if deg_A >= deg_B else node_B
                    duplicate = node_B if canonical == node_A else node_A
                    
                    # Merge labels
                    can_lbls = graph.nodes[canonical].get("labels", [])
                    dup_lbls = graph.nodes[duplicate].get("labels", [])
                    for lbl in dup_lbls:
                        if lbl not in can_lbls:
                            can_lbls.append(lbl)
                    graph.nodes[canonical]["labels"] = can_lbls
                    
                    # Move out edges
                    for _, target, key, data in list(graph.out_edges(duplicate, data=True, keys=True)):
                        if target == canonical:
                            continue
                        if not graph.has_edge(canonical, target):
                            graph.add_edge(canonical, target, **data)
                            
                    # Move in edges
                    for source, _, key, data in list(graph.in_edges(duplicate, data=True, keys=True)):
                        if source == canonical:
                            continue
                        if not graph.has_edge(source, canonical):
                            graph.add_edge(source, canonical, **data)
                            
                    graph.remove_node(duplicate)
                    merged_count += 1
                    
        return merged_count

    def remove_low_confidence_edges(self, threshold: float = 0.1) -> int:
        """
        Deletes fact edges with confidence below threshold.
        """
        graph = self.handler.graph
        pruned_count = 0
        
        edges_to_prune = []
        for u, v, key, data in list(graph.edges(data=True, keys=True)):
            if data.get("type") == "fact":
                conf = data.get("confidence", 1.0)
                if conf < threshold:
                    edges_to_prune.append((u, v, key))
                    
        for u, v, key in edges_to_prune:
            graph.remove_edge(u, v, key=key)
            pruned_count += 1
            
        return pruned_count

    def strengthen_transitive_paths(self) -> int:
        """
        If A -> B -> C (transitive path) and direct edge A -> C exists, reinforces A -> C.
        """
        graph = self.handler.graph
        strengthened_count = 0
        
        for u, v, key, data in list(graph.edges(data=True, keys=True)):
            rel = data.get("relation")
            if rel in ["is_a", "مرادف_لـ"] or data.get("type") != "fact":
                continue
                
            successors_u = set(graph.successors(u))
            successors_v = set(graph.successors(v))
            shared = successors_u & successors_v
            
            if shared:
                # Add co-occurrence boost
                boost = len(shared) * 0.05
                old_conf = data.get("confidence", 1.0)
                new_conf = min(1.0, old_conf + boost)
                
                if new_conf > old_conf:
                    data["confidence"] = new_conf
                    strengthened_count += 1
                    
        return strengthened_count

    def flag_and_clean_isolated_nodes(self) -> int:
        """
        Identifies and removes short concepts (len <= 2) that are completely isolated or have degree <= 1.
        """
        graph = self.handler.graph
        cleaned_count = 0
        
        for node in list(graph.nodes()):
            if graph.nodes[node].get("type") == "concept":
                deg = graph.degree(node)
                if deg == 0:
                    graph.remove_node(node)
                    cleaned_count += 1
                elif deg <= 1 and len(normalize_arabic(node)) <= 2:
                    graph.remove_node(node)
                    cleaned_count += 1
                    
        return cleaned_count
