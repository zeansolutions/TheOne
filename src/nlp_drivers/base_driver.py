class BaseLanguageDriver:
    """
    Base class for language-specific NLP processing.
    Handles tokenization, lemmatization, POS tagging, and morphology.
    """
    
    def normalize_text(self, text: str) -> str:
        """Normalizes orthography (e.g. stripping strange accents or unifying letter shapes)."""
        return text.strip()
        
    def extract_lemmas(self, text: str) -> list[str]:
        """
        Tokenizes the input text and returns a list of lemmas (dictionary forms).
        Useful for concept/entity resolution.
        """
        return [w.lower() for w in text.split()]

    def analyze_tokens(self, text: str) -> list[dict]:
        """
        Performs full token analysis, returning a list of dicts:
        [
          {
            "word": "...",
            "lemma": "...",
            "pos": "NOUN/VERB/...",
            "gender": "M/F",
            "number": "S/P/D",
            "is_stop": True/False
          }
        ]
        """
        return []

    def get_gender(self, word: str) -> str:
        """Returns grammatical gender: 'M' (masculine), 'F' (feminine), or None."""
        return None

    def match_gender(self, word: str, target_gender: str) -> str:
        """
        Modifies a word (like an adjective) to match the target gender.
        E.g. in Arabic: 'جميل' + 'F' -> 'جميلة'.
        """
        return word
