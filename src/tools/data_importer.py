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
    and falls back to Wikidata if ConceptNet is experiencing an outage.
    """
    def __init__(self, graph_handler):
        self.gh = graph_handler

    def enrich_concept(self, concept_label: str, language: str = "ar", trace: Optional[List[str]] = None) -> bool:
        """
        Fetches relations for a given concept label from ConceptNet,
        falling back to Wikidata on outage, and stores them in the SQLite graph.
        """
        # Pacing to avoid rate limiting
        time.sleep(1.0)

        lang_code = "ar" if language == "ar" else "en" if language == "en" else "fr"
        
        # Try ConceptNet first
        success = self._fetch_from_conceptnet(concept_label, lang_code, trace)
        if not success:
            # If ConceptNet failed (e.g. 502 Bad Gateway), fall back to Wikidata
            msg_fallback = f"[KNOWLEDGE IMPORT] ConceptNet down. Falling back to Wikidata for '{concept_label}'..."
            print(msg_fallback)
            logger.info(msg_fallback)
            if trace is not None:
                trace.append(msg_fallback)
            success = self._fetch_from_wikidata(concept_label, lang_code, trace)

        if success:
            # Post-import: linguistically cross-link compound concepts
            self._cross_link_compound_concepts()
            return True
        return False

    def _cross_link_compound_concepts(self):
        """
        Linguistic rule: links compound concepts to their base concepts
        e.g., 'طائر جارح' -> is_a -> 'طائر' if 'طائر' exists in the graph.
        Handles Arabic (first word head) and English (last word head).
        """
        for node in list(self.gh.graph.nodes):
            words = node.split()
            if len(words) > 1:
                # 1. Try first word (Arabic, e.g. "طائر" in "طائر جارح")
                head_candidate_ar = words[0]
                for pref in ["ال", "وبال", "بال", "وال", "لل", "ب", "و", "ل", "ف"]:
                    if head_candidate_ar.startswith(pref) and len(head_candidate_ar) > len(pref):
                        head_candidate_ar = head_candidate_ar[len(pref):]
                        break
                
                # 2. Try last word (English, e.g. "bear" in "polar bear")
                head_candidate_en = words[-1].lower()

                for head_cand in [head_candidate_ar, head_candidate_en]:
                    matched_node = None
                    if self.gh.graph.has_node(head_cand):
                        matched_node = head_cand
                    else:
                        for n, ndata in self.gh.graph.nodes(data=True):
                            labels = [l.lower() for l in ndata.get("labels", [])]
                            if head_cand.lower() == n.lower() or head_cand.lower() in labels:
                                matched_node = n
                                break
                    
                    if matched_node and matched_node != node:
                        # Add is_a link from compound to base concept
                        self.gh.graph.add_edge(
                            node,
                            matched_node,
                            relation="is_a",
                            type="fact",
                            world="reality",
                            confidence=0.95,
                            reason=f"Linguistic compound cross-link: '{node}' is a type of '{matched_node}'",
                            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            source="external_importer",
                            status="active"
                        )

    def _fetch_from_conceptnet(self, concept_label: str, lang_code: str, trace: Optional[List[str]]) -> bool:
        clean_label = concept_label.strip().replace(" ", "_")
        encoded_label = urllib.parse.quote(clean_label)
        api_url = f"http://api.conceptnet.io/c/{lang_code}/{encoded_label}"

        msg = f"[KNOWLEDGE IMPORT] Connecting to ConceptNet for '{concept_label}' ({lang_code})..."
        print(msg)
        logger.info(msg)
        if trace is not None:
            trace.append(msg)

        try:
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'LEGEND-Cognitive-System/1.0 (Contact: developer@theone.ai)'}
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            edges = data.get("edges", [])
            if not edges:
                return False

            imported_count = 0
            if hasattr(self.gh.graph, "_loading"):
                self.gh.graph._loading = False

            concept_id = concept_label.strip()
            if not self.gh.graph.has_node(concept_id):
                self.gh.graph.add_node(concept_id, labels=[concept_label], category="concept", type="concept", confidence=1.0)

            for edge in edges:
                weight = edge.get("weight", 1.0)
                if weight < 1.0:
                    continue

                rel_data = edge.get("rel", {})
                rel_id = rel_data.get("@id", "")
                relation_name = rel_id.split("/")[-1].lower() if "/" in rel_id else rel_id

                start_node = edge.get("start", {})
                end_node = edge.get("end", {})
                start_lang = start_node.get("language", "")
                end_lang = end_node.get("language", "")

                if start_lang != lang_code or end_lang != lang_code:
                    continue

                start_label = start_node.get("label", "")
                end_label = end_node.get("label", "")
                if not start_label or not end_label:
                    continue

                if not self.gh.graph.has_node(start_label):
                    self.gh.graph.add_node(start_label, labels=[start_label], category="concept", type="concept", confidence=1.0)
                if not self.gh.graph.has_node(end_label):
                    self.gh.graph.add_node(end_label, labels=[end_label], category="concept", type="concept", confidence=1.0)

                self.gh.graph.add_edge(
                    start_label,
                    end_label,
                    relation=relation_name,
                    type="fact",
                    world="reality",
                    confidence=min(1.0, float(weight) / 5.0),
                    reason="Imported from ConceptNet API",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    source="external_importer",
                    status="active"
                )
                imported_count += 1

            msg_success = f"[KNOWLEDGE IMPORT] Success: Imported {imported_count} relations from ConceptNet."
            print(msg_success)
            logger.info(msg_success)
            if trace is not None:
                trace.append(msg_success)
            return True

        except Exception as e:
            return False

    def _fetch_from_wikidata(self, concept_label: str, lang_code: str, trace: Optional[List[str]]) -> bool:
        """
        Queries Wikidata as a backup to resolve concept taxonomy.
        """
        start_time = time.time()
        try:
            # 1. Search for the term
            search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(concept_label)}&language={lang_code}&format=json"
            req = urllib.request.Request(search_url, headers={"User-Agent": "LEGEND-Cognitive-System/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            results = data.get("search", [])
            if not results:
                msg = f"[KNOWLEDGE IMPORT] Wikidata: No search results found for '{concept_label}'."
                print(msg)
                if trace is not None:
                    trace.append(msg)
                return False

            best_match = results[0]
            entity_id = best_match["id"]
            desc = best_match.get("description", "")

            # 2. Get claims for taxonomy properties
            entity_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&languages={lang_code}|en&format=json"
            req = urllib.request.Request(entity_url, headers={"User-Agent": "LEGEND-Cognitive-System/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                entity_data = json.loads(resp.read().decode("utf-8"))
            
            entity = entity_data.get("entities", {}).get(entity_id, {})
            claims = entity.get("claims", {})

            # Collect target IDs for P31 (instance of), P171 (parent taxon), P279 (subclass of)
            target_ids = []
            for prop in ["P31", "P171", "P279"]:
                for claim in claims.get(prop, []):
                    val = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                    if isinstance(val, dict) and "id" in val:
                        target_ids.append(val["id"])

            imported_count = 0
            if hasattr(self.gh.graph, "_loading"):
                self.gh.graph._loading = False

            # Add node
            concept_id = concept_label.strip()
            if not self.gh.graph.has_node(concept_id):
                self.gh.graph.add_node(concept_id, labels=[concept_label], category="concept", type="concept", confidence=1.0)

            # 3. Retrieve labels for target IDs in batch
            if target_ids:
                ids_str = "|".join(target_ids[:10]) # Limit to top 10 targets
                batch_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={ids_str}&props=labels&languages={lang_code}|en&format=json"
                req = urllib.request.Request(batch_url, headers={"User-Agent": "LEGEND-Cognitive-System/1.0"})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    batch_data = json.loads(resp.read().decode("utf-8"))
                
                for tid in target_ids:
                    t_entity = batch_data.get("entities", {}).get(tid, {})
                    labels = t_entity.get("labels", {})
                    label_val = labels.get(lang_code, labels.get("en", {})).get("value", "")
                    if label_val:
                        # Add target node
                        if not self.gh.graph.has_node(label_val):
                            self.gh.graph.add_node(label_val, labels=[label_val], category="concept", type="concept", confidence=1.0)
                        
                        # Add relationship
                        self.gh.graph.add_edge(
                            concept_id,
                            label_val,
                            relation="is_a",
                            type="fact",
                            world="reality",
                            confidence=1.0,
                            reason=f"Imported from Wikidata Entity {entity_id} ({prop} link)",
                            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            source="external_importer",
                            status="active"
                        )
                        imported_count += 1

            # 4. Fallback rule-based parsing of the description to inject direct categorizations
            desc_lower = desc.lower()
            direct_categories = []
            
            # Check both Arabic and English keywords in description
            is_bird = any(x in desc_lower for x in ["طائر", "طيور", "عصفور", "bird", "avian", "fowl"])
            is_animal = any(x in desc_lower for x in ["حيوان", "ثديي", "زواحف", "فقاريات", "animal", "mammal", "reptile", "vertebrate", "feline", "canine"])

            if is_bird:
                bird_label = "طائر" if lang_code == "ar" else "oiseau" if lang_code == "fr" else "bird"
                direct_categories.append(bird_label)
            if is_animal:
                animal_label = "حيوان" if lang_code == "ar" else "animal"
                direct_categories.append(animal_label)

            for cat in direct_categories:
                if not self.gh.graph.has_node(cat):
                    self.gh.graph.add_node(cat, labels=[cat], category="concept", type="concept", confidence=1.0)
                
                self.gh.graph.add_edge(
                    concept_id,
                    cat,
                    relation="is_a",
                    type="fact",
                    world="reality",
                    confidence=0.9,
                    reason=f"Extracted from Wikidata description of {entity_id}",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    source="external_importer",
                    status="active"
                )
                imported_count += 1

            duration = time.time() - start_time
            msg_success = f"[KNOWLEDGE IMPORT] Success: Wikidata resolved '{concept_label}' to {entity_id}. Imported {imported_count} taxonomic links in {duration:.2f}s."
            print(msg_success)
            logger.info(msg_success)
            if trace is not None:
                trace.append(msg_success)
            return True

        except Exception as e:
            err_msg = f"[KNOWLEDGE IMPORT] Offline Mode: Could not reach Wikidata ({type(e).__name__}). Proceeding with local graph."
            print(err_msg)
            logger.warning(err_msg)
            if trace is not None:
                trace.append(err_msg)
            return False
