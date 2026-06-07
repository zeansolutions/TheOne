import spacy
from src.nlp_drivers.base_driver import BaseLanguageDriver

class SpaCyLanguageDriver(BaseLanguageDriver):
    """
    NLP Driver for non-Arabic languages using SpaCy.
    """
    
    # Mapping of language code to spacy model names
    MODEL_MAP = {
        "en": "en_core_web_sm",
        "fr": "fr_core_news_sm",
        "es": "es_core_news_sm",
        "de": "de_core_news_sm",
        "it": "it_core_news_sm",
        "pt": "pt_core_news_sm",
        "nl": "nl_core_news_sm",
        "el": "el_core_news_sm",
        "xx": "xx_ent_wiki_sm" # Multilingual
    }
    
    def __init__(self, language="en"):
        self.language = language
        model_name = self.MODEL_MAP.get(language, "en_core_web_sm")
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # Fallback to English if model not found
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Fallback to blank model
                self.nlp = spacy.blank(language)
                
    def extract_lemmas(self, text: str) -> list[str]:
        doc = self.nlp(text)
        # Extract lower-case lemmas for non-stop, non-punctuation tokens
        lemmas = []
        for token in doc:
            if not token.is_punct and not token.is_space:
                lemmas.append(token.lemma_.lower())
        return lemmas

    def analyze_tokens(self, text: str) -> list[dict]:
        doc = self.nlp(text)
        analysis = []
        for token in doc:
            gender = token.morph.get("Gender")
            gender_val = gender[0] if gender else None
            number = token.morph.get("Number")
            number_val = number[0] if number else None
            
            analysis.append({
                "word": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "gender": gender_val,
                "number": number_val,
                "is_stop": token.is_stop
            })
        return analysis

    def get_gender(self, word: str) -> str:
        doc = self.nlp(word)
        if len(doc) > 0:
            gender = doc[0].morph.get("Gender")
            if gender:
                return gender[0] # E.g., 'Masc' or 'Fem' -> we can map to 'M' or 'F'
        return None
