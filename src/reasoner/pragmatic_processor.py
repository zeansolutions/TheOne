import os
import json

class PragmaticProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "pragmatic_knowledge.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def resolve_metaphor(self, text):
        """
        Scans text for metaphorical/pragmatic phrases and maps them to their literal entities.
        e.g., "ملك الغابة" -> "feline_carnivore".
        """
        for fact in self.db.get("pragmatic_facts", []):
            metaphor = fact["metaphor"]
            if metaphor in text:
                return {
                    "metaphor": metaphor,
                    "literal": fact["literal"],
                    "meaning": fact["metaphorical_meaning"],
                    "context": fact["cultural_context"]
                }
        return None
        
    def check_sentiment_implicature(self, phrase):
        """
        Checks implicatures based on contextual rules.
        """
        for rule in self.db.get("contextual_rules", []):
            # For simplicity, check if condition terms match the phrase
            if "praise" in rule["condition"] and any(term in phrase for term in ["ملك", "شجاع", "قوي"]):
                return rule["implicature"]
        return None
