import os
import json

class AnomalyProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "anomaly_detection.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def check_anomaly(self, entity, relation_name, target_concept):
        """
        Checks if a fact (entity --relation_name--> target_concept) is an anomaly or typical exception.
        Returns anomaly details if found, else None.
        """
        exceptions = self.db.get("exceptions", [])
        
        # Look for exceptions matching entity and property
        for ex in exceptions:
            if ex["entity"] == entity and ex["property"] == target_concept:
                return {
                    "is_anomaly": True,
                    "anomaly_type": ex["exception_type"],
                    "anomaly_score": 1.0 - ex.get("confidence", 0.01),
                    "reason": ex.get("reason", "rare exception"),
                    "typical_rule": ex.get("typical_rule", "")
                }
                
        # Simple generic anomaly score calculation
        # If most entities in the class don't have this property
        return None
