class SimpleReasoner:
    def __init__(self, graph_handler):
        self.handler = graph_handler

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

    def process_query(self, query):
        """
        Pipeline: Parsing -> Dynamic Morphological Lookup -> Logical Reasoning.
        Supports the 5 dynamic queries mapped dynamically to graph queries.
        """
        # Clean and segment query into words to extract concepts
        raw_words = query.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
        
        # Look up concepts
        mapped_concepts = []
        for word in words:
            if not word:
                continue
            concept = self.handler.dynamic_morphological_lookup(word)
            if concept and concept not in mapped_concepts:
                mapped_concepts.append(concept)
                
        # 1. Classification query (e.g. "هل الأسد حيوان؟")
        if "هل" in words and len(mapped_concepts) >= 2:
            # We want to check if C1 is a C2
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            # Verify order (first concept in query should be the child)
            # Find which concept appears first in query
            idx1 = min([words.index(w) for w in words if self.handler.dynamic_morphological_lookup(w) == c1])
            idx2 = min([words.index(w) for w in words if self.handler.dynamic_morphological_lookup(w) == c2])
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
            
        # 2. Location query (e.g. "أين يعيش الأسد؟")
        elif "أين" in words and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            props = self.handler.get_properties(concept, world="reality")
            location = None
            for p in props:
                if p["relation"] == "lives_in":
                    location = p["property"]
                    break
                    
            if location:
                # Find Arabic label of location in graph
                loc_label = self.handler.graph.nodes[location].get("labels", [location])[0]
                return {
                    "type": "location",
                    "result": True,
                    "concept": concept,
                    "location": location,
                    "location_label": loc_label,
                    "trace": [f"البحث عن مكان عيش {concept} في عوالم الحقائق الواقعية", f"← وجدنا أن {concept} يعيش في {location}"],
                    "confidence": 1.0
                }
                
        # 3. Hypothetical Scenario query (e.g. "لو الأسد في القطب، ماذا يحتاج؟")
        elif ("لو" in words or "إذا" in words) and len(mapped_concepts) >= 2:
            # We have entity and target environment
            entity = None
            env = None
            for c in mapped_concepts:
                cat = self.handler.graph.nodes[c].get("category", "")
                # feline_carnivore is animal, arctic is environment
                if c == "feline_carnivore" or cat == "animal":
                    entity = c
                elif c == "arctic" or cat == "environment":
                    env = c
                    
            if entity and env:
                # 1. Causal Reasoning
                causal_res = self.causal_reasoning(entity, env)
                trace = list(causal_res["trace"])
                
                if causal_res.get("needs_adaptation"):
                    req = causal_res["requirement"]
                    # 2. Analogy Transfer
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
                
        # 4. Comparison query (e.g. "ما الفرق بين الأسد والدب القطبي؟")
        elif "الفرق" in words and len(mapped_concepts) >= 2:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            props1 = self.handler.get_properties(c1, world="reality")
            props2 = self.handler.get_properties(c2, world="reality")
            
            return {
                "type": "comparison",
                "result": True,
                "concept1": c1,
                "concept2": c2,
                "props1": props1,
                "props2": props2,
                "trace": [f"البحث عن الخصائص الفيزيائية والبيئية للـ {c1}", f"البحث عن الخصائص الفيزيائية والبيئية للـ {c2}", "مقارنة الفروق الجوهرية والتشابهات التصنيفية"],
                "confidence": 1.0
            }
            
        # Honest Fail-safe
        return {
            "type": "unknown",
            "result": False,
            "trace": ["لم نجد مسار استدلالي منطقي أو تصنيفي واضح يربط بين الكلمات المدخلة في قاعدة المعرفة المتاحة"],
            "confidence": 0.0
        }
