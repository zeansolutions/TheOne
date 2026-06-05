import urllib.request
import json
import urllib.parse
import time
import socket
from typing import Dict, List, Any, Optional
from src.utils.logger import logger

class DataImporter:
    """
    On-demand knowledge importer that fetches semantic relations from ConceptNet
    and persists them directly into the SQLite-backed graph database.
    """
    def __init__(self, graph_handler):
        self.gh = graph_handler

    def enrich_concept(self, concept_label: str, language: str = "ar", trace: Optional[List[str]] = None) -> bool:
        """
        Fetches relations for a given concept label from ConceptNet and stores them.
        Includes console feedback, status tracking, and graceful network fallbacks.
        """
        # Canonicalize language code (ConceptNet uses ISO codes)
        lang_code = "ar" if language == "ar" else "en" if language == "en" else "fr"
        
        # Clean label for API query
        clean_label = concept_label.strip().replace(" ", "_")
        encoded_label = urllib.parse.quote(clean_label)
        api_url = f"http://api.conceptnet.io/c/{lang_code}/{encoded_label}"

        msg = f"[KNOWLEDGE IMPORT] Connecting to ConceptNet for '{concept_label}' ({language})..."
        print(msg)
        logger.info(msg)
        if trace is not None:
            trace.append(msg)

        start_time = time.time()
        try:
            # Set a tight socket timeout (3 seconds) to prevent freezing if network is down
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'LEGEND-Cognitive-System/1.0 (Contact: developer@theone.ai)'}
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            edges = data.get("edges", [])
            if not edges:
                msg = f"[KNOWLEDGE IMPORT] No external relations found for '{concept_label}'."
                print(msg)
                logger.info(msg)
                if trace is not None:
                    trace.append(msg)
                return False

            imported_count = 0
            
            # Temporarily disable loading flag on graph to ensure items are written to SQLite
            if hasattr(self.gh.graph, "_loading"):
                self.gh.graph._loading = False

            # Add the central concept node if not exists
            concept_id = concept_label.strip()
            if not self.gh.graph.has_node(concept_id):
                self.gh.graph.add_node(concept_id, labels=[concept_label], category="concept", confidence=1.0)

            for edge in edges:
                weight = edge.get("weight", 1.0)
                # Filter low weight edges to ensure concept graph quality
                if weight < 1.0:
                    continue

                rel_data = edge.get("rel", {})
                rel_id = rel_data.get("@id", "")
                # Clean relation ID, e.g., /r/IsA -> is_a
                relation_name = rel_id.split("/")[-1].lower() if "/" in rel_id else rel_id

                start_node = edge.get("start", {})
                end_node = edge.get("end", {})

                start_lang = start_node.get("language", "")
                end_lang = end_node.get("language", "")

                # Only import concepts that match target language to keep the graph aligned
                if start_lang != lang_code or end_lang != lang_code:
                    continue

                start_label = start_node.get("label", "")
                end_label = end_node.get("label", "")

                if not start_label or not end_label:
                    continue

                # Add nodes to graph
                if not self.gh.graph.has_node(start_label):
                    self.gh.graph.add_node(start_label, labels=[start_label], category="concept", confidence=1.0)
                if not self.gh.graph.has_node(end_label):
                    self.gh.graph.add_node(end_label, labels=[end_label], category="concept", confidence=1.0)

                # Add relationship edge
                self.gh.graph.add_edge(
                    start_label,
                    end_label,
                    relation=relation_name,
                    type="fact",
                    world="reality",
                    confidence=min(1.0, float(weight) / 5.0), # Normalize weight score
                    reason="Imported from ConceptNet API",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    source="external_importer",
                    status="active"
                )
                imported_count += 1

            duration = time.time() - start_time
            msg = f"[KNOWLEDGE IMPORT] Success: Imported {imported_count} relations for '{concept_label}' in {duration:.2f}s."
            print(msg)
            logger.info(msg)
            if trace is not None:
                trace.append(msg)
            return True

        except (urllib.error.URLError, socket.timeout, Exception) as e:
            duration = time.time() - start_time
            err_msg = f"[KNOWLEDGE IMPORT] Offline Mode: Could not reach ConceptNet ({type(e).__name__}). Proceeding with local graph."
            print(err_msg)
            logger.warning(err_msg)
            if trace is not None:
                trace.append(err_msg)
            return False
