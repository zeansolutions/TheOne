import networkx as nx
from src.utils.logger import logger

class IntentHandlers:
    def __init__(self, reasoner):
        self.reasoner = reasoner

    # Delegators to reasoner's properties & processors
    @property
    def handler(self):
        return self.reasoner.handler

    @property
    def anomaly_processor(self):
        return self.reasoner.anomaly_processor

    @property
    def comparison_processor(self):
        return self.reasoner.comparison_processor

    @property
    def temporal_processor(self):
        return self.reasoner.temporal_processor

    @property
    def modality_processor(self):
        return self.reasoner.modality_processor

    @property
    def chain_processor(self):
        return self.reasoner.chain_processor

    @property
    def quantifier_processor(self):
        return self.reasoner.quantifier_processor

    @property
    def negation_processor(self):
        return self.reasoner.negation_processor

    @property
    def semantic_processor(self):
        return self.reasoner.semantic_processor

    @property
    def conflict_resolver(self):
        return self.reasoner.conflict_resolver

    def check_is_a_relationship(self, *args, **kwargs):
        return self.reasoner.check_is_a_relationship(*args, **kwargs)

    def inheritance_deduction(self, *args, **kwargs):
        return self.reasoner.inheritance_deduction(*args, **kwargs)

    def causal_reasoning(self, *args, **kwargs):
        return self.reasoner.causal_reasoning(*args, **kwargs)

    def analogical_reasoning(self, *args, **kwargs):
        return self.reasoner.analogical_reasoning(*args, **kwargs)

    def _resolve_concept(self, *args, **kwargs):
        return self.reasoner._resolve_concept(*args, **kwargs)

    def _get_concept_index(self, *args, **kwargs):
        return self.reasoner._get_concept_index(*args, **kwargs)

    def _is_classification_word_query(self, *args, **kwargs):
        return self.reasoner._is_classification_word_query(*args, **kwargs)

    def handle_anomaly(self, mapped_concepts, words, prag_trace):
        exceptions = self.anomaly_processor.db.get("exceptions", [])
        for ex in exceptions:
            ex_entity = ex.get("entity")
            ex_property = ex.get("property")
            if ex_entity in mapped_concepts:
                has_property_ref = False
                if ex_property in mapped_concepts:
                    has_property_ref = True
                else:
                    prop_labels = []
                    if self.handler.graph.has_node(ex_property):
                        prop_labels = self.handler.graph.nodes[ex_property].get("labels", [])
                    if any(w in prop_labels or w == ex_property for w in words):
                        has_property_ref = True
                    else:
                        prop_parts = ex_property.replace("_", " ").split()
                        translation_map = {
                            "vegetarian": ["نباتي", "نبات", "vegetarian", "نباتية"],
                            "meat": ["لحم", "لحوم", "meat"],
                            "cold": ["بارد", "برودة", "cold"]
                        }
                        for p_part in prop_parts:
                            if p_part in translation_map:
                                if any(t in words for t in translation_map[p_part]):
                                    has_property_ref = True
                                    break
                                    
                if has_property_ref:
                    anomaly_res = self.anomaly_processor.check_anomaly(ex_entity, "has_property", ex_property)
                    if anomaly_res:
                        entity_lbl = self.handler.graph.nodes[ex_entity].get("labels", [ex_entity])[0] if ex_entity in self.handler.graph else ex_entity
                        return {
                            "type": "anomaly",
                            "result": True,
                            "entity": ex_entity,
                            "anomaly_type": anomaly_res["anomaly_type"],
                            "anomaly_score": anomaly_res["anomaly_score"],
                            "reason": anomaly_res["reason"],
                            "typical_rule": anomaly_res["typical_rule"],
                            "trace": prag_trace + [f"كشف الشذوذ: البحث عن استثناءات للـ {entity_lbl}", f"العثور على استثناء: {anomaly_res['anomaly_type']}"],
                            "confidence": anomaly_res["anomaly_score"]
                        }
        return None

    def handle_comparison_scale(self, mapped_concepts, words, language, prag_trace):
        comp_prop = None
        if any(w in words for w in ["أقوى", "stronger", "fort"]):
            comp_prop = "strength"
        elif any(w in words for w in ["أسرع", "faster", "rapide"]):
            comp_prop = "speed"
            
        if comp_prop and len(mapped_concepts) >= 2:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            try:
                idx1 = self._get_concept_index(c1, words, language, " ".join(words))
                idx2 = self._get_concept_index(c2, words, language, " ".join(words))
                if idx1 > idx2:
                    c1, c2 = c2, c1
            except Exception:
                pass
                
            comparison_val = self.comparison_processor.compare_entities(c1, c2, comp_prop)
            trace_msg = self.comparison_processor.get_comparison_rule_trace(c1, c2, comp_prop)
            
            return {
                "type": "comparison_scale",
                "result": comparison_val > 0,
                "entity1": c1,
                "entity2": c2,
                "property_name": comp_prop,
                "comparison_value": comparison_val,
                "trace": prag_trace + [f"مقارنة الكائنات على مقياس {comp_prop}", trace_msg],
                "confidence": 1.0
            }
        return None

    def handle_temporal_logic(self, mapped_concepts, words, prag_trace):
        is_temporal = any(w in words for w in ["قبل", "بعد", "أثناء", "الماضي", "كان", "مستقبلا", "مستقبلاً", "الآن", "before", "after", "during", "past", "present", "future"])
        if is_temporal:
            event = None
            temporal_facts = self.temporal_processor.db.get("temporal_facts", [])
            for tf in temporal_facts:
                tf_entity = tf.get("entity")
                tf_event = tf.get("event")
                entity_match = False
                if tf_entity in mapped_concepts:
                    entity_match = True
                else:
                    labels = []
                    if self.handler.graph.has_node(tf_entity):
                        labels = self.handler.graph.nodes[tf_entity].get("labels", [])
                    if any(w in labels or w == tf_entity for w in words):
                        entity_match = True
                        
                if entity_match:
                    event_labels = [tf_event, "extinction", "انقراض", "shone", "قرار", "ضلال", "advice", "shone_brightly_for_child", "advice_from_old_star"]
                    if any(w in tf_event or tf_event in w or w in event_labels for w in words):
                        event = f"{tf_entity}_{tf_event}"
                        break
            
            if event:
                is_before = self.temporal_processor.check_temporal_order(event, "present", "BEFORE")
                rel_str = "قبل" if is_before else "ليس قبل"
                return {
                    "type": "temporal_logic",
                    "result": is_before,
                    "event": event,
                    "reference": "present",
                    "relation": "BEFORE",
                    "trace": prag_trace + [f"الاستدلال الزمني: التحقق من الترتيب الزمني للحدث {event}", f"الحدث {event} يقع {rel_str} present بالتعدي الزمني"],
                    "confidence": 1.0
                }
        return None

    def handle_modality(self, mapped_concepts, part, language, world, prag_trace):
        modal_info = self.modality_processor.process_modality(part, language)
        if modal_info["modality"] != "certainty":
            c1 = mapped_concepts[0] if len(mapped_concepts) >= 1 else None
            c2 = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            if c1 and c2:
                res_check = self.check_is_a_relationship(c1, c2)
                if not res_check["result"]:
                    props = self.handler.get_properties(c1, world=world)
                    has_prop = any(p["property"] == c2 for p in props)
                    res_check = {"result": has_prop, "trace": [f"فحص الخاصية {c2} للـ {c1}"]}
                    
                if modal_info["modality"] == "impossibility":
                    result = not res_check["result"]
                elif modal_info["modality"] == "necessity":
                    result = res_check["result"]
                else:
                    result = res_check["result"] or modal_info["confidence"] > 0
                    
                return {
                    "type": "modality",
                    "result": result,
                    "modality": modal_info["modality"],
                    "modality_confidence": modal_info["confidence"],
                    "trace": prag_trace + res_check["trace"] + [f"الاستدلال الموجه بالجهة (Modality): الحالة المكتشفة هي '{modal_info['modality']}' وثقتها {modal_info['confidence']}"],
                    "confidence": modal_info["confidence"]
                }
        return None

    def handle_causal_chain(self, mapped_concepts, words, prag_trace):
        is_chain_query = any(w in words for w in ["سلسلة", "أسباب", "يؤدي", "causes", "chain"])
        if is_chain_query and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            chain_res = self.chain_processor.propagate_causal_chains(concept, self.handler)
            matched = chain_res["matched_chains"]
            if matched:
                steps = matched[0]["steps"]
                trace = prag_trace + [f"الاستدلال السببي متعدد الخطوات (Causal Chain): بدءاً من {concept}"]
                for step in steps:
                    trace.append(f"الخطوة {step['step']}: الحدث {step['event']}")
                return {
                    "type": "causal_chain",
                    "result": True,
                    "initial_state": concept,
                    "chain": matched[0],
                    "trace": trace,
                    "confidence": matched[0]["total_confidence"]
                }
        return None

    def handle_quantifiers(self, mapped_concepts, part, world, prag_trace):
        quantifier_info = self.quantifier_processor.detect_quantifier(part)
        if quantifier_info:
            c1 = mapped_concepts[0] if len(mapped_concepts) >= 1 else None
            c2 = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            if c1 and c2:
                res_check = self.check_is_a_relationship(c1, c2)
                if not res_check["result"]:
                    props = self.handler.get_properties(c1, world=world)
                    has_prop = any(p["property"] == c2 for p in props)
                    res_check = {"result": has_prop, "trace": [f"فحص الخاصية {c2} للـ {c1}"]}
                    
                statement_q = {"name": "universal", "confidence": 1.0}
                result = self.quantifier_processor.evaluate_quantifiers(statement_q, quantifier_info) and res_check["result"]
                
                return {
                    "type": "quantifier",
                    "result": result,
                    "quantifier": quantifier_info["name"],
                    "trace": prag_trace + res_check["trace"] + [f"الاستدلال بسور القضية (Quantifiers): السور المكتشف هو '{quantifier_info['name']}'"],
                    "confidence": quantifier_info["confidence"]
                }
        return None

    def handle_negation(self, mapped_concepts, part, language, world, prag_trace):
        is_negated = self.negation_processor.has_negation(part, language)
        if is_negated:
            c1 = mapped_concepts[0] if len(mapped_concepts) >= 1 else None
            c2 = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            if c1 and c2:
                res_check = self.check_is_a_relationship(c1, c2)
                if not res_check["result"]:
                    props = self.handler.get_properties(c1, world=world)
                    has_prop = any(p["property"] == c2 for p in props)
                    res_check = {"result": has_prop, "trace": [f"فحص الخاصية {c2} للـ {c1}"]}
                    
                return {
                    "type": "negation",
                    "result": not res_check["result"],
                    "trace": prag_trace + res_check["trace"] + [f"الاستدلال بالنفي والتقابل (Negation): تم تطبيق قاعدة نفي النفي وعكس القطبية"],
                    "confidence": 1.0
                }
        return None

    def handle_semantic_roles(self, words, language, prag_trace):
        is_roles_query = any(w in words for w in ["من", "ماذا", "أين", "من الذي", "who", "what", "where"]) and \
                         any(w in words or any(r["id"] in ["فرس", "عوش"] for r in self.handler.language_rules.get("morphology", {}).get("roots", []) if w in r["patterns"]) for w in words)
        if is_roles_query:
            roles_res = self.semantic_processor.extract_semantic_roles(words, language, self.handler)
            if roles_res:
                return {
                    "type": "semantic_roles",
                    "result": True,
                    "predicate": roles_res["predicate"],
                    "roles": roles_res["roles"],
                    "trace": prag_trace + [f"تحليل الأدوار الدلالية (Semantic Roles): استخلاص أدوار الفعل '{roles_res['predicate']}'"],
                    "confidence": 1.0
                }
        return None

    def handle_celestial(self, mapped_concepts, words, language, world, prag_trace, match_res=None):
        if "c_sun" in mapped_concepts:
            props = self.handler.get_properties("c_sun", world=world)
            target = None
            for p in props:
                if p["relation"] == "rises_from":
                    target = p["property"]
                    break
                    
            conflicts = self.conflict_resolver.resolve_conflict("c_sun", "rises_from")
            conflict_trace = [c["description"] for c in conflicts]
            
            is_classification_query = (match_res and match_res.intent == "celestial" and "concept2" in match_res.extracted_entities) or self._is_classification_word_query(words, language)
                
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
                        "trace": prag_trace + [f"الاستعلام عن شروق الشمس في العالم النشط '{world}'", f"الشمس تشرق من {target} في هذا العالم"] + conflict_trace,
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
                    "trace": prag_trace + [f"الاستعلام عن شروق الشمس في العالم النشط '{world}'", f"الشمس تشرق من {target_lbl} في هذا العالم"] + conflict_trace,
                    "confidence": 1.0
                }
        return None

    def handle_comparison_diff(self, mapped_concepts, words, world, prag_trace, match_res=None):
        is_comparison_query = (match_res and match_res.intent == "comparison") or (("الفرق" in words or "difference" in words or "différence" in words or "differance" in words) and len(mapped_concepts) >= 2)
        if is_comparison_query and len(mapped_concepts) >= 2:
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
                "trace": prag_trace + [f"مقارنة الخصائص للـ {c1} والـ {c2} في العالم النشط '{world}'"],
                "confidence": 1.0
            }
        return None

    def handle_hypothetical(self, mapped_concepts, words, prag_trace, match_res=None):
        is_hypothetical = (match_res and match_res.intent == "hypothetical") or (("لو" in words or "إذا" in words or "اذا" in words or "if" in words or "si" in words) and len(mapped_concepts) >= 2)
        if is_hypothetical and len(mapped_concepts) >= 2:
            entity = None
            env = None
            for c in mapped_concepts:
                cat = self.handler.graph.nodes[c].get("category", "") if c in self.handler.graph else ""
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
                            "trace": prag_trace + trace,
                            "confidence": analogy_res["similarity"]
                        }
                return {
                    "type": "hypothetical",
                    "result": False,
                    "entity": entity,
                    "environment": env,
                    "needs_adaptation": False,
                    "trace": prag_trace + trace,
                    "confidence": 1.0
                }
        return None

    def handle_location(self, mapped_concepts, words, world, prag_trace, match_res=None):
        loc_settings = self.handler.language_rules.get("location_query_settings", {})
        loc_particles = loc_settings.get("question_particles", ["أين", "اين", "where", "où", "ou"])
        loc_verbs = loc_settings.get("verbs", ["يعيش", "عاش", "يسكن", "live", "lives", "vit", "vivent", "located"])
        
        is_location_query = (match_res and match_res.intent == "location") or any(w in words for w in loc_particles + loc_verbs)
        
        if is_location_query and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            props = self.handler.get_properties(concept, world=world)
            location = None
            relation_used = "lives_in"
            
            for p in props:
                rel = p.get("relation")
                prop_node = p.get("property")
                prop_data = self.handler.graph.nodes.get(prop_node, {}) if self.handler.graph.has_node(prop_node) else {}
                if rel in ["lives_in", "located_in"] or prop_data.get("category") == "location":
                    location = prop_node
                    relation_used = rel
                    break
                    
            if location:
                loc_label = self.handler.graph.nodes[location].get("labels", [location])[0] if location in self.handler.graph else location
                conflicts = self.conflict_resolver.resolve_conflict(concept, relation_used)
                conflict_trace = [c["description"] for c in conflicts]
                
                # Dynamic translation of relation verb in trace
                rel_label = relation_used
                for lang in ["ar", "en", "fr"]:
                    lang_rels = self.handler.language_rules.get(lang, {}).get("relations", {})
                    for k, v in lang_rels.items():
                        if v == relation_used:
                            rel_label = k
                            break
                    if rel_label != relation_used:
                        break
                
                if "ar" in self.handler.language_rules and any(v == relation_used for v in self.handler.language_rules.get("ar", {}).get("relations", {}).values()):
                    trace_msg = f"← وجدنا أن {concept} {rel_label} {loc_label}"
                else:
                    trace_msg = f"← وجدنا أن {concept} {relation_used} {location}"
                
                return {
                    "type": "location",
                    "result": True,
                    "concept": concept,
                    "location": location,
                    "location_label": loc_label,
                    "trace": prag_trace + [f"البحث عن موطن {concept} في العالم '{world}'", trace_msg] + conflict_trace,
                    "confidence": 1.0
                }
        return None

    def handle_causal_why(self, mapped_concepts, words, world, part, prag_trace):
        is_why_query = any(w in words for w in ["لماذا", "ليه", "بسبب", "علل", "why", "because", "pourquoi", "cause"])
        if is_why_query and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            target_concept = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            
            found_edge = None
            if self.handler.graph.has_node(concept):
                for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                    if data.get("type") == "inferred" and data.get("world") == world:
                        if target_concept:
                            if to_node == target_concept:
                                found_edge = (concept, to_node, data)
                                break
                        else:
                            target_labels = self.handler.graph.nodes[to_node].get("labels", [])
                            if any(w in target_labels for w in words):
                                found_edge = (concept, to_node, data)
                                break
                                
                if not found_edge and not target_concept:
                    for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                        if data.get("type") == "inferred" and data.get("world") == world:
                            found_edge = (concept, to_node, data)
                            break
                             
            if found_edge:
                sub, obj, data = found_edge
                sub_lbl = self.handler.graph.nodes[sub].get("labels", [sub])[0] if sub in self.handler.graph else sub
                obj_lbl = self.handler.graph.nodes[obj].get("labels", [obj])[0] if obj in self.handler.graph else obj
                rel_name = data.get("relation", "relation")
                
                rule_desc = data.get("reason", "")
                rule_id = data.get("rule_id", "unknown_rule")
                confidence = data.get("confidence", 1.0)
                
                trace_chain = [
                    f"Parse: تحليل الاستعلام السببي '{part}'",
                    f"Extract: subject={sub_lbl} ({sub}), relation={rel_name}, target={obj_lbl} ({obj})",
                    f"Search Direct Facts: لم يتم العثور عليها كحقيقة مباشرة",
                    f"Apply Rules: تم تطبيق قاعدة الاستدلال '{rule_id}'",
                    f"Condition: مطابقة شروط القاعدة بنجاح",
                    f"Conclusion: استنتاج [{sub_lbl}] --({rel_name})--> [{obj_lbl}] (ثقة: {confidence})",
                    f"Result: {rule_desc}"
                ]
                
                return {
                    "type": "causal_reasoning",
                    "result": True,
                    "subject": sub,
                    "subject_label": sub_lbl,
                    "relation": rel_name,
                    "object": obj,
                    "object_label": obj_lbl,
                    "reason": rule_desc,
                    "rule_id": rule_id,
                    "trace": prag_trace + trace_chain,
                    "confidence": confidence
                }
        return None

    def handle_classification(self, mapped_concepts, words, language, part, prag_trace, match_res=None):
        is_classification_query = (match_res and match_res.intent == "classification") or self._is_classification_word_query(words, language)
            
        if is_classification_query and len(mapped_concepts) >= 2:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            if len(mapped_concepts) >= 3:
                mc0 = mapped_concepts[0]
                mc1 = mapped_concepts[1]
                connected = False
                if self.handler and self.handler.graph:
                    if self.handler.graph.has_node(mc0) and self.handler.graph.has_node(mc1):
                        if self.handler.graph.has_edge(mc0, mc1) or self.handler.graph.has_edge(mc1, mc0):
                            connected = True
                if connected:
                    c1 = mc0
                    c2 = mapped_concepts[2]
            else:
                try:
                    idx1 = self._get_concept_index(c1, words, language, part)
                    idx2 = self._get_concept_index(c2, words, language, part)
                    if idx1 > idx2:
                        c1, c2 = c2, c1
                except Exception:
                    pass
                
            is_same_type_query = False
            same_type_markers = []
            if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
                lang_rules = self.handler.language_rules.get(language, {})
                same_type_markers = list(lang_rules.get("same_type_indicators", []))
                if not same_type_markers:
                    for lang in ["ar", "en", "fr"]:
                        same_type_markers.extend(self.handler.language_rules.get(lang, {}).get("same_type_indicators", []))
                        
            if not same_type_markers:
                same_type_markers = [
                    "نفس النوع", "نفس الفئة", "نفس التصنيف", "نوع واحد", "نفس فئة",
                    "same type", "same category", "same class", "same kind",
                    "même type", "meme type", "même catégorie", "meme categorie", "même classe"
                ]
            if any(marker in part.lower() for marker in same_type_markers):
                is_same_type_query = True
                
            if is_same_type_query:
                cat1 = self.handler.graph.nodes[c1].get("category") if c1 in self.handler.graph else None
                cat2 = self.handler.graph.nodes[c2].get("category") if c2 in self.handler.graph else None
                
                parents1 = set()
                parents2 = set()
                if c1 in self.handler.graph:
                    for _, to_node, data in self.handler.graph.out_edges(c1, data=True):
                        if data.get("relation") == "is_a":
                            parents1.add(to_node)
                if c2 in self.handler.graph:
                    for _, to_node, data in self.handler.graph.out_edges(c2, data=True):
                        if data.get("relation") == "is_a":
                            parents2.add(to_node)
                            
                shared_parents = parents1.intersection(parents2)
                
                is_same = False
                reason = ""
                if cat1 and cat2 and cat1 == cat2:
                    is_same = True
                    cat_label = self.handler.graph.nodes[cat1].get("labels", [cat1])[0] if cat1 in self.handler.graph else cat1
                    reason = f"كلا المفهومين ينتميان لنفس الفئة العامة [{cat_label}]"
                elif shared_parents:
                    is_same = True
                    parent_lbl = self.handler.graph.nodes[list(shared_parents)[0]].get("labels", [list(shared_parents)[0]])[0] if list(shared_parents)[0] in self.handler.graph else list(shared_parents)[0]
                    reason = f"كلا المفهومين يشتركان في التصنيف الفرعي المباشر [{parent_lbl}]"
                else:
                    reason = f"لا يوجد فئة عامة مشتركة أو سلف تصنيفي مباشر يربط بين المفهومين"
                    
                c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
                c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2
                
                return {
                    "type": "classification",
                    "result": is_same,
                    "concept1": c1,
                    "concept2": c2,
                    "is_same_type": True,
                    "trace": prag_trace + [f"التحقق من تطابق النوع لـ '{c1_lbl}' و '{c2_lbl}'", reason],
                    "confidence": 1.0
                }
            else:
                res = self.check_is_a_relationship(c1, c2)
                if res["result"]:
                    return {
                        "type": "classification",
                        "result": True,
                        "concept1": c1,
                        "concept2": c2,
                        "trace": prag_trace + res["trace"],
                        "confidence": 1.0
                    }
                
                # Check for other relationships in the active world between c1 (or ancestors) and c2 (or ancestors)
                # Find ancestors of c1
                ancestors1 = {c1}
                to_explore = [c1]
                while to_explore:
                    curr = to_explore.pop(0)
                    if self.handler.graph.has_node(curr):
                        for _, to_node, edata in self.handler.graph.out_edges(curr, data=True):
                            if edata.get("relation") == "is_a":
                                if to_node not in ancestors1:
                                    ancestors1.add(to_node)
                                    to_explore.append(to_node)
                                    
                # Find ancestors of c2
                ancestors2 = {c2}
                to_explore = [c2]
                while to_explore:
                    curr = to_explore.pop(0)
                    if self.handler.graph.has_node(curr):
                        for _, to_node, edata in self.handler.graph.out_edges(curr, data=True):
                            if edata.get("relation") == "is_a":
                                if to_node not in ancestors2:
                                    ancestors2.add(to_node)
                                    to_explore.append(to_node)
                                    
                # Check active/inferred edges
                world = self.handler.active_world
                found_relation = None
                edge_data = None
                u_source = None
                v_target = None
                
                ALLOWED_CLASSIFICATION_RELATIONS = {
                    "has_property", "hasproperty", "has_behavior", "has_assigned_case",
                    "characterizes_temporarily", "capable_of", "capableof",
                    "has_case_capability", "has_case"
                }
                
                for u in ancestors1:
                    if self.handler.graph.has_node(u):
                        for _, v_node, data in self.handler.graph.out_edges(u, data=True):
                            if v_node in ancestors2:
                                edge_world = data.get("world", "reality")
                                edge_status = data.get("status", "active")
                                if edge_world == world and edge_status == "active":
                                    rel = data.get("relation")
                                    if rel in ALLOWED_CLASSIFICATION_RELATIONS or rel in ["prohibited_case", "prohibited_relation"]:
                                        found_relation = rel
                                        edge_data = data
                                        u_source = u
                                        v_target = v_node
                                        break
                        if found_relation:
                            break
                            
                if found_relation:
                    # If the relation is "prohibited_case" or "prohibited_relation", the logical conclusion is False
                    is_prohibited = found_relation in ["prohibited_case", "prohibited_relation"]
                    result_val = not is_prohibited
                    
                    c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
                    c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2
                    u_lbl = self.handler.graph.nodes[u_source].get("labels", [u_source])[0] if u_source in self.handler.graph else u_source
                    v_lbl = self.handler.graph.nodes[v_target].get("labels", [v_target])[0] if v_target in self.handler.graph else v_target
                    
                    rel_meta = self.handler.graph.graph.get("relations_metadata", {})
                    rel_display = rel_meta.get(found_relation, {}).get("name", found_relation) if isinstance(rel_meta, dict) else found_relation
                    
                    if is_prohibited:
                        conclusion = f"العلاقة محظورة: [{u_lbl}] --({rel_display})--> [{v_lbl}]"
                    else:
                        conclusion = f"تم العثور على علاقة منطقية: [{u_lbl}] --({rel_display})--> [{v_lbl}]"
                        
                    return {
                        "type": "classification",
                        "result": result_val,
                        "concept1": c1,
                        "concept2": c2,
                        "trace": prag_trace + [
                            f"استعلام علاقة تصنيفية بين '{c1_lbl}' و '{c2_lbl}'",
                            conclusion
                        ],
                        "confidence": edge_data.get("confidence", 1.0)
                    }
                    
                return {
                    "type": "classification",
                    "result": False,
                    "concept1": c1,
                    "concept2": c2,
                    "trace": prag_trace + res["trace"] + ["لا يوجد علاقة تصنيفية أو حكم منطقي يربط بين المفهومين في قاعدة المعرفة"],
                    "confidence": 1.0
                }
        return None

    def handle_relation_path(self, mapped_concepts, part, world, prag_trace, words, match_res=None, is_deep=None, language=None):
        if language is None:
            language = "ar"
        is_relation_query = (match_res and match_res.intent == "relation_path") or (any(w in words for w in ["علاقة", "الروابط", "رابط", "يربط", "علاقه", "العلاقة", "العلاقه", "relation", "relationship", "connect", "connection", "link", "between", "entre"]) and len(mapped_concepts) >= 2)
        if is_relation_query:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
            c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2
            
            if is_deep is None:
                is_deep = (match_res and getattr(match_res, "is_deep", False)) or any(keyword in part.lower() for keyword in ["عميق", "مسار", "سلسلة", "تتبع", "مفصل", "تفصيل", "deep", "detailed", "path", "traverse", "unrestricted", "chain"])
            
            active_undirected = nx.Graph()
            for node in self.handler.graph.nodes():
                active_undirected.add_node(node)
                
            for u, v, data in self.handler.graph.edges(data=True):
                edge_type = data.get("type", "relation")
                edge_world = data.get("world", "reality")
                edge_status = data.get("status", "active")
                if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                    if edge_status == "active":
                        if not active_undirected.has_edge(u, v):
                            active_undirected.add_edge(u, v, edges=[])
                        active_undirected[u][v]['edges'].append((u, v, data))
                        
            path_steps = []
            path_found = False
            path_nodes = []
            
            if is_deep:
                try:
                    for meta_node in ["user_defined", "concept", "category", "unknown"]:
                        if active_undirected.has_node(meta_node) and meta_node != c1 and meta_node != c2:
                            active_undirected.remove_node(meta_node)
                    path_nodes = nx.shortest_path(active_undirected, source=c1, target=c2)
                    path_found = True
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    path_found = False
            else:
                if active_undirected.has_edge(c1, c2):
                    path_nodes = [c1, c2]
                    path_found = True
                else:
                    path_found = False
                    
            if not path_found:
                # Find if they share a common ancestor
                def get_ancestors(node):
                    anc = [node]
                    visited = set()
                    queue = [node]
                    while queue:
                        curr = queue.pop(0)
                        if curr in visited:
                            continue
                        visited.add(curr)
                        if self.handler.graph.has_node(curr):
                            for _, to_node, data in self.handler.graph.out_edges(curr, data=True):
                                if data.get("relation") == "is_a" and data.get("status", "active") == "active":
                                    if to_node not in anc:
                                        anc.append(to_node)
                                        queue.append(to_node)
                    return anc

                anc1 = get_ancestors(c1)
                anc2 = get_ancestors(c2)
                common_ancestor = None
                for a in anc1:
                    if a in anc2 and a != c1 and a != c2:
                        if a not in ["user_defined", "concept", "category", "unknown"]:
                            common_ancestor = a
                            break
                
                if common_ancestor:
                    anc_label = self.handler.graph.nodes[common_ancestor].get("labels", [common_ancestor])[0] if common_ancestor in self.handler.graph else common_ancestor
                    # Try to get translation of the common ancestor if available in lexicon
                    lang_lex = self.handler.language_rules.get(language, {}).get("lexicon", {})
                    for k, v in lang_lex.items():
                        if v == common_ancestor:
                            anc_label = k
                            break
                            
                    # Construct step description based on language
                    if language == "ar":
                        step_desc = f"كلاهما يندرجان تحت تصنيف {anc_label}"
                    elif language == "fr":
                        step_desc = f"les deux appartiennent à la catégorie {anc_label}"
                    else:
                        step_desc = f"both belong to the category {anc_label}"
                        
                    path_steps = [step_desc]
                    path_found = True
                    path_nodes = [c1, common_ancestor, c2]

            if path_found and len(path_nodes) >= 2:
                if not path_steps:
                    for i in range(len(path_nodes) - 1):
                        u_node = path_nodes[i]
                        v_node = path_nodes[i+1]
                        edge_list = active_undirected[u_node][v_node]['edges']
                        step_desc_list = []
                        for src, tgt, edge_data in edge_list:
                            rel_name = edge_data.get("relation", "relation")
                            rel_display = self.handler.get_relation_label(rel_name, language)

                            src_lbl = self.handler.graph.nodes[src].get("labels", [src])[0] if src in self.handler.graph else src
                            tgt_lbl = self.handler.graph.nodes[tgt].get("labels", [tgt])[0] if tgt in self.handler.graph else tgt
                            step_desc_list.append(f"({src_lbl}) --[{rel_display}]--> ({tgt_lbl})")
                        path_steps.append(" أو ".join(step_desc_list))
                    
                query_mode_str = "عميق" if is_deep else "محدد"
                trace_msg = [
                    f"استعلام علاقات {query_mode_str} بين '{c1_lbl}' و '{c2_lbl}'",
                    f"تم العثور على مسار يربط بين المفهومين يتكون من {len(path_nodes)} عقدة"
                ]
                
                return {
                    "type": "relation_path",
                    "result": True,
                    "concept1": c1,
                    "concept1_label": c1_lbl,
                    "concept2": c2,
                    "concept2_label": c2_lbl,
                    "is_deep": is_deep,
                    "path_found": True,
                    "path_nodes": path_nodes,
                    "path_steps": path_steps,
                    "trace": prag_trace + trace_msg,
                    "confidence": 1.0
                }
            else:
                query_mode_str = "عميق" if is_deep else "محدد"
                fail_msg = f"لا يوجد مسار علاقة {query_mode_str} يربط بين المفهومين '{c1_lbl}' و '{c2_lbl}' في قاعدة معرفة العالم '{world}'."
                if not is_deep:
                    fail_msg += " (يمكنك تجربة الاستعلام العميق بإضافة كلمة 'عميقة' أو 'مسار' لملاحظة الروابط غير المباشرة)."
                return {
                    "type": "relation_path",
                    "result": False,
                    "concept1": c1,
                    "concept1_label": c1_lbl,
                    "concept2": c2,
                    "concept2_label": c2_lbl,
                    "is_deep": is_deep,
                    "path_found": False,
                    "path_nodes": [],
                    "path_steps": [],
                    "trace": prag_trace + [f"استعلام علاقات {query_mode_str} بين '{c1_lbl}' و '{c2_lbl}'", "لم يتم العثور على روابط متصلة"],
                    "message": fail_msg,
                    "confidence": 0.8
                }
        return None

    def handle_describe(self, mapped_concepts, words, world, prag_trace, match_res=None):
        is_describe_query = ((match_res and match_res.intent == "describe") or any(w in words for w in ["ما", "ماذا", "what", "من", "who", "هي", "هو"])) and len(mapped_concepts) >= 1
        if is_describe_query:
            concept = mapped_concepts[0]
            all_relations = []
            if self.handler.graph.has_node(concept):
                for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            rel_name = data.get("relation", "unknown")
                            if rel_name in ["formof", "derivedfrom", "etymologicallyrelatedto", "etymologicallyderivedfrom", "etymologicalorigin", "externalurl", "pronunciation", "soundsalike"]:
                                continue
                            to_label = self.handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in self.handler.graph else to_node
                            rel_meta = self.handler.graph.graph.get("relations_metadata", {})
                            if isinstance(rel_meta, dict) and rel_name in rel_meta:
                                rel_display = rel_meta[rel_name].get("name", rel_name)
                            else:
                                rel_display = rel_name
                            all_relations.append({
                                "relation": rel_name,
                                "relation_display": rel_display,
                                "target": to_node,
                                "target_label": to_label,
                                "confidence": data.get("confidence", 1.0)
                            })
                for from_node, _, data in self.handler.graph.in_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            rel_name = data.get("relation", "unknown")
                            if rel_name in ["formof", "derivedfrom", "etymologicallyrelatedto", "etymologicallyderivedfrom", "etymologicalorigin", "externalurl", "pronunciation", "soundsalike"]:
                                continue
                            from_label = self.handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in self.handler.graph else from_node
                            all_relations.append({
                                "relation": rel_name,
                                "source": from_node,
                                "source_label": from_label,
                                "direction": "incoming",
                                "confidence": data.get("confidence", 1.0)
                            })
            
            if all_relations:
                concept_label = self.handler.graph.nodes[concept].get("labels", [concept])[0] if concept in self.handler.graph else concept
                concept_category = self.handler.graph.nodes[concept].get("category", "") if concept in self.handler.graph else ""
                return {
                    "type": "describe",
                    "result": True,
                    "concept": concept,
                    "concept_label": concept_label,
                    "category": concept_category,
                    "relations": all_relations,
                    "trace": prag_trace + [f"استعلام وصفي عن المفهوم '{concept_label}' ({concept})", f"تم العثور على {len(all_relations)} علاقة مرتبطة"],
                    "confidence": 1.0
                }
        return None

    def handle_knowledge_fallback(self, mapped_concepts, world, prag_trace):
        if len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            all_out = []
            all_in = []
            if self.handler.graph.has_node(concept):
                for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            rel_name = data.get("relation", "unknown")
                            if rel_name in ["formof", "derivedfrom", "etymologicallyrelatedto", "etymologicallyderivedfrom", "etymologicalorigin", "externalurl", "pronunciation", "soundsalike"]:
                                continue
                            to_label = self.handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in self.handler.graph else to_node
                            all_out.append({
                                "relation": rel_name,
                                "target": to_node,
                                "target_label": to_label
                            })
                for from_node, _, data in self.handler.graph.in_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            rel_name = data.get("relation", "unknown")
                            if rel_name in ["formof", "derivedfrom", "etymologicallyrelatedto", "etymologicallyderivedfrom", "etymologicalorigin", "externalurl", "pronunciation", "soundsalike"]:
                                continue
                            from_label = self.handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in self.handler.graph else from_node
                            all_in.append({
                                "relation": rel_name,
                                "source": from_node,
                                "source_label": from_label
                            })
            
            if all_out or all_in:
                concept_label = self.handler.graph.nodes[concept].get("labels", [concept])[0] if concept in self.handler.graph else concept
                return {
                    "type": "knowledge",
                    "result": True,
                    "concept": concept,
                    "concept_label": concept_label,
                    "outgoing": all_out,
                    "incoming": all_in,
                    "trace": prag_trace + [f"استعلام عام عن المعرفة المتوفرة حول '{concept_label}'", f"← علاقات صادرة: {len(all_out)}, علاقات واردة: {len(all_in)}"],
                    "confidence": 0.8
                }
        return None
