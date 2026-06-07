import re
from typing import Dict, Any

class WorldManager:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def _is_stopword_or_particle(self, word: str, language: str) -> bool:
        if not word:
            return True
        w_norm = self.handler.normalize_text(word, language).lower() if language in ["en", "fr"] else self.handler.canonicalize_concept(word, language)
        
        # Check language rules particles
        if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
            # Check particles
            particles = self.handler.language_rules.get("morphology", {}).get("particles", [])
            for p in particles:
                form = p.get("form", "").replace("ـ", "").strip()
                if form and (word == form or w_norm == form):
                    return True
            # Check question particles
            qp = self.handler.language_rules.get(language, {}).get("question_particles", [])
            if not qp:
                qp = self.handler.language_rules.get("grammar", {}).get("question_particles", [])
            if word in qp or w_norm in qp:
                return True
                
        # General stop words for ar, en, fr
        ar_stop = {"في", "من", "إلى", "على", "عن", "مع", "بـ", "لـ", "كـ", "ال", "و", "أو", "ثم", "هو", "هي", "هم", "هن", "أنت", "أنا", "نحن", "يكون", "كان", "كانت", "صار", "ليس", "ليست", "تم", "هذا", "هذه", "ذلك", "تلك", "يكون"}
        en_stop = {"in", "on", "at", "to", "from", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "this", "that", "these", "those", "it", "its", "he", "she", "they", "we", "i", "you"}
        fr_stop = {"dans", "sur", "à", "de", "pour", "en", "par", "avec", "sans", "sous", "entre", "derrière", "devant", "avant", "après", "le", "la", "les", "un", "une", "des", "et", "ou", "mais", "est", "sont", "était", "étaient", "être", "avoir", "ce", "cette", "ces", "il", "elle", "ils", "elles", "je", "tu", "nous", "vous"}
        
        if language == "ar" and (word in ar_stop or w_norm in ar_stop):
            return True
        if language == "en" and (word in en_stop or w_norm in en_stop):
            return True
        if language == "fr" and (word in fr_stop or w_norm in fr_stop):
            return True
            
        return False

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
        # 2. Identify mapped concepts, skipping the relation word and sharing roots
        # 2a. Find matches of existing concepts (including multi-word ones)
        matches = []
        text_canon = self.handler.canonicalize_concept(cleaned_text, language).lower() if language in ["en", "fr"] else self.handler.canonicalize_concept(cleaned_text, language)
        
        for node, ndata in self.handler.graph.nodes(data=True):
            if ndata.get("type") != "concept":
                continue
            labels = ndata.get("labels", [])
            labels_to_check = list(labels) + [node]
            for label in labels_to_check:
                lbl_canon = self.handler.canonicalize_concept(label, language).lower() if language in ["en", "fr"] else self.handler.canonicalize_concept(label, language)
                if not lbl_canon:
                    continue
                idx = text_canon.find(lbl_canon)
                while idx != -1:
                    has_left_boundary = (idx == 0 or not text_canon[idx-1].isalnum())
                    has_right_boundary = (idx + len(lbl_canon) == len(text_canon) or not text_canon[idx + len(lbl_canon)].isalnum())
                    if has_left_boundary and has_right_boundary:
                        matches.append((idx, idx + len(lbl_canon), node, len(lbl_canon)))
                    idx = text_canon.find(lbl_canon, idx + 1)

        # Lexicon check
        lexicon = self.handler.language_rules.get(language, {}).get("lexicon", {})
        for lex_term, concept_id in lexicon.items():
            lex_canon = self.handler.canonicalize_concept(lex_term, language).lower() if language in ["en", "fr"] else self.handler.canonicalize_concept(lex_term, language)
            if not lex_canon:
                continue
            idx = text_canon.find(lex_canon)
            while idx != -1:
                has_left_boundary = (idx == 0 or not text_canon[idx-1].isalnum())
                has_right_boundary = (idx + len(lex_canon) == len(text_canon) or not text_canon[idx + len(lex_canon)].isalnum())
                if has_left_boundary and has_right_boundary:
                    matches.append((idx, idx + len(lex_canon), concept_id, len(lex_canon)))
                idx = text_canon.find(lex_canon, idx + 1)

        # Remove overlapping matches greedily
        matches.sort(key=lambda x: x[3], reverse=True)
        selected_matches = []
        matched_ranges = []
        for start, end, cid, length in matches:
            overlaps = False
            for s_r, e_r in matched_ranges:
                if not (end <= s_r or start >= e_r):
                    overlaps = True
                    break
            if not overlaps:
                selected_matches.append((start, end, cid))
                matched_ranges.append((start, end))

        # Check remaining words that are not covered
        current_pos = 0
        remaining_concepts = []
        for word in words:
            word_canon = self.handler.canonicalize_concept(word, language).lower() if language in ["en", "fr"] else self.handler.canonicalize_concept(word, language)
            w_start = text_canon.find(word_canon, current_pos)
            if w_start == -1:
                continue
            w_end = w_start + len(word_canon)
            current_pos = w_end
            
            if word == relation_word:
                continue
            if self._is_stopword_or_particle(word, language):
                continue
            shares_relation_root = False
            if relation_word and self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
                for root in self.handler.language_rules.get("morphology", {}).get("roots", []):
                    if word in root["patterns"] and relation_word in root["patterns"]:
                        shares_relation_root = True
                        break
            if shares_relation_root:
                continue
                
            is_covered = False
            for start, end, cid in selected_matches:
                if not (w_end <= start or w_start >= end):
                    is_covered = True
                    break
            
            if not is_covered:
                concept = self.handler.dynamic_morphological_lookup(word, language=language)
                if not concept:
                    concept = self.handler.canonicalize_concept(word, language=language)
                if concept:
                    remaining_concepts.append((w_start, w_end, concept))

        all_extracted = selected_matches + remaining_concepts
        all_extracted.sort(key=lambda x: x[0])
        mapped_concepts = []
        for start, end, cid in all_extracted:
            if cid not in mapped_concepts:
                mapped_concepts.append(cid)
                
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
