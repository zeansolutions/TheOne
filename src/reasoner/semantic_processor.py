import os
import json

class SemanticProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "semantic_roles.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def extract_semantic_roles(self, words, language, graph_handler):
        """
        Dynamically extracts semantic roles from sentence words based on the semantic_roles.json config.
        """
        frames = self.db.get("semantic_frames", {})
        
        # 1. Identify predicate
        detected_pred = None
        frame_key = None
        
        # Look for a word that matches a predicate or its root
        for key, frame in frames.items():
            pred_word = frame["predicate"]
            # Look up morphological matches
            for word in words:
                # Direct match
                if word == pred_word or word in pred_word:
                    detected_pred = pred_word
                    frame_key = key
                    break
                # Root match
                for root in graph_handler.language_rules.get("morphology", {}).get("roots", []):
                    if word in root["patterns"] and pred_word in root["patterns"]:
                        detected_pred = pred_word
                        frame_key = key
                        break
                if detected_pred:
                    break
            if detected_pred:
                break
                
        if not frame_key:
            return None
            
        frame = frames[frame_key]
        roles = {}
        
        # 2. Extract arguments for roles
        for role_def in frame["roles"]:
            role_type = role_def["role_type"]
            constraints = role_def.get("constraints", [])
            
            # Find a word in sentence that matches the role type constraints
            for word in words:
                # Skip predicate or words sharing the predicate's root
                shares_root = False
                for root in graph_handler.language_rules.get("morphology", {}).get("roots", []):
                    if word in root["patterns"] and detected_pred in root["patterns"]:
                        shares_root = True
                        break
                if shares_root or word == detected_pred:
                    continue
                    
                concept = graph_handler.dynamic_morphological_lookup(word, language=language)
                if not concept:
                    continue
                    
                # If there are constraints, verify if the concept satisfies them
                satisfied = True
                for constraint in constraints:
                    if ":" in constraint:
                        c_type, c_val = constraint.split(":", 1)
                        if c_type == "is_a":
                            # Check taxonomic classification
                            # Check if concept is subclass of c_val
                            from src.simple_reasoner import SimpleReasoner
                            reasoner = SimpleReasoner(graph_handler)
                            res = reasoner.check_is_a_relationship(concept, c_val)
                            if not res["result"] and concept != c_val:
                                satisfied = False
                                break
                    else:
                        # Simple value match
                        if concept != constraint:
                            satisfied = False
                            break
                            
                if satisfied:
                    roles[role_type] = concept
                    break
                    
        # Check required roles
        for role_def in frame["roles"]:
            role_type = role_def["role_type"]
            if role_def.get("required", False) and role_type not in roles:
                # Bind fallback from graph
                if role_type == "AGENT" and "PATIENT" in roles:
                    patient_concept = roles["PATIENT"]
                    for u, v, data in graph_handler.graph.edges(data=True):
                        if v == patient_concept and data.get("relation") in ["eats", "hunting", "has_property"]:
                            roles["AGENT"] = u
                            break
                elif role_type == "PATIENT" and "AGENT" in roles:
                    agent_concept = roles["AGENT"]
                    for u, v, data in graph_handler.graph.edges(data=True):
                        if u == agent_concept and data.get("relation") in ["eats", "hunting", "has_property"]:
                            roles["PATIENT"] = v
                            break
                            
        return {
            "predicate": frame_key,
            "roles": roles
        }
