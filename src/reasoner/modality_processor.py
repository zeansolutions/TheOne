import os
import json

class ModalityProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "modalities.json")
            
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
            
        import re
        detected_name = None
        detected_def = None
        
        modalities_dict = self.db.get("logical_modalities") or self.db.get("modalities", {})
        for modal_name, modal_def in modalities_dict.items():
            markers = modal_def.get("markers", [])
            matched = False
            for marker in markers:
                if " " in marker:
                    # multi-word phrase matching with word boundaries
                    pattern = rf"(?:^|\s|[،,\.\?؟]){re.escape(marker)}(?:$|\s|[،,\.\?؟])"
                    if re.search(pattern, text):
                        matched = True
                        break
                else:
                    if marker in words:
                        matched = True
                        break
            if matched:
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
