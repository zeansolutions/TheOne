import re
import json

class LanguageSelectionEngine:
    """
    Determines the best language for the response based on user input,
    preferences, and conversation history.
    """
    
    def __init__(self, languages_data):
        # languages_data can be the parsed dict from config/languages.json or a path
        if isinstance(languages_data, str):
            with open(languages_data, 'r', encoding='utf-8') as f:
                self.languages_config = json.load(f)
        else:
            self.languages_config = languages_data
            
        self.languages = {lang["id"]: lang for lang in self.languages_config.get("languages", [])}
        self.default_language = "ar"
    
    def detect_language(self, text):
        """
        Detects the language of the input text using regex and vocabulary.
        Returns 'ar', 'en', 'fr', or self.default_language.
        """
        if not text:
            return self.default_language
            
        text_lower = text.lower()
        
        # 1. Check for Arabic characters
        if re.search(r"[\u0600-\u06FF]", text):
            return "ar"
            
        # 2. Check for French specific features (accents or key vocabulary)
        french_accent_pattern = r"[àâäéèêëîïôöùûüç]"
        french_keywords = [
            "mange", "mangent", "manger", "vit", "vivent", "vivre", "polaire", "ours", 
            "savane", "arctique", "pourquoi", "comment", "est-ce", "viande", "soleil",
            "le", "la", "les", "du", "de", "est", "et", "un", "une", "où", "que"
        ]
        
        if re.search(french_accent_pattern, text_lower):
            return "fr"
            
        # Tokenize words for keyword matching
        words = re.findall(r"\b\w+\b", text_lower)
        if any(w in french_keywords for w in words):
            return "fr"
            
        # 3. Check for English characters / keywords
        english_keywords = [
            "why", "how", "what", "where", "who", "when", "does", "is", "difference",
            "lion", "lions", "bear", "bears", "polar", "savanna", "savannah", "arctic",
            "fur", "meat", "animal", "predator", "feline", "eat", "eats", "live", "lives",
            "the", "a", "an", "and", "or", "in", "on", "of", "to", "rises", "rise", "sun"
        ]
        if any(w in english_keywords for w in words):
            return "en"
            
        if re.search(r"[a-zA-Z]", text):
            # If there are Latin characters and no French features, default to English
            return "en"
            
        return self.default_language
    
    def select_language(self, detected_lang, user_preference=None, conversation_history=None):
        """
        Selects the language based on:
        1. User preference (e.g. user_preference = 'en')
        2. Detected language
        3. Conversation history (uses last turn language if available)
        4. Default language
        """
        if user_preference:
            return self.validate_language(user_preference)
            
        if detected_lang:
            return self.validate_language(detected_lang)
            
        if conversation_history:
            # conversation_history is a list of dicts, e.g. [{"question": ..., "language": "en"}]
            # or maybe from ConversationManager.get_history()
            # Let's inspect last turn
            last_turn = conversation_history[-1] if conversation_history else None
            if isinstance(last_turn, dict) and "language" in last_turn:
                return self.validate_language(last_turn["language"])
                
        return self.default_language
        
    def validate_language(self, lang_id):
        """
        Validates if the language is supported and enabled.
        """
        if lang_id in self.languages and self.languages[lang_id].get("enabled", True):
            return lang_id
        return self.default_language
