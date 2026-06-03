import os
import json

class FuzzyModalEngine:
    def __init__(self):
        self.modalities = {
            "always": 1.0,
            "usually": 0.8,
            "sometimes": 0.5,
            "rarely": 0.2,
            "possibly": 0.1
        }
        self.keywords = {}
        self.load_modalities()

    def load_modalities(self):
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(project_dir, "data", "modalities.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.keywords = data.get("keywords", {})
                self.modalities = data.get("weights", self.modalities)

    def detect_modality(self, text: str, language: str) -> tuple:
        """
        Checks if text contains a modality keyword.
        Returns (modality_name, cleaned_text).
        """
        words = text.strip().split()
        lang_keywords = self.keywords.get(language, {})
        
        detected_modality = None
        cleaned_words = []
        
        for word in words:
            clean_w = word.replace("؟", "").replace("!", "").replace("،", "").replace(",", "")
            # Check lowercase for English/French
            lookup_w = clean_w.lower() if language in ["en", "fr"] else clean_w
            if lookup_w in lang_keywords:
                detected_modality = lang_keywords[lookup_w]
            else:
                cleaned_words.append(word)
                
        if detected_modality:
            return detected_modality, " ".join(cleaned_words)
        return None, text

    def get_confidence_multiplier(self, modality: str) -> float:
        return self.modalities.get(modality, 1.0)
