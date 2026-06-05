import os
import json
import datetime

class DbIoHandler:
    def __init__(self, graph_handler):
        self.gh = graph_handler

    def load_databases(self, ontology_path, facts_path, language_rules_path, inference_rules_path=None):
        self.gh.ontology_path = ontology_path
        self.gh.facts_path = facts_path
        self.gh.language_rules_path = language_rules_path
        self.gh.inference_rules_path = inference_rules_path
        
        # Close old database if exists
        if hasattr(self.gh, "graph") and hasattr(self.gh.graph, "close"):
            self.gh.graph.close()
            
        from src.persistence.graph_database import GraphDatabaseSQLite
        db_path = ontology_path.replace('.json', '.db')
        self.gh.graph = GraphDatabaseSQLite(db_path)
        self.gh.graph.clear()
        
        # 1. Load Language Rules
        with open(language_rules_path, 'r', encoding='utf-8') as f:
            self.gh.language_rules = json.load(f)
            
        # 1.5 Load Inference Rules
        self.gh.inference_rules = []
        if inference_rules_path is None:
            inference_rules_path = os.path.join(os.path.dirname(ontology_path), "inference_rules.json")
        if os.path.exists(inference_rules_path):
            with open(inference_rules_path, 'r', encoding='utf-8') as f:
                rules_db = json.load(f)
                self.gh.inference_rules = rules_db.get("rules", [])
        else:
            self.gh.inference_rules = []
            
        # 2. Load Ontology (Concepts & Relations)
        with open(ontology_path, 'r', encoding='utf-8') as f:
            ontology = json.load(f)
            # Populate concepts as nodes
            for concept in ontology.get("concepts", []):
                self.gh.graph.add_node(
                    concept["id"],
                    labels=concept.get("labels", []),
                    category=concept.get("category", ""),
                    type="concept"
                )
            # Populate relations as directed edges
            for rel in ontology.get("relations", []):
                self.gh.graph.add_edge(
                    rel["from"],
                    rel["to"],
                    relation=rel["relation"],
                    causal_purpose=rel.get("causal_purpose", None),
                    type="relation"
                )
            # Store inference rules in graph attributes
            self.gh.graph.graph["inference_rules"] = ontology.get("inference_rules", [])

        # 3. Load Facts & Personas
        with open(facts_path, 'r', encoding='utf-8') as f:
            facts_db = json.load(f)
            self.gh.facts = facts_db.get("facts", [])
            self.gh.personas = facts_db.get("personas", [])
            
            # Load facts into graph under specific worlds
            for fact in self.gh.facts:
                self.gh.graph.add_edge(
                    fact["subject"],
                    fact["object"],
                    relation=fact["predicate"],
                    world=fact["world"],
                    confidence=fact.get("confidence", 1.0),
                    type="fact",
                    reason=fact.get("reason", None),
                    timestamp=fact.get("timestamp", datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")),
                    source="database",
                    status="active",
                    update_history=[]
                )

    def save_databases(self, ontology_path=None, facts_path=None):
        if ontology_path is None:
            ontology_path = getattr(self.gh, "ontology_path", "data/ontology.json")
        if facts_path is None:
            facts_path = getattr(self.gh, "facts_path", "data/facts.json")

        # 1. Prepare Ontology Structure
        concepts = []
        for node, data in self.gh.graph.nodes(data=True):
            if data.get("type") == "concept":
                concepts.append({
                    "id": node,
                    "labels": data.get("labels", []),
                    "category": data.get("category", "")
                })

        relations = []
        for u, v, data in self.gh.graph.edges(data=True):
            if data.get("type") == "relation":
                relations.append({
                    "from": u,
                    "to": v,
                    "relation": data.get("relation"),
                    "causal_purpose": data.get("causal_purpose", None)
                })

        ontology_data = {
            "concepts": concepts,
            "relations": relations,
            "inference_rules": self.gh.graph.graph.get("inference_rules", [])
        }

        # 2. Prepare Facts Structure
        facts = []
        for u, v, data in self.gh.graph.edges(data=True):
            if data.get("type") == "fact":
                fact_entry = {
                    "subject": u,
                    "predicate": data.get("relation"),
                    "object": v,
                    "world": data.get("world", "reality"),
                    "confidence": data.get("confidence", 1.0)
                }
                if data.get("reason"):
                    fact_entry["reason"] = data["reason"]
                if data.get("modality"):
                    fact_entry["modality"] = data["modality"]
                facts.append(fact_entry)

        facts_data = {
            "facts": facts,
            "personas": self.gh.personas
        }

        # Write to files
        with open(ontology_path, 'w', encoding='utf-8') as f:
            json.dump(ontology_data, f, ensure_ascii=False, indent=2)

        with open(facts_path, 'w', encoding='utf-8') as f:
            json.dump(facts_data, f, ensure_ascii=False, indent=2)

    def import_json_data(self, data):
        stats = {
            "concepts_added": 0,
            "relations_added": 0,
            "inference_rules_added": 0,
            "facts_added": 0,
            "personas_added": 0,
            "language_rules_updated": False,
            "other_files_updated": []
        }
        
        def save_helper(filename, dict_data):
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(base_dir, "data", filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(dict_data, f, ensure_ascii=False, indent=2)
                stats["other_files_updated"].append(filename)
            except Exception as e:
                print(f"Error saving to {filename}: {e}")

        # 1. Check for ontology / concepts
        if "concepts" in data:
            for concept in data["concepts"]:
                c_id = concept.get("id")
                if c_id:
                    labels = concept.get("labels", [c_id])
                    category = concept.get("category", "")
                    if not self.gh.graph.has_node(c_id):
                        self.gh.graph.add_node(c_id, labels=labels, category=category, type="concept")
                        stats["concepts_added"] += 1
                    else:
                        existing_labels = set(self.gh.graph.nodes[c_id].get("labels", []))
                        existing_labels.update(labels)
                        self.gh.graph.nodes[c_id]["labels"] = list(existing_labels)
                        if category:
                            self.gh.graph.nodes[c_id]["category"] = category

        # 2. Check for ontology / relations
        if "relations" in data and isinstance(data["relations"], list):
            for rel in data["relations"]:
                u = rel.get("from")
                v = rel.get("to")
                rel_type = rel.get("relation")
                if u and v and rel_type:
                    exists = False
                    if self.gh.graph.has_edge(u, v):
                        for key, edata in self.gh.graph[u][v].items():
                            if edata.get("type") == "relation" and edata.get("relation") == rel_type:
                                exists = True
                                break
                    if not exists:
                        self.gh.graph.add_edge(
                            u, v, relation=rel_type,
                            causal_purpose=rel.get("causal_purpose"),
                            type="relation"
                        )
                        stats["relations_added"] += 1

        # 2b. Check for relations_metadata
        if "relations_metadata" in data and isinstance(data["relations_metadata"], list):
            try:
                meta_path = os.path.join(os.path.dirname(self.gh.ontology_path), "relations_metadata.json")
                current_meta = {"relations": []}
                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        current_meta = json.load(f)
                existing_ids = {r["id"]: i for i, r in enumerate(current_meta.get("relations", []))}
                for r in data["relations_metadata"]:
                    r_id = r.get("id")
                    if r_id:
                        if r_id in existing_ids:
                            current_meta["relations"][existing_ids[r_id]].update(r)
                        else:
                            current_meta["relations"].append(r)
                save_helper("relations_metadata.json", current_meta)
            except Exception as e:
                print(f"Error merging relations metadata: {e}")

        # 3. Check for ontology / inference_rules
        if "inference_rules" in data:
            current_rules = self.gh.graph.graph.get("inference_rules", [])
            existing_rule_ids = {rule.get("id") for rule in current_rules if rule.get("id")}
            for rule in data["inference_rules"]:
                rule_id = rule.get("id")
                if rule_id and rule_id not in existing_rule_ids:
                    current_rules.append(rule)
                    stats["inference_rules_added"] += 1
            self.gh.graph.graph["inference_rules"] = current_rules

        # 4. Check for dynamic rules (inference_rules.json)
        if "rules" in data:
            try:
                rules_path = os.path.join(os.path.dirname(self.gh.ontology_path), "inference_rules.json")
                current_rules = {"rules": []}
                if os.path.exists(rules_path):
                    with open(rules_path, 'r', encoding='utf-8') as f:
                        current_rules = json.load(f)
                existing_ids = {r["id"] for r in current_rules.get("rules", []) if r.get("id")}
                for r in data["rules"]:
                    r_id = r.get("id")
                    if r_id and r_id not in existing_ids:
                        current_rules["rules"].append(r)
                        stats["inference_rules_added"] += 1
                save_helper("inference_rules.json", current_rules)
                self.gh.inference_rules = current_rules.get("rules", [])
            except Exception as e:
                print(f"Error merging dynamic inference rules: {e}")

        # 5. Check for facts
        if "facts" in data:
            for fact in data["facts"]:
                subj = fact.get("subject")
                obj = fact.get("object")
                pred = fact.get("predicate")
                if subj and obj and pred:
                    if not self.gh.graph.has_node(subj):
                        self.gh.graph.add_node(subj, labels=[subj], category="user_defined", type="concept")
                    if not self.gh.graph.has_node(obj):
                        self.gh.graph.add_node(obj, labels=[obj], category="user_defined", type="concept")
                        
                    res = self.gh.add_or_update_fact(
                        subj, obj, relation=pred,
                        world=fact.get("world", "reality"),
                        confidence=float(fact.get("confidence", 1.0)),
                        reason=fact.get("reason"),
                        modality=fact.get("modality"),
                        interactive=False
                    )
                    if res.get("success"):
                        stats["facts_added"] += 1

        # 6. Check for personas
        if "personas" in data:
            existing_persona_ids = {p["id"] for p in self.gh.personas if "id" in p}
            for persona in data["personas"]:
                p_id = persona.get("id")
                if p_id and p_id not in existing_persona_ids:
                    self.gh.personas.append(persona)
                    stats["personas_added"] += 1

        # 7. Check for language_rules components
        has_lang_rules = any(k in data for k in ["morphology", "grammar", "en", "fr", "ar"])
        if has_lang_rules:
            for k in ["morphology", "grammar", "en", "fr", "ar"]:
                if k in data:
                    if k in ["morphology", "grammar"]:
                        if k not in self.gh.language_rules:
                            self.gh.language_rules[k] = {}
                        if isinstance(data[k], dict):
                            for subk, subv in data[k].items():
                                if isinstance(subv, list):
                                    if subk not in self.gh.language_rules[k]:
                                        self.gh.language_rules[k][subk] = []
                                    self.gh.language_rules[k][subk].extend(subv)
                                elif isinstance(subv, dict):
                                    if subk not in self.gh.language_rules[k]:
                                        self.gh.language_rules[k][subk] = {}
                                    self.gh.language_rules[k][subk].update(subv)
                                else:
                                    self.gh.language_rules[k][subk] = subv
                    else:
                        if k not in self.gh.language_rules:
                            self.gh.language_rules[k] = {}
                        if isinstance(data[k], dict):
                            for subk, subv in data[k].items():
                                if subk not in self.gh.language_rules[k]:
                                    self.gh.language_rules[k][subk] = {}
                                if isinstance(subv, dict):
                                    self.gh.language_rules[k][subk].update(subv)
                                elif isinstance(subv, list):
                                    if not isinstance(self.gh.language_rules[k][subk], list):
                                        self.gh.language_rules[k][subk] = []
                                    self.gh.language_rules[k][subk].extend(subv)
            
            try:
                with open(self.gh.language_rules_path, 'w', encoding='utf-8') as f:
                    json.dump(self.gh.language_rules, f, ensure_ascii=False, indent=2)
                stats["language_rules_updated"] = True
            except Exception as e:
                print(f"Error saving language rules: {e}")

        # 8. Check for other schema files
        if "weights" in data or "keywords" in data:
            try:
                mod_path = os.path.join(os.path.dirname(self.gh.ontology_path), "modalities.json")
                current_mods = {}
                if os.path.exists(mod_path):
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        current_mods = json.load(f)
                if "weights" in data:
                    if "weights" not in current_mods:
                        current_mods["weights"] = {}
                    current_mods["weights"].update(data["weights"])
                if "keywords" in data:
                    if "keywords" not in current_mods:
                        current_mods["keywords"] = {}
                    for lang, kmaps in data["keywords"].items():
                        if lang not in current_mods["keywords"]:
                            current_mods["keywords"][lang] = {}
                        current_mods["keywords"][lang].update(kmaps)
                save_helper("modalities.json", current_mods)
            except Exception as e:
                print(f"Error merging modalities: {e}")
                
        if "modalities" in data and isinstance(data["modalities"], dict):
            try:
                mod_path = os.path.join(os.path.dirname(self.gh.ontology_path), "modalities.json")
                current_mods = {}
                if os.path.exists(mod_path):
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        current_mods = json.load(f)
                if "logical_modalities" not in current_mods:
                    current_mods["logical_modalities"] = {}
                current_mods["logical_modalities"].update(data["modalities"])
                save_helper("modalities.json", current_mods)
            except Exception as e:
                print(f"Error merging modality description: {e}")

        if "semantic_frames" in data:
            try:
                sem_path = os.path.join(os.path.dirname(self.gh.ontology_path), "semantic_roles.json")
                current_sems = {"version": "1.0", "semantic_frames": {}}
                if os.path.exists(sem_path):
                    with open(sem_path, 'r', encoding='utf-8') as f:
                        current_sems = json.load(f)
                current_sems["semantic_frames"].update(data["semantic_frames"])
                save_helper("semantic_roles.json", current_sems)
            except Exception as e:
                print(f"Error merging semantic frames: {e}")

        if "temporal_relations" in data or "temporal_markers" in data or "temporal_facts" in data:
            try:
                temp_path = os.path.join(os.path.dirname(self.gh.ontology_path), "temporal_logic.json")
                current_temp = {"version": "1.0", "temporal_relations": {}, "temporal_markers": {}, "temporal_facts": []}
                if os.path.exists(temp_path):
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        current_temp = json.load(f)
                if "temporal_relations" in data:
                    current_temp["temporal_relations"].update(data["temporal_relations"])
                if "temporal_markers" in data:
                    current_temp["temporal_markers"].update(data["temporal_markers"])
                if "temporal_facts" in data:
                    current_temp["temporal_facts"].extend(data["temporal_facts"])
                save_helper("temporal_logic.json", current_temp)
            except Exception as e:
                print(f"Error merging temporal logic: {e}")

        if "causal_chains" in data or "causal_rules" in data:
            try:
                causal_path = os.path.join(os.path.dirname(self.gh.ontology_path), "causal_chains.json")
                current_causal = {"version": "1.0", "causal_chains": [], "causal_rules": []}
                if os.path.exists(causal_path):
                    with open(causal_path, 'r', encoding='utf-8') as f:
                        current_causal = json.load(f)
                if "causal_chains" in data:
                    current_causal["causal_chains"].extend(data["causal_chains"])
                if "causal_rules" in data:
                    current_causal["causal_rules"].extend(data["causal_rules"])
                save_helper("causal_chains.json", current_causal)
            except Exception as e:
                print(f"Error merging causal chains: {e}")

        if "negation_rules" in data or "negation_markers" in data or "polarities" in data:
            try:
                neg_path = os.path.join(os.path.dirname(self.gh.ontology_path), "negation_rules.json")
                current_neg = {"version": "1.0", "negation_rules": [], "negation_markers": {}, "polarities": []}
                if os.path.exists(neg_path):
                    with open(neg_path, 'r', encoding='utf-8') as f:
                        current_neg = json.load(f)
                if "negation_rules" in data:
                    current_neg["negation_rules"].extend(data["negation_rules"])
                if "negation_markers" in data:
                    current_neg["negation_markers"].update(data["negation_markers"])
                if "polarities" in data:
                    current_neg["polarities"].extend(data["polarities"])
                save_helper("negation_rules.json", current_neg)
            except Exception as e:
                print(f"Error merging negation rules: {e}")

        if "quantifiers" in data or "quantifier_inferences" in data:
            try:
                quant_path = os.path.join(os.path.dirname(self.gh.ontology_path), "quantifiers.json")
                current_quant = {"version": "1.0", "quantifiers": [], "quantifier_inferences": []}
                if os.path.exists(quant_path):
                    with open(quant_path, 'r', encoding='utf-8') as f:
                        current_quant = json.load(f)
                if "quantifiers" in data:
                    current_quant["quantifiers"].extend(data["quantifiers"])
                if "quantifier_inferences" in data:
                    current_quant["quantifier_inferences"].extend(data["quantifier_inferences"])
                save_helper("quantifiers.json", current_quant)
            except Exception as e:
                print(f"Error merging quantifiers: {e}")

        if "entailments" in data or "contradiction_detection" in data:
            try:
                ent_path = os.path.join(os.path.dirname(self.gh.ontology_path), "entailment.json")
                current_ent = {"version": "1.0", "entailments": [], "contradiction_detection": []}
                if os.path.exists(ent_path):
                    with open(ent_path, 'r', encoding='utf-8') as f:
                        current_ent = json.load(f)
                if "entailments" in data:
                    current_ent["entailments"].extend(data["entailments"])
                if "contradiction_detection" in data:
                    current_ent["contradiction_detection"].extend(data["contradiction_detection"])
                save_helper("entailment.json", current_ent)
            except Exception as e:
                print(f"Error merging entailments: {e}")

        if "pragmatic_facts" in data or "contextual_rules" in data:
            try:
                prag_path = os.path.join(os.path.dirname(self.gh.ontology_path), "pragmatic_knowledge.json")
                current_prag = {"version": "1.0", "pragmatic_facts": [], "contextual_rules": []}
                if os.path.exists(prag_path):
                    with open(prag_path, 'r', encoding='utf-8') as f:
                        current_prag = json.load(f)
                if "pragmatic_facts" in data:
                    current_prag["pragmatic_facts"].extend(data["pragmatic_facts"])
                if "contextual_rules" in data:
                    current_prag["contextual_rules"].extend(data["contextual_rules"])
                save_helper("pragmatic_knowledge.json", current_prag)
            except Exception as e:
                print(f"Error merging pragmatic knowledge: {e}")

        if "exceptions" in data or "anomaly_patterns" in data:
            try:
                anomaly_path = os.path.join(os.path.dirname(self.gh.ontology_path), "anomaly_detection.json")
                current_anomaly = {"version": "1.0", "exceptions": [], "anomaly_patterns": []}
                if os.path.exists(anomaly_path):
                    with open(anomaly_path, 'r', encoding='utf-8') as f:
                        current_anomaly = json.load(f)
                if "exceptions" in data:
                    current_anomaly["exceptions"].extend(data["exceptions"])
                if "anomaly_patterns" in data:
                    current_anomaly["anomaly_patterns"].extend(data["anomaly_patterns"])
                save_helper("anomaly_detection.json", current_anomaly)
            except Exception as e:
                print(f"Error merging anomaly detection exceptions: {e}")

        if "comparative_properties" in data or "comparison_rules" in data:
            try:
                comp_path = os.path.join(os.path.dirname(self.gh.ontology_path), "comparison.json")
                current_comp = {"version": "1.0", "comparative_properties": {}, "comparison_rules": []}
                if os.path.exists(comp_path):
                    with open(comp_path, 'r', encoding='utf-8') as f:
                        current_comp = json.load(f)
                if "comparative_properties" in data:
                    for prop, pdata in data["comparative_properties"].items():
                        if prop not in current_comp["comparative_properties"]:
                            current_comp["comparative_properties"][prop] = {"scale": []}
                        if "scale" in pdata:
                            current_comp["comparative_properties"][prop]["scale"].extend(pdata["scale"])
                if "comparison_rules" in data:
                    current_comp["comparison_rules"].extend(data["comparison_rules"])
                save_helper("comparison.json", current_comp)
            except Exception as e:
                print(f"Error merging comparison scales: {e}")

        self.save_databases(self.gh.ontology_path, self.gh.facts_path)
        self.gh.infer_facts(self.gh.active_world)
        
        return stats
