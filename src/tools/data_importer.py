import urllib.request
import json
import urllib.parse
import time
import socket
import os
import sqlite3
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
        success_cn = self._fetch_from_conceptnet(concept_label, lang_code, trace)
        
        # Supplement with Wikidata to ensure robust taxonomy
        success_wd = self._fetch_from_wikidata(concept_label, lang_code, trace)
        
        success = success_cn or success_wd

        if success:
            # Post-import: linguistically cross-link compound concepts
            self._cross_link_compound_concepts()
            return True
        return False

    def _cross_link_compound_concepts(self):
        """
        Linguistic rule: links compound concepts to their base concepts
        e.g., 'طائر جارح' -> is_a -> 'طائر' if 'طائر' exists in the graph.
        Handles Arabic (first word head, plural normalization) and English (last word head).
        """
        import itertools

        def strip_arabic_prefix(w):
            for pref in ["ال", "وبال", "بال", "وال", "لل", "ب", "و", "ل", "ف"]:
                if w.startswith(pref) and len(w) > len(pref):
                    return w[len(pref):]
            return w

        def get_word_variants(w, lang):
            variants = {w, w.lower()}
            if lang == "ar":
                w_clean = strip_arabic_prefix(w)
                variants.add(w_clean)
                if w_clean.endswith("ات") and len(w_clean) > 3:
                    sing = w_clean[:-2]
                    variants.add(sing)
                    variants.add(sing + "ة")
                    variants.add(sing + "ه")
                elif (w_clean.endswith("ون") or w_clean.endswith("ين")) and len(w_clean) > 3:
                    variants.add(w_clean[:-2])
                
                if (w_clean.endswith("ة") or w_clean.endswith("ه")) and len(w_clean) >= 3:
                    variants.add(w_clean[:-1])
            else:
                w_lower = w.lower()
                variants.add(w_lower)
                if w_lower.endswith("s") and len(w_lower) > 3:
                    variants.add(w_lower[:-1])
                if w_lower.endswith("es") and len(w_lower) > 4:
                    variants.add(w_lower[:-2])
            
            # Normalize each variant
            normalized_variants = set()
            for var in variants:
                normalized_variants.add(var)
                if hasattr(self.gh, "normalize_text"):
                    normalized_variants.add(self.gh.normalize_text(var, lang))
            return list(normalized_variants)

        def get_phrase_variants(phrase, lang):
            words = phrase.split()
            if not words:
                return []
            words_variants = [get_word_variants(w, lang) for w in words]
            phrases = []
            for combo in itertools.product(*words_variants):
                phrases.append(" ".join(combo))
            return list(set(phrases))

        for node in list(self.gh.graph.nodes):
            words = node.split()
            if len(words) > 1:
                # 1. Arabic: First word, or first two words (for compound heads)
                # English: Last word, or last two words
                head_candidates_ar = []
                head_candidates_en = []
                
                # Arabic candidates:
                head_candidates_ar.append(words[0])
                if len(words) >= 2:
                    head_candidates_ar.append(" ".join(words[0:2]))
                    
                # English candidates:
                head_candidates_en.append(words[-1])
                if len(words) >= 2:
                    head_candidates_en.append(" ".join(words[-2:]))

                # For each candidate, generate all variants (plural/singular/normalized)
                matched_nodes = set()
                
                # Check Arabic candidates
                for cand in head_candidates_ar:
                    variants = get_phrase_variants(cand, "ar")
                    for var in variants:
                        for n in self.gh.graph.nodes:
                            norm_var = self.gh.normalize_text(var, "ar") if hasattr(self.gh, "normalize_text") else var.strip()
                            norm_n = self.gh.normalize_text(n, "ar") if hasattr(self.gh, "normalize_text") else n.strip()
                            
                            ndata = self.gh.graph.nodes[n]
                            n_labels = ndata.get("labels", [])
                            norm_labels = [self.gh.normalize_text(lbl, "ar") if hasattr(self.gh, "normalize_text") else lbl.strip() for lbl in n_labels]
                            
                            if norm_var == norm_n or norm_var in norm_labels:
                                matched_nodes.add(n)

                # Check English candidates
                for cand in head_candidates_en:
                    variants = get_phrase_variants(cand, "en")
                    for var in variants:
                        for n in self.gh.graph.nodes:
                            norm_var = var.lower().strip()
                            norm_n = n.lower().strip()
                            
                            ndata = self.gh.graph.nodes[n]
                            norm_labels = [lbl.lower().strip() for lbl in ndata.get("labels", [])]
                            
                            if norm_var == norm_n or norm_var in norm_labels:
                                matched_nodes.add(n)

                # Link to all matched nodes (except itself)
                for matched_node in matched_nodes:
                    if matched_node != node:
                        # Add is_a link from compound to base concept if not already exists
                        if not self.gh.graph.has_edge(node, matched_node):
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
        db_path = "data/conceptnet_offline.db"
        if os.path.exists(db_path):
            return self._fetch_from_conceptnet_offline(concept_label, lang_code, db_path, trace)
        else:
            return self._fetch_from_conceptnet_online(concept_label, lang_code, trace)

    def _normalize_label_match(self, label: str, target: str, lang: str) -> str:
        if lang == "ar":
            l_clean = label.strip()
            t_clean = target.strip()
            if l_clean.startswith("ال") and len(l_clean) > 2:
                l_clean = l_clean[2:]
            if t_clean.startswith("ال") and len(t_clean) > 2:
                t_clean = t_clean[2:]
            if l_clean == t_clean:
                return target
        else:
            if label.strip().lower() == target.strip().lower():
                return target
        return label

    def _fetch_from_conceptnet_offline(self, concept_label: str, lang_code: str, db_path: str, trace: Optional[List[str]]) -> bool:
        search_label = concept_label.strip()
        if lang_code == "ar":
            if search_label.startswith("ال") and len(search_label) > 2:
                search_label = search_label[2:]
        clean_label = search_label.replace(" ", "_").lower()
        
        msg = f"[KNOWLEDGE IMPORT] Querying offline ConceptNet database for '{concept_label}' ({lang_code})..."
        print(msg)
        logger.info(msg)
        if trace is not None:
            trace.append(msg)
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            concept_uri = f"/c/{lang_code}/{clean_label}"
            slash_start = concept_uri + "/"
            slash_end = concept_uri + "0"
            
            cursor.execute("""
                SELECT relation, start, end, weight
                FROM assertions
                WHERE start = ? OR (start >= ? AND start < ?)
                   OR end = ? OR (end >= ? AND end < ?)
            """, (concept_uri, slash_start, slash_end, concept_uri, slash_start, slash_end))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                msg_empty = f"[KNOWLEDGE IMPORT] Offline ConceptNet: No relations found for '{concept_label}'."
                print(msg_empty)
                if trace is not None:
                    trace.append(msg_empty)
                return False
                
            imported_count = 0
            if hasattr(self.gh.graph, "_loading"):
                self.gh.graph._loading = False
 
            concept_id = concept_label.strip()
            if not self.gh.graph.has_node(concept_id):
                self.gh.graph.add_node(concept_id, labels=[concept_label], category="concept", type="concept", confidence=1.0)
                
            for relation, start, end, weight in rows:
                if weight < 1.0:
                    continue
                    
                relation_name = relation.split("/")[-1].lower() if "/" in relation else relation
                
                # Parse start and end URIs
                def parse_concept_uri(uri: str):
                    parts = uri.split('/')
                    if len(parts) >= 4 and parts[1] == 'c':
                        lang = parts[2]
                        label = parts[3].replace('_', ' ')
                        return lang, label
                    return None, None
                    
                start_lang, start_label = parse_concept_uri(start)
                end_lang, end_label = parse_concept_uri(end)
                
                if start_lang != lang_code or end_lang != lang_code:
                    continue
                    
                if not start_label or not end_label:
                    continue

                start_label = self._normalize_label_match(start_label, concept_id, lang_code)
                end_label = self._normalize_label_match(end_label, concept_id, lang_code)
                    
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
                    reason="Imported from local offline ConceptNet database",
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    source="external_importer",
                    status="active"
                )
                imported_count += 1
                
            if imported_count == 0:
                msg_fail = f"[KNOWLEDGE IMPORT] Offline ConceptNet: 0 relations matching language '{lang_code}' were imported."
                print(msg_fail)
                if trace is not None:
                    trace.append(msg_fail)
                return False

            msg_success = f"[KNOWLEDGE IMPORT] Success: Imported {imported_count} relations from offline ConceptNet."
            print(msg_success)
            logger.info(msg_success)
            if trace is not None:
                trace.append(msg_success)
            return True
            
        except Exception as e:
            err_msg = f"[KNOWLEDGE IMPORT] Offline ConceptNet Error: {e}"
            print(err_msg)
            logger.warning(err_msg)
            if trace is not None:
                trace.append(err_msg)
            return False

    def _fetch_from_conceptnet_online(self, concept_label: str, lang_code: str, trace: Optional[List[str]]) -> bool:
        search_label = concept_label.strip()
        if lang_code == "ar":
            if search_label.startswith("ال") and len(search_label) > 2:
                search_label = search_label[2:]
        clean_label = search_label.replace(" ", "_")
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
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with self._url_open_with_retry(req, timeout=3.0) as response:
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

                start_label = self._normalize_label_match(start_label, concept_id, lang_code)
                end_label = self._normalize_label_match(end_label, concept_id, lang_code)

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

            if imported_count == 0:
                return False

            msg_success = f"[KNOWLEDGE IMPORT] Success: Imported {imported_count} relations from ConceptNet."
            print(msg_success)
            logger.info(msg_success)
            if trace is not None:
                trace.append(msg_success)
            return True

        except Exception as e:
            return False

    def _url_open_with_retry(self, req, timeout=3.0, max_retries=3):
        import urllib.error
        backoff = 0.5
        url_str = req.full_url if hasattr(req, "full_url") else str(req)
        if "wikidata.org" in url_str:
            last_time = getattr(self.gh, "_last_wikidata_req_time", 0.0)
            elapsed = time.time() - last_time
            if elapsed < 1.5:
                time.sleep(1.5 - elapsed)
            self.gh._last_wikidata_req_time = time.time()

        for attempt in range(max_retries):
            try:
                return urllib.request.urlopen(req, timeout=timeout)
            except urllib.error.HTTPError as e:
                if e.code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                    if "wikidata.org" in url_str:
                        self.gh._last_wikidata_req_time = time.time()
                    continue
                raise e
            except Exception as e:
                raise e

    def _fetch_from_wikidata(self, concept_label: str, lang_code: str, trace: Optional[List[str]]) -> bool:
        """
        Queries Wikidata as a backup to resolve concept taxonomy.
        """
        start_time = time.time()
        try:
            search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(concept_label)}&language={lang_code}&format=json"
            req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
            with self._url_open_with_retry(req, timeout=3.0) as resp:
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

            entity_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&languages={lang_code}|en&format=json"
            req = urllib.request.Request(entity_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
            with self._url_open_with_retry(req, timeout=3.0) as resp:
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
                req = urllib.request.Request(batch_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
                with self._url_open_with_retry(req, timeout=3.0) as resp:
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
            err_msg = f"[KNOWLEDGE IMPORT] Offline Mode: Could not reach Wikidata ({type(e).__name__}): {e}. Proceeding with local graph."
            print(err_msg)
            logger.warning(err_msg)
            if trace is not None:
                trace.append(err_msg)
            return False
