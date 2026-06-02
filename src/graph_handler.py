import os
import json
import networkx as nx

class GraphHandler:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.language_rules = {}
        self.facts = []
        self.personas = []
        self.active_world = "reality"

    def load_databases(self, ontology_path, facts_path, language_rules_path, inference_rules_path=None):
        """Loads and parses JSON databases, populating the NetworkX graph and dynamic rules."""
        # 1. Load Language Rules
        with open(language_rules_path, 'r', encoding='utf-8') as f:
            self.language_rules = json.load(f)
            
        # 1.5 Load Inference Rules
        self.inference_rules = []
        if inference_rules_path is None:
            inference_rules_path = os.path.join(os.path.dirname(ontology_path), "inference_rules.json")
        if os.path.exists(inference_rules_path):
            with open(inference_rules_path, 'r', encoding='utf-8') as f:
                rules_db = json.load(f)
                self.inference_rules = rules_db.get("rules", [])
        else:
            self.inference_rules = []
            
        # 2. Load Ontology (Concepts & Relations)
        with open(ontology_path, 'r', encoding='utf-8') as f:
            ontology = json.load(f)
            # Populate concepts as nodes
            for concept in ontology.get("concepts", []):
                self.graph.add_node(
                    concept["id"],
                    labels=concept.get("labels", []),
                    category=concept.get("category", ""),
                    type="concept"
                )
            # Populate relations as directed edges
            for rel in ontology.get("relations", []):
                self.graph.add_edge(
                    rel["from"],
                    rel["to"],
                    relation=rel["relation"],
                    causal_purpose=rel.get("causal_purpose", None),
                    type="relation"
                )
            # Store inference rules in graph attributes
            self.graph.graph["inference_rules"] = ontology.get("inference_rules", [])

        # 3. Load Facts & Personas
        with open(facts_path, 'r', encoding='utf-8') as f:
            facts_db = json.load(f)
            self.facts = facts_db.get("facts", [])
            self.personas = facts_db.get("personas", [])
            
            # Load facts into graph under specific worlds
            for fact in self.facts:
                # Add edge to represent the fact
                self.graph.add_edge(
                    fact["subject"],
                    fact["object"],
                    relation=fact["predicate"],
                    world=fact["world"],
                    confidence=fact.get("confidence", 1.0),
                    type="fact",
                    reason=fact.get("reason", None),
                    timestamp="2026-06-02T00:00:00Z",
                    source="database",
                    status="active",
                    update_history=[]
                )

    def add_or_update_fact(self, subj, obj, relation, world, confidence=1.0, reason=None, interactive=False):
        """
        Adds a new fact edge, or resolves conflicts if a fact already exists for (subj, relation, world)
        or if opposite properties are taught (e.g. thin_fur vs thick_fur).
        """
        import datetime
        timestamp = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")
        
        # 1. Identify opposite properties
        OPPOSITE_PROPERTIES = {
            ("thin_fur", "thick_fur"),
            ("thick_fur", "thin_fur"),
        }
        
        # 2. Get existing facts of type 'fact' for this subject in the target world
        existing_edges = []
        if self.graph.has_node(subj):
            for u, v, key, data in list(self.graph.out_edges(subj, data=True, keys=True)):
                if data.get("type") == "fact" and data.get("world") == world:
                    # Check if it's the same relation
                    if data.get("relation") == relation:
                        existing_edges.append((u, v, key, data))
                    # Also check if it's has_property and we have conflicting property objects
                    elif relation == "has_property" and data.get("relation") == "has_property":
                        if (v, obj) in OPPOSITE_PROPERTIES or (obj, v) in OPPOSITE_PROPERTIES:
                            existing_edges.append((u, v, key, data))
                            
        # 3. If there are no existing conflicting facts, simply add the new fact
        if not existing_edges:
            self.graph.add_edge(
                subj,
                obj,
                relation=relation,
                world=world,
                confidence=confidence,
                type="fact",
                reason=reason,
                timestamp=timestamp,
                source="user_interactive" if interactive else "automated",
                status="active",
                update_history=[]
            )
            subj_lbl = self.graph.nodes[subj].get("labels", [subj])[0]
            obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
            return {
                "success": True,
                "status": "added",
                "message": f"تم حفظ الحقيقة الجديدة: [{subj_lbl}] --({relation})--> [{obj_lbl}] في عالم '{world}'"
            }
            
        # 4. We found one or more existing/conflicting edges. Let's process the first one.
        u, v, key, data = existing_edges[0]
        
        # Check if identical (same relation and same object)
        is_identical = (data.get("relation") == relation and v == obj)
        
        if is_identical:
            # Update attributes of the existing edge
            data["confidence"] = confidence
            data["reason"] = reason or data.get("reason")
            data["timestamp"] = timestamp
            data["source"] = "user_interactive" if interactive else data.get("source", "database")
            
            subj_lbl = self.graph.nodes[subj].get("labels", [subj])[0]
            obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
            return {
                "success": True,
                "status": "identical",
                "message": f"المعلومة [{subj_lbl}] --({relation})--> [{obj_lbl}] موجودة بالفعل في عالم '{world}' (تم تحديث الثقة لـ {confidence})."
            }
            
        # Contradiction detected! (v != obj for a functional relation, or opposite properties)
        old_conf = data.get("confidence", 1.0)
        
        # Tier 1: Auto-Resolution based on confidence difference
        if confidence > old_conf + 0.3:
            # Auto-replace
            history_entry = {
                "old_object": v,
                "old_relation": data.get("relation"),
                "old_confidence": old_conf,
                "old_reason": data.get("reason"),
                "timestamp": data.get("timestamp"),
                "source": data.get("source"),
                "resolution": "auto_replaced_higher_confidence"
            }
            new_history = data.get("update_history", []) + [history_entry]
            
            # Remove old edge
            self.graph.remove_edge(u, v, key=key)
            # Add new edge
            self.graph.add_edge(
                subj,
                obj,
                relation=relation,
                world=world,
                confidence=confidence,
                type="fact",
                reason=reason,
                timestamp=timestamp,
                source="user_interactive" if interactive else "automated",
                status="active",
                update_history=new_history
            )
            
            subj_lbl = self.graph.nodes[subj].get("labels", [subj])[0]
            old_obj_lbl = self.graph.nodes[v].get("labels", [v])[0]
            new_obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
            return {
                "success": True,
                "status": "auto_replaced",
                "message": f"⚠️ تم تحديث الحقيقة تلقائياً لـ [{subj_lbl}] من [{old_obj_lbl}] إلى [{new_obj_lbl}] لأن ثقة المعلومة الجديدة أعلى بكثير ({confidence} مقابل {old_conf})."
            }
            
        elif confidence < old_conf - 0.3:
            # Auto-reject
            subj_lbl = self.graph.nodes[subj].get("labels", [subj])[0]
            old_obj_lbl = self.graph.nodes[v].get("labels", [v])[0]
            new_obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
            return {
                "success": True,
                "status": "auto_rejected",
                "message": f"⚠️ تم رفض الحقيقة الجديدة تلقائياً [{subj_lbl}] --({relation})--> [{new_obj_lbl}] لأن ثقة المعلومة الحالية أعلى بكثير ({old_conf} مقابل {confidence})."
            }
            
        # Tier 3: Interactive Confirmation or Fallback
        if interactive:
            # Ask the user in the CLI
            subj_lbl = self.graph.nodes[subj].get("labels", [subj])[0]
            old_obj_lbl = self.graph.nodes[v].get("labels", [v])[0]
            new_obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
            
            print(f"\n⚠️  [تعارض معلومات] الحقيقة الجديدة تتعارض مع حقيقة مسجلة في عالم '{world}'!")
            print(f"المعلومة الحالية: [{subj_lbl}] --({data.get('relation')})--> [{old_obj_lbl}] (ثقة: {old_conf})")
            print(f"المعلومة الجديدة: [{subj_lbl}] --({relation})--> [{new_obj_lbl}] (ثقة: {confidence})")
            print("-" * 50)
            print("الرجاء اختيار خيار الحل:")
            print(" 1. استبدال (احذف المعلومة القديمة واحفظ الجديدة مع تسجيل السابقة في الأرشيف)")
            print(" 2. دمج (احفظ المعلومة الجديدة إلى جانب القديمة)")
            print(" 3. تجاهل (ألغِ الإضافة الجديدة واحتفظ بالقديمة فقط)")
            
            choice = ""
            while choice not in ["1", "2", "3"]:
                choice = input("اختر رقم الحل (1-3): ").strip()
                
            if choice == "1":
                # Replace
                history_entry = {
                    "old_object": v,
                    "old_relation": data.get("relation"),
                    "old_confidence": old_conf,
                    "old_reason": data.get("reason"),
                    "timestamp": data.get("timestamp"),
                    "source": data.get("source"),
                    "resolution": "user_replaced"
                }
                new_history = data.get("update_history", []) + [history_entry]
                
                self.graph.remove_edge(u, v, key=key)
                self.graph.add_edge(
                    subj,
                    obj,
                    relation=relation,
                    world=world,
                    confidence=confidence,
                    type="fact",
                    reason=reason,
                    timestamp=timestamp,
                    source="user_interactive",
                    status="active",
                    update_history=new_history
                )
                return {
                    "success": True,
                    "status": "replaced",
                    "message": f"تم استبدال المعلومة القديمة [{old_obj_lbl}] بالجديدة [{new_obj_lbl}] بناءً على اختيارك."
                }
            elif choice == "2":
                # Add both (Merge)
                self.graph.add_edge(
                    subj,
                    obj,
                    relation=relation,
                    world=world,
                    confidence=confidence,
                    type="fact",
                    reason=reason,
                    timestamp=timestamp,
                    source="user_interactive",
                    status="active",
                    update_history=[]
                )
                return {
                    "success": True,
                    "status": "merged",
                    "message": f"تم دمج المعلومتين معاً (أصبحت كل من [{old_obj_lbl}] و [{new_obj_lbl}] مسجلة لـ [{subj_lbl}])."
                }
            else:
                # Cancel/Ignore
                return {
                    "success": True,
                    "status": "ignored",
                    "message": f"تم تجاهل المعلومة الجديدة والاحتفاظ بـ [{old_obj_lbl}] بناءً على اختيارك."
                }
        else:
            # Fallback for non-interactive (tests): reject/keep old
            subj_lbl = self.graph.nodes[subj].get("labels", [subj])[0]
            old_obj_lbl = self.graph.nodes[v].get("labels", [v])[0]
            new_obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
            return {
                "success": True,
                "status": "non_interactive_rejected",
                "message": f"⚠️ تم تجاهل الحقيقة الجديدة [{subj_lbl}] --({relation})--> [{new_obj_lbl}] في عالم '{world}' افتراضياً لعدم وجود تفاعل بشري."
            }

    def set_active_world(self, world_name):
        self.active_world = world_name

    def get_parent(self, concept_id, relation="is_a"):
        """Traverses the graph to find the target concept matching the relation."""
        if not self.graph.has_node(concept_id):
            return None
        # Look for edges starting from concept_id with relation
        for _, to_node, data in self.graph.out_edges(concept_id, data=True):
            if data.get("relation") == relation:
                return to_node
        return None

    def get_properties(self, concept_id, world=None):
        """Returns physical and functional properties of a concept in the active or specified world."""
        properties = []
        if not self.graph.has_node(concept_id):
            return properties
            
        world = world or self.active_world
        
        # Look at relations in ontology
        for _, to_node, data in self.graph.out_edges(concept_id, data=True):
            if data.get("type") == "relation" and data.get("relation") in ["has_property", "lives_in"]:
                properties.append({
                    "property": to_node,
                    "relation": data.get("relation"),
                    "causal_purpose": data.get("causal_purpose")
                })
                
        # Look at facts matching the world
        for _, to_node, data in self.graph.out_edges(concept_id, data=True):
            if data.get("type") == "fact" and data.get("world") == world:
                if data.get("status", "active") == "active":
                    properties.append({
                        "property": to_node,
                        "relation": data.get("relation"),
                        "reason": data.get("reason")
                    })
        return properties

    def get_requirements(self, environment_id):
        """Returns the dynamic requirements of an environment (e.g. extreme_cold requires good_insulation)."""
        requirements = []
        if not self.graph.has_node(environment_id):
            return requirements
            
        # Get environment attributes (like arctic has extreme_cold)
        conditions = []
        for _, to_node, data in self.graph.out_edges(environment_id, data=True):
            if data.get("relation") in ["has_environment", "has_property"]:
                conditions.append(to_node)
                
        # Get requirements for those conditions (e.g., extreme_cold requires good_insulation)
        for cond in conditions:
            if self.graph.has_node(cond):
                for _, to_node, data in self.graph.out_edges(cond, data=True):
                    if data.get("relation") == "requires":
                        requirements.append({
                            "condition": cond,
                            "requirement": to_node
                        })
        return requirements

    def calculate_similarity(self, concept1, concept2):
        """Calculates taxonomy-based similarity by sharing parent categories in is_a hierarchy."""
        if not (self.graph.has_node(concept1) and self.graph.has_node(concept2)):
            return 0.0
            
        # Get ancestors for concept 1
        ancestors1 = set()
        curr = concept1
        while curr:
            curr = self.get_parent(curr, "is_a")
            if curr:
                ancestors1.add(curr)
                
        # Get ancestors for concept 2
        ancestors2 = set()
        curr = concept2
        while curr:
            curr = self.get_parent(curr, "is_a")
            if curr:
                ancestors2.add(curr)
                
        # Jaccard similarity of ancestors
        intersection = ancestors1.intersection(ancestors2)
        union = ancestors1.union(ancestors2)
        
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def spreading_activation(self, source_concepts, max_steps=2, decay=0.5, threshold=0.1):
        """
        Runs a Spreading Activation algorithm on the NetworkX graph.
        Starts with a dict of {concept_id: activation_value}.
        Spreads activation to neighbors, scaled by decay and edge confidence.
        Returns a dict of final concept activations: {concept_id: activation}.
        """
        if not source_concepts:
            return {}
            
        # Initialize activation levels
        activations = {c: 1.0 for c in source_concepts if self.graph.has_node(c)}
        
        for step in range(max_steps):
            new_activations = {}
            for node, val in activations.items():
                if val < threshold:
                    continue
                # Find all neighbors (incoming and outgoing edges)
                neighbors = []
                # Out edges
                if self.graph.has_node(node):
                    for _, target, data in self.graph.out_edges(node, data=True):
                        # We can weigh the link
                        weight = data.get("confidence", 1.0)
                        neighbors.append((target, weight))
                    # In edges (back-propagation)
                    for source, _, data in self.graph.in_edges(node, data=True):
                        weight = data.get("confidence", 1.0) * 0.7 # slightly less weight back-propagation
                        neighbors.append((source, weight))
                    
                if not neighbors:
                    # Keep activation if no neighbors
                    new_activations[node] = new_activations.get(node, 0.0) + val
                    continue
                    
                # Distribute activation to neighbors
                spread_val = (val * decay) / len(neighbors)
                # Node retains some activation
                new_activations[node] = new_activations.get(node, 0.0) + val * (1.0 - decay)
                
                for neigh, weight in neighbors:
                    new_activations[neigh] = new_activations.get(neigh, 0.0) + spread_val * weight
                    
            # Normalize or threshold new activations
            activations = new_activations
            
        return activations

    def dynamic_morphological_lookup(self, word, language="ar", context_concepts=None):
        """
        Dynamic morphological analyzer.
        Matches input words to concept IDs using rules loaded in self.language_rules.
        Supports Spreading Activation if multiple concepts match.
        """
        # Clean word of punctuation
        word = word.strip().replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "")
        
        matched_concepts = []

        if language in ["en", "fr"]:
            word = word.lower()
            # 1. Lookup in the language-specific lexicon
            lang_rules = self.language_rules.get(language, {})
            lexicon = lang_rules.get("lexicon", {})
            if word in lexicon:
                matched_concepts.append(lexicon[word])
                
            # 2. Direct lookup in node IDs (as fallback)
            for node in self.graph.nodes:
                if word == node.lower():
                    matched_concepts.append(node)
        else:
            # --- Arabic Morphological Lookup ---
            # Direct lookup in concept labels
            for node, data in self.graph.nodes(data=True):
                if data.get("type") == "concept":
                    if word in data.get("labels", []):
                        matched_concepts.append(node)
                        
            # Apply affix rules dynamically loaded from language_rules
            prefixes = [p["form"].replace("ـ", "") for p in self.language_rules.get("morphology", {}).get("particles", []) if p["type"] in ["definite_article", "preposition", "conjunction"]]
            suffixes = [s["form"].replace("ـ", "") for s in self.language_rules.get("morphology", {}).get("particles", []) if s["type"] in ["pronoun_suffix", "plural_suffix"]]
            
            # Iterative stripping of prefixes/suffixes to handle compound affixes like "بالقطب" (ب + ال + قطب)
            candidates = {word}
            
            # Try iterative prefix stripping
            changed = True
            while changed:
                changed = False
                new_candidates = set()
                for cand in candidates:
                    for pref in prefixes:
                        if cand.startswith(pref) and len(cand) > len(pref):
                            stem = cand[len(pref):]
                            if stem not in candidates:
                                new_candidates.add(stem)
                                changed = True
                candidates.update(new_candidates)
                
            # Try iterative suffix stripping
            changed = True
            while changed:
                changed = False
                new_candidates = set()
                for cand in candidates:
                    for suff in suffixes:
                        if cand.endswith(suff) and len(cand) > len(suff):
                            stem = cand[:-len(suff)]
                            if stem not in candidates:
                                new_candidates.add(stem)
                                changed = True
                candidates.update(new_candidates)
                
            # Check if any candidate is a concept label
            for stem in sorted(list(candidates), key=len):
                for node, data in self.graph.nodes(data=True):
                    if data.get("type") == "concept":
                        if stem in data.get("labels", []):
                            matched_concepts.append(node)
                            
            # Check dynamic lexicon roots
            for stem in sorted(list(candidates), key=len):
                for root in self.language_rules.get("morphology", {}).get("roots", []):
                    if stem in root["patterns"]:
                        for pat in root["patterns"]:
                            for node, data in self.graph.nodes(data=True):
                                if data.get("type") == "concept" and pat in data.get("labels", []):
                                    matched_concepts.append(node)
                                    
        # Resolve ambiguity using Spreading Activation if context is available
        if matched_concepts:
            # Deduplicate preserving order
            unique_matches = []
            for c in matched_concepts:
                if c not in unique_matches:
                    unique_matches.append(c)
            
            if len(unique_matches) > 1:
                if context_concepts:
                    activations = self.spreading_activation(context_concepts)
                    # Pick candidate with highest activation level
                    best_concept = max(unique_matches, key=lambda c: activations.get(c, 0.0))
                    # If we found a candidate with positive activation, return it
                    if activations.get(best_concept, 0.0) > 0.0:
                        return best_concept
                # Default fallback is the first match
                return unique_matches[0]
            return unique_matches[0]
            
        return None

    def find_bindings(self, active_world, conditions, index=0, current_bindings=None):
        """
        Recursively matches a list of query conditions with variables (e.g. ?x, ?y)
        against the graph's edges (ontology relations and active world facts).
        Returns a list of binding dictionaries, e.g. [{'?x': 'feline_carnivore', '?y': 'carnivore'}].
        """
        if current_bindings is None:
            current_bindings = {}
            
        if index >= len(conditions):
            return [current_bindings]
            
        cond = conditions[index]
        cond_sub = cond["subject"]
        cond_rel = cond["relation"]
        cond_obj = cond["object"]
        
        results = []
        
        # Iterate over all edges in the graph
        for u, v, data in self.graph.edges(data=True):
            # 1. Match relation
            if data.get("relation") != cond_rel:
                continue
                
            # 2. Match world
            edge_type = data.get("type", "relation")
            edge_world = data.get("world", "reality")
            
            # Facts and Inferred edges must match active_world. Ontology relations (type="relation") apply in all worlds.
            if edge_type in ["fact", "inferred"] and edge_world != active_world:
                continue
                
            # 3. Match subject
            new_bindings = current_bindings.copy()
            if cond_sub.startswith("?"):
                if cond_sub in new_bindings:
                    if new_bindings[cond_sub] != u:
                        continue
                else:
                    new_bindings[cond_sub] = u
            else:
                if cond_sub != u:
                    continue
                    
            # 4. Match object
            if cond_obj.startswith("?"):
                if cond_obj in new_bindings:
                    if new_bindings[cond_obj] != v:
                        continue
                else:
                    new_bindings[cond_obj] = v
            else:
                if cond_obj != v:
                    continue
                    
            # Match was successful, match next condition recursively
            sub_results = self.find_bindings(active_world, conditions, index + 1, new_bindings)
            results.extend(sub_results)
            
        return results

    def infer_facts(self, active_world, max_iterations=5):
        """
        Runs a Forward Chaining logic engine.
        Applies rules in self.inference_rules to derive new edges of type 'inferred'
        and stores them in the NetworkX graph.
        """
        # 1. Clear previous inferred edges for the active world to prevent duplicate build-up
        inferred_edges = [(u, v, k) for u, v, k, d in list(self.graph.edges(keys=True, data=True)) 
                          if d.get("type") == "inferred" and d.get("world") == active_world]
        self.graph.remove_edges_from(inferred_edges)
        
        iteration = 0
        while iteration < max_iterations:
            new_edges_added = False
            
            for rule in self.inference_rules:
                rule_id = rule["id"]
                conditions = rule["conditions"]
                conclusion_template = rule["conclusion"]
                
                # Find all satisfying variable bindings
                bindings_list = self.find_bindings(active_world, conditions)
                
                for binding in bindings_list:
                    # Construct conclusion
                    sub = binding.get(conclusion_template["subject"], conclusion_template["subject"])
                    obj = binding.get(conclusion_template["object"], conclusion_template["object"])
                    rel = conclusion_template["relation"]
                    
                    # Verify u and v exist as nodes in the graph
                    if not (self.graph.has_node(sub) and self.graph.has_node(obj)):
                        continue
                        
                    # Check if this edge already exists in the active world
                    exists = False
                    # Check ontology relations
                    for _, target, data in self.graph.out_edges(sub, data=True):
                        if target == obj and data.get("relation") == rel:
                            if data.get("type") == "relation":
                                exists = True
                                break
                            elif data.get("type") in ["fact", "inferred"] and data.get("world") == active_world:
                                exists = True
                                break
                                
                    if not exists:
                        # Find the matched edges to calculate minimum confidence
                        matched_confidences = []
                        
                        # Re-verify which edges matched
                        for cond in conditions:
                            c_sub = binding.get(cond["subject"], cond["subject"])
                            c_obj = binding.get(cond["object"], cond["object"])
                            c_rel = cond["relation"]
                            
                            # Find the edge confidence
                            for _, target, data in self.graph.out_edges(c_sub, data=True):
                                if target == c_obj and data.get("relation") == c_rel:
                                    matched_confidences.append(data.get("confidence", 1.0))
                                    break
                                    
                        conf = min(matched_confidences) if matched_confidences else 1.0
                        
                        # Construct a trace step description in Arabic
                        sub_lbl = self.graph.nodes[sub].get("labels", [sub])[0]
                        obj_lbl = self.graph.nodes[obj].get("labels", [obj])[0]
                        
                        if rule_id == "transitive_is_a":
                            y_node = binding["?y"]
                            y_lbl = self.graph.nodes[y_node].get("labels", [y_node])[0]
                            desc = f"{sub_lbl} هو {obj_lbl} (استنتاج بالتعدي التصنيفي: {sub_lbl} هو {y_lbl}، و {y_lbl} هو {obj_lbl})"
                        elif rule_id == "property_inheritance":
                            y_node = binding["?y"]
                            y_lbl = self.graph.nodes[y_node].get("labels", [y_node])[0]
                            desc = f"{sub_lbl} يرث خاصية [{obj_lbl}] تصاعدياً من فئته الأعلى {y_lbl}"
                        elif rule_id == "environment_requirement":
                            env_node = binding["?env"]
                            env_lbl = self.graph.nodes[env_node].get("labels", [env_node])[0]
                            cond_node = binding["?cond"]
                            cond_lbl = self.graph.nodes[cond_node].get("labels", [cond_node])[0]
                            desc = f"بما أن {sub_lbl} يعيش في {env_lbl}، و {env_lbl} يشتمل على {cond_lbl} الذي يتطلب [{obj_lbl}]، فإن {sub_lbl} يتطلب [{obj_lbl}]"
                        else:
                            desc = f"استنتاج الحقيقة: [{sub_lbl}] --({rel})--> [{obj_lbl}] بناءً على قاعدة '{rule.get('name', rule_id)}'"
                            
                        # Add inferred edge
                        self.graph.add_edge(
                            sub,
                            obj,
                            relation=rel,
                            world=active_world,
                            confidence=conf,
                            type="inferred",
                            rule_id=rule_id,
                            reason=desc,
                            timestamp="2026-06-03T00:00:00Z",
                            source="forward_chainer"
                        )
                        new_edges_added = True
                        
            if not new_edges_added:
                break
            iteration += 1

    def get_persona(self, persona_id="persona_1"):
        for p in self.personas:
            if p["id"] == persona_id:
                return p
        return None
