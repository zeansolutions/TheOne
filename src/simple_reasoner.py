import os
import json
from src.world_manager import WorldManager
from src.conflict_resolver import ConflictResolver
from src.conversation_manager import ConversationManager
from src.entity_resolver import EntityResolver
from src.manager.language_selection_engine import LanguageSelectionEngine

class SimpleReasoner:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        self.conversation_manager = ConversationManager()
        self.entity_resolver = EntityResolver(self.conversation_manager, self.handler)
        self.world_manager = WorldManager(self.handler)
        self.conflict_resolver = ConflictResolver(self.handler)
        
        # Load language engine
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        languages_path = os.path.join(project_dir, "config", "languages.json")
        if not os.path.exists(languages_path):
            languages_path = "config/languages.json"
        
        self.language_engine = None
        if os.path.exists(languages_path):
            self.language_engine = LanguageSelectionEngine(languages_path)

    def check_is_a_relationship(self, concept_id, target_category_id):
        """Checks if concept_id is a target_category_id directly or via transitive inheritance."""
        trace = []
        curr = concept_id
        path = [concept_id]
        
        while curr:
            parent = self.handler.get_parent(curr, "is_a")
            if parent:
                path.append(parent)
                trace.append(f"{curr} هو تصنيف فرعي من {parent} (علاقة is_a)")
                if parent == target_category_id:
                    return {
                        "result": True,
                        "path": path,
                        "trace": trace
                    }
            curr = parent
            
        return {
            "result": False,
            "path": path,
            "trace": trace
        }

    def inheritance_deduction(self, entity_id, property_id):
        """
        Deduces if an entity inherits a property from any of its taxonomic parent categories.
        """
        curr = entity_id
        trace = []
        
        # Check direct properties
        props = self.handler.get_properties(entity_id)
        for p in props:
            if p["property"] == property_id:
                trace.append(f"{entity_id} لديه الخاصية {property_id} بشكل مباشر")
                return {"result": True, "source": entity_id, "trace": trace}
                
        # Traverse up the hierarchy
        while curr:
            parent = self.handler.get_parent(curr, "is_a")
            if parent:
                trace.append(f"تتبع الوراثة تصاعدياً: {curr} يرث من {parent}")
                parent_props = self.handler.get_properties(parent)
                for p in parent_props:
                    if p["property"] == property_id:
                        trace.append(f"وجدنا أن {parent} لديه الخاصية {property_id}، وبالتالي يرثها {entity_id} بالتبعية")
                        return {"result": True, "source": parent, "trace": trace}
            curr = parent
            
        return {"result": False, "trace": trace}

    def causal_reasoning(self, entity_id, environment_id):
        """
        Causal/Teleological reasoning.
        Identifies requirements of the environment, matches them against the entity's current properties,
        and determines what adaptation is needed based on functional causal purposes.
        """
        trace = []
        trace.append(f"بدء الاستدلال السببي للـ {entity_id} في البيئة {environment_id}")
        
        # 1. Get environment conditions & requirements
        requirements = self.handler.get_requirements(environment_id)
        if not requirements:
            trace.append(f"البيئة {environment_id} لا تفرض أي متطلبات خاصة مسجلة في قاعدة المعرفة")
            return {"needs_adaptation": False, "trace": trace}
            
        # For simplicity, look at the insulation requirement (e.g. good_insulation)
        insulation_req = None
        for req in requirements:
            if req["requirement"] == "good_insulation":
                insulation_req = req
                trace.append(f"البيئة {environment_id} بها {req['condition']} مما يستدعي متطلب: {req['requirement']}")
                break
                
        if not insulation_req:
            return {"needs_adaptation": False, "trace": trace}
            
        # 2. Check current entity properties
        properties = self.handler.get_properties(entity_id)
        has_thick_fur = False
        has_thin_fur = False
        current_fur = None
        
        for p in properties:
            if p["property"] == "thick_fur":
                has_thick_fur = True
                current_fur = "thick_fur"
            elif p["property"] == "thin_fur":
                has_thin_fur = True
                current_fur = "thin_fur"
                
        trace.append(f"الفحص الصرفي/الفيزيائي للـ {entity_id}: يمتلك {current_fur or 'لا يوجد فرو مسجل'}")
        
        # Check function of current property
        provides_good_insulation = False
        if current_fur:
            # Check edge property -> provides -> insulation in the graph
            for _, to_node, data in self.handler.graph.out_edges(current_fur, data=True):
                if data.get("relation") == "provides" and to_node == "good_insulation":
                    provides_good_insulation = True
                    
        if provides_good_insulation:
            trace.append(f"الخاصية {current_fur} تلبي المتطلب {insulation_req['requirement']} بنجاح")
            return {"needs_adaptation": False, "trace": trace}
        else:
            trace.append(f"الخاصية الحالية للـ {entity_id} ({current_fur}) لا توفر العزل المطلوب ({insulation_req['requirement']})")
            trace.append(f"← النتيجة: {entity_id} بحاجة إلى عزل حراري ({insulation_req['requirement']}) في {environment_id}")
            return {
                "needs_adaptation": True,
                "requirement": insulation_req["requirement"],
                "current_property": current_fur,
                "trace": trace
            }

    def analogical_reasoning(self, target_entity_id, environment_id, requirement):
        """
        Analogical Transfer.
        Finds a similar entity (analogical candidate) that lives in environment_id and possesses
        a property solving the given requirement, and transfers that property to target_entity_id.
        """
        trace = []
        trace.append(f"بدء استدلال التناظر والقياس للـ {target_entity_id} في البيئة {environment_id}")
        
        # 1. Find entities living in this environment
        candidates = []
        for node, data in self.handler.graph.nodes(data=True):
            if data.get("type") == "concept" and node != target_entity_id:
                # Check if it lives in environment_id in reality or ontology
                properties = self.handler.get_properties(node, world="reality")
                for p in properties:
                    if p["relation"] == "lives_in" and p["property"] == environment_id:
                        candidates.append(node)
        candidates = list(set(candidates))
        trace.append(f"الكائنات البديلة التي تعيش في {environment_id}: {candidates}")
        
        # 2. Calculate similarity and find best match solving the requirement
        best_candidate = None
        best_similarity = 0.0
        solution_property = None
        
        for cand in candidates:
            sim = self.handler.calculate_similarity(target_entity_id, cand)
            trace.append(f"مقياس التشابه الجاكاردي (Ancestry Similarity) بين {target_entity_id} و {cand} هو {sim:.2f}")
            
            # Check properties of candidate to see if it solves requirement
            cand_props = self.handler.get_properties(cand, world="reality")
            for p in cand_props:
                prop = p["property"]
                # Does this property provide the requirement?
                for _, to_node, data in self.handler.graph.out_edges(prop, data=True):
                    if data.get("relation") == "provides" and to_node == requirement:
                        if sim > best_similarity:
                            best_similarity = sim
                            best_candidate = cand
                            solution_property = prop
                            
        if best_candidate and solution_property:
            trace.append(f"المرشح الأنسب للقياس هو: {best_candidate} (معدل تشابه: {best_similarity:.2f})")
            trace.append(f"نقوم بنقل الخاصية {solution_property} من {best_candidate} إلى {target_entity_id} لحل مشكلة البيئة")
            return {
                "success": True,
                "analogy_candidate": best_candidate,
                "transferred_property": solution_property,
                "similarity": best_similarity,
                "trace": trace
            }
            
        trace.append("لم نجد أي كائن مماثل يعيش في تلك البيئة ولديه الخاصية المطلوبة لقياسها")
        return {"success": False, "trace": trace}

    def process_query(self, query, interactive=False, language=None):
        """
        Pipeline: Parsing -> Dynamic Morphological Lookup -> Logical Reasoning.
        Supports 5 dynamic queries, multi-world state, dynamic fact teaching, and dialog context.
        Supports multilingual execution (ar, en, fr).
        """
        # Detect and set language if not provided
        if language is None:
            if self.language_engine:
                detected = self.language_engine.detect_language(query)
                language = self.language_engine.select_language(detected)
            else:
                language = "ar"

        # Detect and set active world
        query, world = self.world_manager.detect_and_set_world(query)
        
        # Split into sentences to support combined fact teaching + question
        # Split by both Arabic Question Mark '؟' and English/French Question Mark '?' and period '.'
        normalized_query = query.replace("؟", "؟.").replace("?", "?.")
        parts = [p.strip() for p in normalized_query.split(".") if p.strip()]
        
        last_result = None
        
        for idx, part in enumerate(parts):
            raw_words = part.strip().split()
            words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
            if language in ["en", "fr"]:
                words = [w.lower() for w in words]
            
            # Check if this part is a question
            lang_rules = self.handler.language_rules.get(language, {})
            question_particles = lang_rules.get("question_particles", [])
            if not question_particles:
                question_particles = self.handler.language_rules.get("grammar", {}).get("question_particles", [])
                
            is_question = any(q in words for q in question_particles) or \
                          part.endswith("؟") or part.endswith("?") or \
                          any(w in words for w in ["الفرق", "إزاي", "ازاي", "difference", "différence", "comment", "how"])
            
            if not is_question:
                # Teach fact to world manager
                teach_res = self.world_manager.parse_and_add_fact(part, world, interactive=interactive, language=language)
                last_result = {
                    "type": "teaching",
                    "result": teach_res["success"],
                    "message": teach_res["msg"],
                    "status": teach_res.get("status"),
                    "world": world,
                    "trace": [f"تحليل الجملة الخبرية وإدخالها في العالم النشط '{world}'"],
                    "confidence": 1.0
                }
                if idx == len(parts) - 1:
                    return last_result
            else:
                # Identify mapped concepts
                mapped_concepts = []
                for word in words:
                    if not word:
                        continue
                    concept = self.handler.dynamic_morphological_lookup(word, language=language)
                    if concept and concept not in mapped_concepts:
                        mapped_concepts.append(concept)
                        
                # Resolve implicit references (pronouns, verbs) using EntityResolver
                mapped_concepts = self.entity_resolver.resolve(part, mapped_concepts)
                
                # Record turn in conversation manager
                self.conversation_manager.record_turn(part, mapped_concepts)
                
                # 1. Custom celestial/direction query handling for astronomical world questions
                if "c_sun" in mapped_concepts:
                    props = self.handler.get_properties("c_sun", world=world)
                    target = None
                    for p in props:
                        if p["relation"] == "rises_from":
                            target = p["property"]
                            break
                            
                    conflicts = self.conflict_resolver.resolve_conflict("c_sun", "rises_from")
                    conflict_trace = [c["description"] for c in conflicts]
                    
                    is_classification_query = False
                    if language == "ar" and "هل" in words:
                        is_classification_query = True
                    elif language == "en" and any(w in words for w in ["does", "is", "did", "can", "has", "are"]):
                        is_classification_query = True
                    elif language == "fr" and any(w in words for w in ["est-ce", "est", "a-t-il", "peut-il", "a", "ont"]):
                        is_classification_query = True
                        
                    if is_classification_query:
                        dir_concept = None
                        for c in mapped_concepts:
                            if c in ["c_east", "c_west"]:
                                dir_concept = c
                                break
                        if dir_concept and target:
                            is_correct = (target == dir_concept)
                            return {
                                "type": "classification",
                                "result": is_correct,
                                "concept1": "c_sun",
                                "concept2": dir_concept,
                                "trace": [f"الاستعلام عن شروق الشمس في العالم النشط '{world}'", f"الشمس تشرق من {target} في هذا العالم"] + conflict_trace,
                                "confidence": 1.0
                            }
                            
                    if target:
                        target_lbl = self.handler.graph.nodes[target].get("labels", [target])[0]
                        return {
                            "type": "location",
                            "result": True,
                            "concept": "c_sun",
                            "location": target,
                            "location_label": target_lbl,
                            "trace": [f"الاستعلام عن شروق الشمس في العالم النشط '{world}'", f"الشمس تشرق من {target_lbl} في هذا العالم"] + conflict_trace,
                            "confidence": 1.0
                        }

                # 2. Comparison
                if ("الفرق" in words or "difference" in words or "différence" in words or "differance" in words) and len(mapped_concepts) >= 2:
                    c1, c2 = mapped_concepts[0], mapped_concepts[1]
                    props1 = self.handler.get_properties(c1, world=world)
                    props2 = self.handler.get_properties(c2, world=world)
                    return {
                        "type": "comparison",
                        "result": True,
                        "concept1": c1,
                        "concept2": c2,
                        "props1": props1,
                        "props2": props2,
                        "trace": [f"مقارنة الخصائص للـ {c1} والـ {c2} في العالم النشط '{world}'"],
                        "confidence": 1.0
                    }
                    
                # 3. Hypothetical
                elif ("لو" in words or "إذا" in words or "اذا" in words or "if" in words or "si" in words) and len(mapped_concepts) >= 2:
                    entity = None
                    env = None
                    for c in mapped_concepts:
                        cat = self.handler.graph.nodes[c].get("category", "")
                        if c == "feline_carnivore" or cat == "animal":
                            entity = c
                        elif c == "arctic" or cat == "environment":
                            env = c
                            
                    if entity and env:
                        causal_res = self.causal_reasoning(entity, env)
                        trace = list(causal_res["trace"])
                        
                        if causal_res.get("needs_adaptation"):
                            req = causal_res["requirement"]
                            analogy_res = self.analogical_reasoning(entity, env, req)
                            trace.extend(analogy_res["trace"])
                            
                            if analogy_res.get("success"):
                                return {
                                    "type": "hypothetical",
                                    "result": True,
                                    "entity": entity,
                                    "environment": env,
                                    "needs_adaptation": True,
                                    "transferred_property": analogy_res["transferred_property"],
                                    "analogy_candidate": analogy_res["analogy_candidate"],
                                    "trace": trace,
                                    "confidence": analogy_res["similarity"]
                                }
                        return {
                            "type": "hypothetical",
                            "result": False,
                            "entity": entity,
                            "environment": env,
                            "needs_adaptation": False,
                            "trace": trace,
                            "confidence": 1.0
                        }

                # 4. Classification
                else:
                    is_classification_query = False
                    if language == "ar" and "هل" in words:
                        is_classification_query = True
                    elif language == "en" and any(w in words for w in ["does", "is", "did", "can", "has", "are"]):
                        is_classification_query = True
                    elif language == "fr" and any(w in words for w in ["est-ce", "est", "a-t-il", "peut-il", "a", "ont"]):
                        is_classification_query = True
                        
                    if is_classification_query and len(mapped_concepts) >= 2:
                        c1, c2 = mapped_concepts[0], mapped_concepts[1]
                        # Verify order
                        idx1 = min([words.index(w) for w in words if self.handler.dynamic_morphological_lookup(w, language=language) == c1]) if any(self.handler.dynamic_morphological_lookup(w, language=language) == c1 for w in words) else 0
                        idx2 = min([words.index(w) for w in words if self.handler.dynamic_morphological_lookup(w, language=language) == c2]) if any(self.handler.dynamic_morphological_lookup(w, language=language) == c2 for w in words) else 1
                        if idx1 > idx2:
                            c1, c2 = c2, c1
                            
                        res = self.check_is_a_relationship(c1, c2)
                        return {
                            "type": "classification",
                            "result": res["result"],
                            "concept1": c1,
                            "concept2": c2,
                            "trace": res["trace"],
                            "confidence": 1.0
                        }

                # 5. Location (lives_in)
                if ("أين" in words or "اين" in words or "يعيش" in words or "عاش" in words or "where" in words or "où" in words or "ou" in words or "vit" in words or "lives" in words) and len(mapped_concepts) >= 1:
                    concept = mapped_concepts[0]
                    props = self.handler.get_properties(concept, world=world)
                    location = None
                    for p in props:
                        if p["relation"] == "lives_in":
                            location = p["property"]
                            break
                            
                    if location:
                        loc_label = self.handler.graph.nodes[location].get("labels", [location])[0]
                        conflicts = self.conflict_resolver.resolve_conflict(concept, "lives_in")
                        conflict_trace = [c["description"] for c in conflicts]
                        return {
                            "type": "location",
                            "result": True,
                            "concept": concept,
                            "location": location,
                            "location_label": loc_label,
                            "trace": [f"البحث عن موطن {concept} في العالم '{world}'", f"← وجدنا أن {concept} يعيش في {location}"] + conflict_trace,
                            "confidence": 1.0
                        }
                        
                # Default unknown fail-safe
                return {
                    "type": "unknown",
                    "result": False,
                    "trace": ["لم نجد مسار استدلالي منطقي أو تصنيفي واضح يربط بين الكلمات المدخلة في قاعدة المعرفة المتاحة"],
                    "confidence": 0.0
                }
                
        return last_result
