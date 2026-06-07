from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.utils.dediac import dediac_ar
from camel_tools.utils.normalize import normalize_alef_ar, normalize_alef_maksura_ar, normalize_teh_marbuta_ar
from src.nlp_drivers.base_driver import BaseLanguageDriver

class ArabicLanguageDriver(BaseLanguageDriver):
    """
    NLP Driver for Arabic using NYUAD's CAMeL Tools.
    Supports high-quality tokenization, lemmatization, and gender/number detection.
    """
    
    def __init__(self):
        # Initialize pretrained MLE Disambiguator
        try:
            self.mle = MLEDisambiguator.pretrained()
        except Exception as e:
            # Re-raise with a clear message
            raise RuntimeError(
                f"CAMeL Tools pretrained MLEDisambiguator failed to load: {e}. "
                "Ensure that light datasets are installed via 'camel_data -i light'."
            )
            
    def normalize_text(self, text: str) -> str:
        """Normalizes alefs, alef maksuras, and teh marbutas to reduce orthographic noise."""
        text = text.strip()
        text = normalize_alef_ar(text)
        text = normalize_alef_maksura_ar(text)
        text = normalize_teh_marbuta_ar(text)
        return text
        
    def extract_lemmas(self, text: str) -> list[str]:
        # Tokenize using simple whitespace/punctuation tokenizer
        tokens = simple_word_tokenize(text)
        if not tokens:
            return []
            
        disambiguated = self.mle.disambiguate(tokens)
        lemmas = []
        for word_analyses in disambiguated:
            if word_analyses and word_analyses.analyses:
                # The first analysis in the list is the most probable one (highest score)
                best_analysis = word_analyses.analyses[0].analysis
                lex = best_analysis.get('lex')
                if lex:
                    # Strip diacritics from the lemma
                    clean_lemma = dediac_ar(lex)
                    # Strip camel-tools specific endings (e.g. '_1', '_2')
                    if '_' in clean_lemma:
                        clean_lemma = clean_lemma.split('_')[0]
                    # Strip leading underscore
                    if clean_lemma.startswith('_'):
                        clean_lemma = clean_lemma[1:]
                    lemmas.append(clean_lemma)
            else:
                # If no analysis was found, just use the token itself
                pass
        return lemmas

    def analyze_tokens(self, text: str) -> list[dict]:
        tokens = simple_word_tokenize(text)
        if not tokens:
            return []
            
        disambiguated = self.mle.disambiguate(tokens)
        analysis = []
        
        for token, word_analyses in zip(tokens, disambiguated):
            if word_analyses and word_analyses.analyses:
                best_analysis = word_analyses.analyses[0].analysis
                lex = best_analysis.get('lex', token)
                clean_lemma = dediac_ar(lex).split('_')[0]
                if clean_lemma.startswith('_'):
                    clean_lemma = clean_lemma[1:]
                    
                pos = best_analysis.get('pos', 'noun')
                # Map gender
                gen = best_analysis.get('gen', 'na')
                gender_val = 'M' if gen == 'm' else ('F' if gen == 'f' else None)
                # Map number
                num = best_analysis.get('num', 'na')
                num_map = {'s': 'S', 'd': 'D', 'p': 'P'}
                number_val = num_map.get(num, None)
                
                # Check if it's a stop word
                is_stop = pos in ['prep', 'conj', 'part', 'pron']
                
                analysis.append({
                    "word": token,
                    "lemma": clean_lemma,
                    "pos": pos.upper(),
                    "gender": gender_val,
                    "number": number_val,
                    "is_stop": is_stop
                })
            else:
                analysis.append({
                    "word": token,
                    "lemma": token,
                    "pos": "NOUN",
                    "gender": None,
                    "number": None,
                    "is_stop": False
                })
        return analysis

    def get_gender(self, word: str) -> str:
        # Resolve gender for a single word
        analyses = self.analyze_tokens(word)
        if analyses:
            return analyses[0]["gender"]
        return None

    def match_gender(self, word: str, target_gender: str) -> str:
        """
        Synthesizes/adjusts the word suffix to match the target grammatical gender.
        E.g., 'جميل' + 'F' -> 'جميلة'.
        """
        if not word or not target_gender:
            return word
            
        target_gender = target_gender.upper()
        current_gender = self.get_gender(word)
        
        # If it already matches, return as is
        if current_gender == target_gender:
            return word
            
        # Basic morphological rules for adjective/noun feminization
        if target_gender == 'F':
            if not (word.endswith('ة') or word.endswith('ى') or word.endswith('اء')):
                return word + 'ة'
        elif target_gender == 'M':
            if word.endswith('ة'):
                return word[:-1]
                
        return word
