import os
import json

class NegationProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "negation_rules.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def has_negation(self, text, language):
        """
        Returns True if the text contains a negation marker.
        Supports counting to handle double-negation elimination.
        """
        words = text.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "") for w in words]
        
        markers = self.db.get("negation_markers", {}).get(language, [])
        neg_count = sum(1 for w in words if w in markers)
        
        # If count is even, double negation elimination applies: it's positive.
        # If count is odd, it is negated.
        return neg_count % 2 == 1
        
    def resolve_opposite(self, property_name):
        """
        Maps a property to its antonym/opposite if configured.
        """
        for p in self.db.get("polarities", []):
            if p["positive"] == property_name:
                return p["opposite"]
            if p["negative"] == property_name:
                return p["positive"]
        return None
