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

    def load_databases(self, ontology_path, facts_path, language_rules_path):
        """Loads and parses JSON databases, populating the NetworkX graph and dynamic rules."""
        # 1. Load Language Rules
        with open(language_rules_path, 'r', encoding='utf-8') as f:
            self.language_rules = json.load(f)
            
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
                    reason=fact.get("reason", None)
                )

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
            if data.get("relation") in ["has_property", "lives_in"]:
                properties.append({
                    "property": to_node,
                    "relation": data.get("relation"),
                    "causal_purpose": data.get("causal_purpose")
                })
                
        # Look at facts matching the world
        for _, to_node, data in self.graph.out_edges(concept_id, data=True):
            if data.get("type") == "fact" and data.get("world") == world:
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

    def dynamic_morphological_lookup(self, word):
        """
        Dynamic morphological analyzer.
        Matches input words to concept IDs using rules loaded in self.language_rules.
        """
        # Clean word of punctuation
        word = word.strip().replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "")
        
        # Direct lookup in concept labels
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "concept":
                if word in data.get("labels", []):
                    return node
                    
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
                        return node
                        
        # Check dynamic lexicon roots
        for stem in sorted(list(candidates), key=len):
            for root in self.language_rules.get("morphology", {}).get("roots", []):
                if stem in root["patterns"]:
                    for pat in root["patterns"]:
                        for node, data in self.graph.nodes(data=True):
                            if data.get("type") == "concept" and pat in data.get("labels", []):
                                return node
                                
        return None

    def get_persona(self, persona_id="persona_1"):
        for p in self.personas:
            if p["id"] == persona_id:
                return p
        return None
