import json
import os
import re
from typing import List, Dict, Optional, Any

class InteractiveBootstrapper:
    def __init__(self, graph_handler, language_rules_path: str):
        self.handler = graph_handler
        self.rules_path = language_rules_path

    def scan_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Scans the text for known concept labels in the graph, resolving overlaps by longest match."""
        if not self.handler or not self.handler.graph:
            return []

        # Gather all concepts and their labels
        concept_matches = []
        for node, data in self.handler.graph.nodes(data=True):
            if data.get("type") == "concept":
                labels = data.get("labels", [])
                for lbl in labels:
                    # Case insensitive and robust string search
                    # We can use regex to find word boundaries or simple substring search
                    # Let's find all occurrences of the label in the text
                    # We use re.finditer but escape the label
                    try:
                        pattern = r'\b' + re.escape(lbl) + r'\b'
                        # For Arabic, word boundaries are sometimes tricky, so let's check both with and without word boundary
                        # or simple string index matching
                        start = 0
                        while True:
                            idx = text.lower().find(lbl.lower(), start)
                            if idx == -1:
                                break
                            concept_matches.append({
                                "concept_id": node,
                                "label": lbl,
                                "start": idx,
                                "end": idx + len(lbl)
                            })
                            start = idx + 1
                    except Exception:
                        pass
        
        # Resolve overlaps: sort by length descending, and keep non-overlapping
        concept_matches.sort(key=lambda x: (x["end"] - x["start"]), reverse=True)
        
        resolved = []
        for match in concept_matches:
            # Check if this match overlaps with any already resolved match
            overlap = False
            for res in resolved:
                if not (match["end"] <= res["start"] or match["start"] >= res["end"]):
                    overlap = True
                    break
            if not overlap:
                resolved.append(match)
                
        # Sort by start index
        resolved.sort(key=lambda x: x["start"])
        return resolved

    def propose_pattern(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyzes text, identifies concepts and unknown words, and proposes a new pattern structure."""
        concepts = self.scan_concepts(text)
        if len(concepts) < 2:
            return None
            
        # We take the first two detected concepts to form a relation pattern
        c1_data = concepts[0]
        c2_data = concepts[1]
        
        c1_id = c1_data["concept_id"]
        c2_id = c2_data["concept_id"]
        c1_lbl = c1_data["label"]
        c2_lbl = c2_data["label"]
        
        # Tokenize text
        words = text.strip().split()
        # Clean punctuation
        words_clean = [w.replace("؟", "").replace("?", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "") for w in words]
        words_clean = [w for w in words_clean if w]
        
        # Construct pattern tokens
        pattern_tokens = []
        mapping = {}
        var_count = 1
        
        # Replace the substring matches with variables in the pattern tokens
        i = 0
        while i < len(words_clean):
            word = words_clean[i]
            # Check if this word is part of concept 1
            if c1_lbl in word or word in c1_lbl:
                pattern_tokens.append("?X")
                mapping["concept1"] = "?X"
                i += len(c1_lbl.split())
            elif c2_lbl in word or word in c2_lbl:
                pattern_tokens.append("?Y")
                mapping["concept2"] = "?Y"
                i += len(c2_lbl.split())
            else:
                pattern_tokens.append(word)
                i += 1
                
        # Ensure we have ?X and ?Y in the pattern
        if "?X" not in pattern_tokens or "?Y" not in pattern_tokens:
            # Alternative: simpler construction
            # just ["?X", "unknown_word", "?Y"]
            # Find the word between concepts
            # Text between concepts
            start_between = c1_data["end"]
            end_between = c2_data["start"]
            between_text = text[start_between:end_between].strip()
            # Clean punctuation
            for p in ["؟", "?", "!", "،", ",", "."]:
                between_text = between_text.replace(p, "")
            between_words = [w for w in between_text.split() if w]
            if not between_words:
                between_words = ["هو"]  # fallback default relation word
                
            pattern_tokens = ["?X"] + between_words + ["?Y"]
            mapping = {"concept1": "?X", "concept2": "?Y"}

        # Infer intent
        # Check if there is an existing relation in the graph
        inferred_intent = "classification"
        inferred_relation = "is_a"
        
        if self.handler and self.handler.graph:
            if self.handler.graph.has_edge(c1_id, c2_id):
                edge_data = self.handler.graph[c1_id][c2_id]
                rel = edge_data.get("relation", "is_a")
                if rel == "lives_in":
                    inferred_intent = "location"
                    inferred_relation = "lives_in"
                    mapping = {"concept": "?X", "relation": "?ACTION"}
                    # Replace intermediate words with ?ACTION in pattern
                    # Find index of intermediate words
                    for idx, token in enumerate(pattern_tokens):
                        if token not in ["?X", "?Y"]:
                            pattern_tokens[idx] = "?ACTION"
                            mapping["relation"] = "?ACTION"
                elif rel == "is_a":
                    inferred_intent = "classification"
                    inferred_relation = "is_a"
                    mapping = {"concept1": "?X", "concept2": "?Y"}
            else:
                # Default fallback
                inferred_intent = "classification"
                mapping = {"concept1": "?X", "concept2": "?Y"}
                
        suggested_question = ""
        unknown_str = " ".join([t for t in pattern_tokens if not t.startswith("?")])
        
        if inferred_intent == "classification":
            suggested_question = f"أنا أفهم '{c1_lbl}' وأفهم '{c2_lbl}'، لكنني لا أعرف معنى '{unknown_str}'. هل تقصد أن {c1_lbl} هو تصنيف فرعي من {c2_lbl}؟"
        elif inferred_intent == "location":
            suggested_question = f"أنا أفهم '{c1_lbl}' وأفهم '{c2_lbl}'، لكنني لا أعرف معنى '{unknown_str}'. هل تقصد السؤال عن موطن أو موقع {c1_lbl}؟"
            
        pattern_id = f"learned_{inferred_intent}_{len(pattern_tokens)}_{abs(hash(tuple(pattern_tokens))) % 10000}"
        
        return {
            "id": pattern_id,
            "pattern": pattern_tokens,
            "intent": inferred_intent,
            "mapping": mapping,
            "confidence": 1.0,
            "suggested_question": suggested_question,
            "inferred_relation": inferred_relation,
            "concept1": c1_id,
            "concept2": c2_id,
            "concept1_lbl": c1_lbl,
            "concept2_lbl": c2_lbl
        }

    def save_new_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        """Appends the newly learned pattern to language_rules.json."""
        if not os.path.exists(self.rules_path):
            return False
            
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "semantic_frames" not in data:
                data["semantic_frames"] = []
                
            # Avoid duplicate pattern IDs
            for pat in data["semantic_frames"]:
                if pat.get("id") == pattern_data.get("id") or pat.get("pattern") == pattern_data.get("pattern"):
                    return True # already exists
                    
            # Clean structure to save
            clean_pat = {
                "id": pattern_data["id"],
                "pattern": pattern_data["pattern"],
                "intent": pattern_data["intent"],
                "mapping": pattern_data["mapping"],
                "confidence": pattern_data.get("confidence", 1.0)
            }
            if "conditions" in pattern_data:
                clean_pat["conditions"] = pattern_data["conditions"]
            if "is_deep" in pattern_data:
                clean_pat["is_deep"] = pattern_data["is_deep"]
                
            data["semantic_frames"].append(clean_pat)
            
            with open(self.rules_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # Reload graph handler's rules if reference exists
            if self.handler:
                self.handler.language_rules = data
            return True
        except Exception as e:
            print(f"Error saving pattern to {self.rules_path}: {e}")
            return False

    def ask_for_clarification(self, query: str, user_response: str = None, 
                              interactive: bool = False, input_func=input) -> Optional[Dict[str, Any]]:
        """Handles interactive pattern learning. Prompts user, gets approval, saves pattern."""
        proposal = self.propose_pattern(query)
        if not proposal:
            return None
            
        # If interactive is true, prompt via console
        if interactive:
            print(f"\n💡 {proposal['suggested_question']}")
            ans = input_func("هل هذا صحيح؟ (نعم/لا): ").strip()
            if ans in ["نعم", "yes", "y", "صح", "بالظبط", "بالضبط"]:
                success = self.save_new_pattern(proposal)
                if success:
                    print("✅ تم تعلم النمط الدلالي الجديد وحفظه بنجاح!")
                    return proposal
            else:
                print("❌ تم إلغاء عملية التعلم.")
        else:
            # Non-interactive mode (e.g., test cases with simulated user_response)
            if user_response in ["نعم", "yes", "y", "صح", "بالظبط", "بالضبط"]:
                success = self.save_new_pattern(proposal)
                if success:
                    return proposal
                    
        return None
