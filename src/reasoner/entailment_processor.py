import os
import json

class EntailmentProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "entailment.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def check_entailment(self, relation_name, target_concept, graph_handler):
        """
        Given a relation and target concept, checks if any entailment rules apply.
        e.g. premise: is_a animal => conclusion: is_a living_thing.
        Returns a list of inferred entailed relations.
        """
        entailed = []
        for ent in self.db.get("entailments", []):
            premise = ent.get("premise")
            conclusion = ent.get("conclusion")
            if not premise or not conclusion:
                continue
            
            if "relation" not in premise or "to" not in premise:
                continue
            if "relation" not in conclusion or "to" not in conclusion:
                continue
            
            if premise["relation"] == relation_name and premise["to"] == target_concept:
                entailed.append({
                    "relation": conclusion["relation"],
                    "to": conclusion["to"],
                    "confidence": ent.get("confidence", 1.0)
                })
        return entailed
        
    def detect_contradiction(self, relation_1, relation_2):
        """
        Checks if two relations / statements contradict each other.
        e.g., eats_meat and eats_vegetarian, or is_alive and is_dead.
        """
        for rule in self.db.get("contradiction_detection", []):
            s1 = rule["statement1"]
            s2 = rule["statement2"]
            if (relation_1 == s1 and relation_2 == s2) or (relation_1 == s2 and relation_2 == s1):
                return True
        return False
