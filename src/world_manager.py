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
        
        # Arabic world switching triggers
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
            
        # Clean leading conjunctions/punctuation
        cleaned_query = cleaned_query.lstrip("،").lstrip(",").lstrip(".").strip()
        if cleaned_query.startswith("و "):
            cleaned_query = cleaned_query[2:].strip()
            
        self.handler.set_active_world(world)
        return cleaned_query, world

    def parse_and_add_fact(self, text, world):
        """
        Dynamically extracts a fact from clean statement text and saves it in the Graph.
        Expected format: [Subject] [Relation Verb] [Object] (e.g. "الأسد يعيش في القطب" or "الشمس تشرق من تحت الأرض")
        """
        raw_words = text.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
        
        # Identify mapped concepts
        mapped_concepts = []
        for word in words:
            concept = self.handler.dynamic_morphological_lookup(word)
            if concept and concept not in mapped_concepts:
                mapped_concepts.append(concept)
                
        # If we have 2 mapped concepts, we need to find the relation verb/root
        if len(mapped_concepts) >= 2:
            # We want to identify the relationship.
            # Look for roots/particles that match known relations.
            # Default to lives_in if "يعيش" or "عاش" is present.
            # Default to rises_from if "تشرق" or "شرق" is present.
            relation = "has_property" # default fallback
            
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
            
            # Add edge to the NetworkX graph under the active world
            self.handler.graph.add_edge(
                subj,
                obj,
                relation=relation,
                world=world,
                confidence=1.0,
                type="fact"
            )
            
            # Print for debugging
            subj_lbl = self.handler.graph.nodes[subj].get("labels", [subj])[0]
            obj_lbl = self.handler.graph.nodes[obj].get("labels", [obj])[0]
            return {
                "success": True,
                "subject": subj,
                "relation": relation,
                "object": obj,
                "msg": f"تم حفظ الحقيقة الجديدة: [{subj_lbl}] --({relation})--> [{obj_lbl}] في عالم '{world}'"
            }
            
        return {"success": False, "msg": "لم نتمكن من استخراج مفاهيم وعلاقات كافية من الجملة الخبرية."}
