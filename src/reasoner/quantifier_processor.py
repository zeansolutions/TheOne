import os
import json

class QuantifierProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "quantifiers.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def detect_quantifier(self, text):
        """
        Detects if there is a quantifier in the text (Arabic/English) and returns its properties.
        """
        words = text.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").lower() for w in words]
        
        for q in self.db.get("quantifiers", []):
            markers = q.get("markers", [])
            for marker in markers:
                m_words = marker.strip().lower().split()
                if not m_words:
                    continue
                # Check if the list of marker tokens is a subsegment of the list of word tokens
                n = len(m_words)
                for i in range(len(words) - n + 1):
                    if words[i:i+n] == m_words:
                        return q
        return None
        
    def evaluate_quantifiers(self, statement_quantifier, query_quantifier):
        """
        Resolves query checks based on quantifier entailments.
        e.g., if universal holds (forall), then existential holds (exists).
        if existential holds (exists), universal (forall) does not necessarily hold.
        """
        if not statement_quantifier or not query_quantifier:
            return False
            
        s_name = statement_quantifier.get("name")
        q_name = query_quantifier.get("name")
        
        if s_name == "universal":
            # universal implies everything
            return True
        elif s_name == "majority":
            if q_name in ["majority", "existential"]:
                return True
        elif s_name == "existential":
            if q_name == "existential":
                return True
                
        return False
