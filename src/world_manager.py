import re
from typing import Dict, Any

class WorldManager:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def detect_and_set_world(self, query: str):
        """
        Detects if query specifies a world (e.g. "في عالم خيالي" or "في عالم الواقع")
        and sets the active world accordingly. Returns the cleaned query and the detected world.
        """
        world = self.handler.active_world
        cleaned_query = query
        query_lower = query.lower()
        
        # Check if query is conditional/hypothetical to avoid stripping the environment triggers
        words = query_lower.split()
        is_conditional = any(p in words[:2] for p in ["لو", "إذا", "اذا", "if", "si"])
        
        world_rules = {}
        if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
            world_rules = self.handler.language_rules.get("world_rules", {})
            
        world_triggers = world_rules.get("world_triggers", [])
        
        # 1. Check world triggers dynamically
        for trigger in world_triggers:
            target_world = trigger.get("world")
            patterns = trigger.get("patterns", [])
            for pattern in patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in cleaned_query.lower():
                    world = target_world
                    if not is_conditional:
                        cleaned_query = re_replace_ignore_case(pattern, "", cleaned_query).strip()
                    
        # Clean leading conjunctions/punctuation dynamically or using fallbacks
        conjunctions_to_strip = world_rules.get("conjunctions_to_strip", {})
        for lang, conj_list in conjunctions_to_strip.items():
            for conj in conj_list:
                if cleaned_query.lower().startswith(conj):
                    cleaned_query = cleaned_query[len(conj):].strip()
                    
        cleaned_query = cleaned_query.lstrip("،").lstrip(",").lstrip(".").strip()
        if cleaned_query.startswith("و "):
            cleaned_query = cleaned_query[2:].strip()
        elif cleaned_query.lower().startswith("and "):
            cleaned_query = cleaned_query[4:].strip()
        elif cleaned_query.lower().startswith("et "):
            cleaned_query = cleaned_query[3:].strip()
            
        self.handler.set_active_world(world)
        return cleaned_query, world

    def parse_and_add_fact(self, text, world, interactive=False, language="ar"):
        """
        Dynamically extracts a fact from clean statement text and saves it in the Graph.
        Expected format: [Subject] [Relation Verb] [Object] (e.g. "الأسد يعيش في القطب" or "الشمس تشرق من تحت الأرض")
        """
        from src.enrichment.fuzzy_modal import FuzzyModalEngine
        modal_engine = FuzzyModalEngine()
        modality, cleaned_text = modal_engine.detect_modality(text, language)

        raw_words = cleaned_text.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
        if language in ["en", "fr"]:
            words = [w.lower() for w in words]
            
        # 1. Identify relation and the matching word/verb first
        relation = "has_property"
        relation_word = None
        
        relation_mappings = {}
        if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
            relation_mappings = self.handler.language_rules.get("relation_mappings", {})
            
        # Check direct mapping
        for word in words:
            if word in relation_mappings:
                relation = relation_mappings[word]
                relation_word = word
                break
                
        # Check morphology roots
        if not relation_word and self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
            for root in self.handler.language_rules.get("morphology", {}).get("roots", []):
                for word in words:
                    if word in root["patterns"]:
                        root_id = root["id"]
                        if root_id in relation_mappings:
                            relation = relation_mappings[root_id]
                            relation_word = word
                            break
                if relation_word:
                    break

        # 2. Identify mapped concepts, skipping the relation word and sharing roots
        mapped_concepts = []
        for word in words:
            if word == relation_word:
                continue
            shares_relation_root = False
            if relation_word and self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
                for root in self.handler.language_rules.get("morphology", {}).get("roots", []):
                    if word in root["patterns"] and relation_word in root["patterns"]:
                        shares_relation_root = True
                        break
            if shares_relation_root:
                continue
                
            concept = self.handler.dynamic_morphological_lookup(word, language=language)
            if concept and concept not in mapped_concepts:
                mapped_concepts.append(concept)
                
        if len(mapped_concepts) >= 2:
            # Deduce direction (subject usually comes first in statement)
            subj = mapped_concepts[0]
            obj = mapped_concepts[1]
            
            # Use add_or_update_fact to handle duplicates and contradictions
            update_res = self.handler.add_or_update_fact(
                subj,
                obj,
                relation=relation,
                world=world,
                confidence=1.0,
                interactive=interactive,
                modality=modality
            )
            
            return {
                "success": update_res["success"],
                "subject": subj,
                "relation": relation,
                "object": obj,
                "msg": update_res["message"],
                "status": update_res.get("status")
            }
            
        return {"success": False, "msg": "لم نتمكن من استخراج مفاهيم وعلاقات كافية من الجملة الخبرية."}

def re_replace_ignore_case(pattern, replacement, text):
    """Helper to perform case-insensitive regex replacement."""
    compiled = re.compile(re.escape(pattern), re.IGNORECASE)
    return compiled.sub(replacement, text)
