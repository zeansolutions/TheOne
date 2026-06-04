import json
import random

class ResponseGeneratorSimple:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        
        # Load fallback templates from JSON
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fallback_path = os.path.join(base_dir, "data", "fallback_templates.json")
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                self.fallback_db = json.load(f)
        except Exception:
            self.fallback_db = {"concept_labels": {}, "templates": {}}

    def get_template(self, key, language, default):
        """Retrieves a template from language_rules or falls back to default."""
        lang_rules = self.handler.language_rules.get(language, {})
        templates = lang_rules.get("templates", {})
        return templates.get(key, default)

    def get_fallback_template(self, key, language):
        """Retrieves a baseline fallback template from the fallback database."""
        return self.fallback_db.get("templates", {}).get(language, {}).get(key, "")

    def get_concept_label(self, concept_id, language="ar"):
        """Translates a concept ID into the target language label."""
        # 1. Try fallbacks for common concepts first (to guarantee correct baseline translation)
        fallback_map = self.fallback_db.get("concept_labels", {}).get(language, {})
        if concept_id in fallback_map:
            return fallback_map[concept_id]

        # 2. Try to get from language rules lexicon (dynamic database lookup)
        lang_rules = self.handler.language_rules.get(language, {})
        lexicon = lang_rules.get("lexicon", {})
        
        candidates = []
        for k, v in lexicon.items():
            if v == concept_id:
                candidates.append(k)
        if candidates:
            candidates.sort(key=len)
            return candidates[0]
            
        # 3. Fallback to node labels in graph
        if self.handler.graph.has_node(concept_id):
            labels = self.handler.graph.nodes[concept_id].get("labels", [])
            if labels:
                return labels[0]

        return concept_id

    def find_lowest_common_ancestor(self, c1, c2):
        """Finds the lowest common ancestor node using is_a relations."""
        def get_ancestors(node):
            ancestors = [node]
            visited = set()
            queue = [node]
            while queue:
                curr = queue.pop(0)
                if curr in visited:
                    continue
                visited.add(curr)
                if self.handler.graph.has_node(curr):
                    for _, to_node, data in self.handler.graph.out_edges(curr, data=True):
                        if data.get("relation") == "is_a":
                            if to_node not in ancestors:
                                ancestors.append(to_node)
                                queue.append(to_node)
            return ancestors

        anc1 = get_ancestors(c1)
        anc2 = get_ancestors(c2)
        for a in anc1:
            if a in anc2:
                return a
        return None

    def generate(self, res, persona_id="persona_1", language=None):
        """Generates a natural language response from the reasoning result, applying templates and persona styling."""
        if language is None:
            language = res.get("language") or getattr(self.handler, "active_language", "ar")
        if language not in ["ar", "en", "fr"]:
            language = "ar"

        persona = self.handler.get_persona(persona_id)
        
        # Load persona rules dynamically
        particles = [""]
        fillers = [""]
        if persona:
            style = persona.get("language_style", {})
            particles = style.get("particles", [""])
            fillers = style.get("filler_words", [""])
            
        p_ref = random.choice(particles) if particles else ""
        f_ref = random.choice(fillers) if fillers else ""
        
        if language == "ar":
            prefix = f"{p_ref}، {f_ref} " if (p_ref or f_ref) else ""
        else:
            prefix = f"{p_ref}, {f_ref} " if (p_ref or f_ref) else ""
            prefix = prefix.strip(", ") + " " if prefix else ""
            
        type_ = res.get("type", "unknown")
        
        # 1. Classification Response
        if type_ == "classification":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            key = "classification_true" if res["result"] else "classification_false"
            
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            ans = template.format(concept1=c1_lbl, concept2=c2_lbl)
            return prefix + ans
                 
        # 2. Location Response
        elif type_ == "location":
            c_lbl = self.get_concept_label(res["concept"], language)
            loc_lbl = self.get_concept_label(res.get("location_label", res.get("location", "")), language)
            
            template = self.get_template("location", language, self.get_fallback_template("location", language))
            ans = template.format(concept=c_lbl, location=loc_lbl)
            return prefix + ans
            
        # 3. Hypothetical Response (Causal + Analogy)
        elif type_ == "hypothetical":
            entity_lbl = self.get_concept_label(res["entity"], language)
            env_lbl = self.get_concept_label(res["environment"], language)
            
            if res["needs_adaptation"]:
                prop_lbl = self.get_concept_label(res["transferred_property"], language)
                cand_lbl = self.get_concept_label(res["analogy_candidate"], language)
                
                template = self.get_template("hypothetical_needs_adaptation", language, self.get_fallback_template("hypothetical_needs_adaptation", language))
                ans = template.format(entity=entity_lbl, environment=env_lbl, transferred_property=prop_lbl, analogy_candidate=cand_lbl)
            else:
                template = self.get_template("hypothetical_no_adaptation", language, self.get_fallback_template("hypothetical_no_adaptation", language))
                ans = template.format(entity=entity_lbl, environment=env_lbl)
            return prefix + ans
                 
        # 4. Comparison Response
        elif type_ == "comparison":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            
            p1_str = "، ".join([self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "has_property"])
            p2_str = ".. ".join([self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "has_property"])
            
            l1 = next((self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "lives_in"), None)
            l2 = next((self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "lives_in"), None)
            
            common = self.find_lowest_common_ancestor(res["concept1"], res["concept2"])
            
            l1_fallback = self.get_template("comparison_lives_in_fallback", language, self.get_fallback_template("comparison_lives_in_fallback", language))
            p1_fallback = self.get_template("comparison_props_fallback_1", language, self.get_fallback_template("comparison_props_fallback_1", language))
            p2_fallback = self.get_template("comparison_props_fallback_2", language, self.get_fallback_template("comparison_props_fallback_2", language))
            common_fallback = self.get_template("comparison_common_fallback", language, self.get_fallback_template("comparison_common_fallback", language))
            
            l1_str = l1 or l1_fallback
            l2_str = l2 or l2_fallback
            p1_formatted = p1_str or p1_fallback
            p2_formatted = p2_str or p2_fallback
            
            common_lbl = self.get_concept_label(common, language) if common else common_fallback
            
            template = self.get_template("comparison", language, self.get_fallback_template("comparison", language))
            ans = template.format(
                concept1=c1_lbl,
                concept2=c2_lbl,
                l1_str=l1_str,
                l2_str=l2_str,
                p1_formatted=p1_formatted,
                p2_formatted=p2_formatted,
                common_lbl=common_lbl
            )
            return prefix + ans
             
        # 6. Teaching Response
        elif type_ == "teaching":
            status = res.get("status")
            world = res.get("world", "reality")
            msg = res.get("message", "")
            
            status_keys = {
                "added": "teaching_added",
                "identical": "teaching_identical",
                "auto_replaced": "teaching_auto_replaced",
                "auto_rejected": "teaching_auto_rejected",
                "non_interactive_rejected": "teaching_non_interactive_rejected"
            }
            
            key = status_keys.get(status)
            if key:
                template = self.get_template(key, language, self.get_fallback_template(key, language))
                ans = template.format(world=world)
            else:
                template = self.get_template("teaching_fallback", language, msg or self.get_fallback_template("teaching_fallback", language))
                ans = template
            return prefix + ans
             
        # 7. Anomaly Response
        elif type_ == "anomaly":
            entity_lbl = self.get_concept_label(res["entity"], language)
            template = self.get_template("anomaly", language, self.get_fallback_template("anomaly", language))
            ans = template.format(entity=entity_lbl, anomaly_type=res["anomaly_type"], reason=res["reason"], anomaly_score=res["anomaly_score"])
            return prefix + ans
             
        # 8. Comparison Scale Response
        elif type_ == "comparison_scale":
            c1_lbl = self.get_concept_label(res["entity1"], language)
            c2_lbl = self.get_concept_label(res["entity2"], language)
            key = "comparison_scale_true" if res["result"] else "comparison_scale_false"
            
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            ans = template.format(entity1=c1_lbl, entity2=c2_lbl, property_name=res["property_name"])
            return prefix + ans
             
        # 9. Temporal Logic Response
        elif type_ == "temporal_logic":
            key = "temporal_logic_true" if res["result"] else "temporal_logic_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            ans = template.format(event=res["event"], reference=res["reference"])
            return prefix + ans
             
        # 10. Modality Response
        elif type_ == "modality":
            key = "modality_true" if res["result"] else "modality_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            ans = template.format(modality=res["modality"], modality_confidence=res["modality_confidence"])
            return prefix + ans
             
        # 11. Causal Chain Response
        elif type_ == "causal_chain":
            steps = res["chain"]["steps"]
            chain_str = " -> ".join([f"[{s['event']}]" for s in steps])
            template = self.get_template("causal_chain", language, self.get_fallback_template("causal_chain", language))
            ans = template.format(initial_state=res["initial_state"], chain_str=chain_str)
            return prefix + ans
             
        # 12. Quantifier Response
        elif type_ == "quantifier":
            key = "quantifier_true" if res["result"] else "quantifier_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            ans = template.format(quantifier=res["quantifier"])
            return prefix + ans
             
        # 13. Negation Response
        elif type_ == "negation":
            key = "negation_true" if res["result"] else "negation_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            ans = template
            return prefix + ans
             
        # 14. Causal Reasoning Response (Why query / Inference Rules)
        elif type_ == "causal_reasoning":
            return prefix + res.get("reason", "")
 
        # 15. Semantic Roles Response
        elif type_ == "semantic_roles":
            roles_list = []
            for r_type, val in res["roles"].items():
                val_lbl = self.get_concept_label(val, language)
                roles_list.append(f"{r_type}: {val_lbl}")
            sep = self.get_template("semantic_roles_separator", language, self.get_fallback_template("semantic_roles_separator", language))
            roles_str = sep.join(roles_list)
            
            template = self.get_template("semantic_roles", language, self.get_fallback_template("semantic_roles", language))
            ans = template.format(predicate=res["predicate"], roles_str=roles_str)
            return prefix + ans
 
        # 15.5. Relation Path Response
        elif type_ == "relation_path":
            c1_lbl = res.get("concept1_label", "")
            c2_lbl = res.get("concept2_label", "")
            is_deep = res.get("is_deep", False)
            path_steps = res.get("path_steps", [])
            
            if res.get("path_found") and path_steps:
                sep = self.get_template("relation_path_steps_separator", language, self.get_fallback_template("relation_path_steps_separator", language))
                steps_str = sep.join(path_steps)
                if is_deep:
                    key = "relation_path_deep"
                else:
                    key = "relation_path_direct"
                template = self.get_template(key, language, self.get_fallback_template(key, language))
                ans = template.format(concept1=c1_lbl, concept2=c2_lbl, steps_str=steps_str)
            else:
                key = "relation_path_none"
                template = self.get_template(key, language, self.get_fallback_template(key, language))
                ans = template
            return prefix + ans
 
        # 16. Describe Response
        elif type_ == "describe":
            concept_label = res.get("concept_label", self.get_concept_label(res.get("concept", ""), language))
            category = res.get("category", "")
            relations = res.get("relations", [])
            
            parts = []
            if category:
                template_cat = self.get_template("describe_category", language, self.get_fallback_template("describe_category", language))
                parts.append(template_cat.format(concept_label=concept_label, category=category))
            else:
                parts.append(concept_label)
            
            # De-duplicate outgoing relations
            seen_out = set()
            unique_outgoing = []
            for r in relations:
                if "target_label" in r:
                    key = (r.get("relation"), r.get("target"))
                    if key not in seen_out:
                        seen_out.add(key)
                        unique_outgoing.append(r)
            
            # De-duplicate incoming relations
            seen_in = set()
            unique_incoming = []
            for r in relations:
                if "source_label" in r:
                    key = (r.get("source"), r.get("relation"))
                    if key not in seen_in:
                        seen_in.add(key)
                        unique_incoming.append(r)
            
            mapped_rel_map = self.get_template("describe_rel_map", language, self.get_fallback_template("describe_rel_map", language))
            if not isinstance(mapped_rel_map, dict):
                mapped_rel_map = {}
            
            for r in unique_outgoing[:5]:
                rel_display = mapped_rel_map.get(r.get("relation"), r.get("relation_display", r.get("relation", "")))
                parts.append(f"{rel_display} {r['target_label']}")
            
            for r in unique_incoming[:3]:
                rel_display = mapped_rel_map.get(r.get("relation"), r.get("relation", ""))
                parts.append(f"{r['source_label']} {rel_display} {concept_label}")
            
            sep = self.get_template("describe_separator", language, self.get_fallback_template("describe_separator", language))
            body = sep.join(parts)
            return prefix + body + "."
 
        # 17. Knowledge Response
        elif type_ == "knowledge":
            concept_label = res.get("concept_label", self.get_concept_label(res.get("concept", ""), language))
            outgoing = res.get("outgoing", [])
            incoming = res.get("incoming", [])
            
            template_header = self.get_template("knowledge_header", language, self.get_fallback_template("knowledge_header", language))
            parts = [template_header.format(concept_label=concept_label)]
            
            # De-duplicate outgoing
            seen_out = set()
            unique_outgoing = []
            for r in outgoing:
                key = (r.get("relation"), r.get("target"))
                if key not in seen_out:
                    seen_out.add(key)
                    unique_outgoing.append(r)
            
            # De-duplicate incoming
            seen_in = set()
            unique_incoming = []
            for r in incoming:
                key = (r.get("source"), r.get("relation"))
                if key not in seen_in:
                    seen_in.add(key)
                    unique_incoming.append(r)
            
            for r in unique_outgoing[:5]:
                parts.append(f"{concept_label} {r.get('relation', '')} {r.get('target_label', r.get('target', ''))}")
            
            for r in unique_incoming[:3]:
                parts.append(f"{r.get('source_label', r.get('source', ''))} {r.get('relation', '')} {concept_label}")
            
            sep = self.get_template("knowledge_separator", language, self.get_fallback_template("knowledge_separator", language))
            body = sep.join(parts)
            return prefix + body + "."
            
        # 18. Honest Fail-safe
        else:
            template = self.get_template("unknown", language, self.get_fallback_template("unknown", language))
            return prefix + template
