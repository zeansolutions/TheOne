class WorldManager:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def detect_and_set_world(self, query):
        """
        Detects if query specifies a world (e.g. "في عالم خيالي" or "في عالم الواقع")
        and sets the active world accordingly. Returns the cleaned query and the detected world.
        """
        world = self.handler.active_world
        cleaned_query = query
        query_lower = query.lower()
        
        # 1. Arabic world switching triggers
        if "في عالم خيالي" in query:
            world = "خيالي"
            cleaned_query = query.replace("في عالم خيالي", "").strip()
        elif "عالم خيالي" in query:
            world = "خيالي"
            cleaned_query = query.replace("عالم خيالي", "").strip()
        elif "في عالم الواقع" in query:
            world = "reality"
            cleaned_query = query.replace("في عالم الواقع", "").strip()
        elif "في عالم القطب" in query:
            world = "arctic_scenario"
            cleaned_query = query.replace("في عالم القطب", "").strip()
            
        # 2. English world switching triggers
        elif "in fantasy world" in query_lower:
            world = "خيالي"
            cleaned_query = re_replace_ignore_case("in fantasy world", "", query)
        elif "fantasy world" in query_lower:
            world = "خيالي"
            cleaned_query = re_replace_ignore_case("fantasy world", "", query)
        elif "in real world" in query_lower:
            world = "reality"
            cleaned_query = re_replace_ignore_case("in real world", "", query)
        elif "in real life" in query_lower:
            world = "reality"
            cleaned_query = re_replace_ignore_case("in real life", "", query)
        elif "in arctic world" in query_lower:
            world = "arctic_scenario"
            cleaned_query = re_replace_ignore_case("in arctic world", "", query)
        elif "in polar scenario" in query_lower:
            world = "arctic_scenario"
            cleaned_query = re_replace_ignore_case("in polar scenario", "", query)
            
        # 3. French world switching triggers
        elif "dans un monde imaginaire" in query_lower:
            world = "خيالي"
            cleaned_query = re_replace_ignore_case("dans un monde imaginaire", "", query)
        elif "monde imaginaire" in query_lower:
            world = "خيالي"
            cleaned_query = re_replace_ignore_case("monde imaginaire", "", query)
        elif "dans le monde réel" in query_lower:
            world = "reality"
            cleaned_query = re_replace_ignore_case("dans le monde réel", "", query)
        elif "dans le monde polaire" in query_lower:
            world = "arctic_scenario"
            cleaned_query = re_replace_ignore_case("dans le monde polaire", "", query)
        elif "dans le monde arctique" in query_lower:
            world = "arctic_scenario"
            cleaned_query = re_replace_ignore_case("dans le monde arctique", "", query)
            
        # Clean leading conjunctions/punctuation
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
        raw_words = text.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
        if language in ["en", "fr"]:
            words = [w.lower() for w in words]
            
        # Identify mapped concepts
        mapped_concepts = []
        for word in words:
            concept = self.handler.dynamic_morphological_lookup(word, language=language)
            if concept and concept not in mapped_concepts:
                mapped_concepts.append(concept)
                
        # If we have 2 mapped concepts, we need to find the relation verb/root
        if len(mapped_concepts) >= 2:
            # We want to identify the relationship.
            # Look for roots/particles that match known relations.
            # Default to lives_in if "يعيش" or "عاش" is present.
            # Default to rises_from if "تشرق" or "شرق" is present.
            relation = "has_property" # default fallback
            
            if language in ["en", "fr"]:
                lang_rules = self.handler.language_rules.get(language, {})
                relations_dict = lang_rules.get("relations", {})
                for word in words:
                    if word in relations_dict:
                        relation = relations_dict[word]
                        break
            else:
                # Simple root/verb checks
                for root in self.handler.language_rules.get("morphology", {}).get("roots", []):
                    for word in words:
                        if word in root["patterns"]:
                            # Map known roots to relations
                            if root["id"] == "عوش":
                                relation = "lives_in"
                            elif root["id"] == "شروق":
                                relation = "rises_from"
                            elif root["id"] == "حتاج":
                                relation = "requires"
                            elif root["id"] == "حمي":
                                relation = "provides"
            
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
                interactive=interactive
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
    import re
    compiled = re.compile(re.escape(pattern), re.IGNORECASE)
    return compiled.sub(replacement, text)
