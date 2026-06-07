from src.nlp_drivers.base_driver import BaseLanguageDriver
from src.nlp_drivers.spacy_driver import SpaCyLanguageDriver

# Cache loaded drivers to prevent reloading heavy models (like SpaCy/CamelTools) on every query
_drivers_cache = {}

def get_nlp_driver(language: str = "en") -> BaseLanguageDriver:
    """
    Returns the appropriate NLP Driver instance for the given language.
    Caches the instances for performance.
    """
    language = language.lower().strip()
    
    if language in _drivers_cache:
        return _drivers_cache[language]
        
    if language == "ar":
        try:
            from src.nlp_drivers.arabic_driver import ArabicLanguageDriver
            driver = ArabicLanguageDriver()
        except Exception as e:
            print(f"Warning: Failed to load ArabicLanguageDriver: {e}. Falling back to BaseLanguageDriver.")
            from src.nlp_drivers.base_driver import BaseLanguageDriver
            driver = BaseLanguageDriver()
    else:
        # Load SpaCy for other languages (en, fr, es, etc.)
        try:
            driver = SpaCyLanguageDriver(language=language)
        except Exception as e:
            print(f"Warning: Failed to load SpaCyLanguageDriver for '{language}': {e}. Falling back to base English driver.")
            driver = SpaCyLanguageDriver(language="en")
            
    _drivers_cache[language] = driver
    return driver
