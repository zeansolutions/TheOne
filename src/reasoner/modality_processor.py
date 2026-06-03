import os
import json

class ModalityProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "modality.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def process_modality(self, text, language):
        """
        Parses modality markers in a sentence and determines its modality type and confidence.
        """
        words = text.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "") for w in words]
        if language in ["en", "fr"]:
            words = [w.lower() for w in words]
            
        detected_name = None
        detected_def = None
        
        for modal_name, modal_def in self.db.get("modalities", {}).items():
            markers = modal_def.get("markers", [])
            if any(marker in words or marker in text for marker in markers):
                detected_name = modal_name
                detected_def = modal_def
                break
                
        if detected_name:
            return {
                "modality": detected_name,
                "confidence": detected_def.get("confidence", 1.0),
                "logic": detected_def.get("logic", "")
            }
            
        return {
            "modality": "certainty",
            "confidence": 1.0,
            "logic": "always(X)"
        }
