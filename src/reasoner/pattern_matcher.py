import json
import os
from typing import List, Dict, Optional, Any

class MatchResult:
    def __init__(self, intent: str, extracted_entities: Dict[str, str], confidence: float, pattern_id: str, is_deep: bool = False):
        self.intent = intent
        self.extracted_entities = extracted_entities
        self.confidence = confidence
        self.pattern_id = pattern_id
        self.is_deep = is_deep

    def __repr__(self):
        return f"MatchResult(intent={self.intent}, entities={self.extracted_entities}, confidence={self.confidence}, pattern_id={self.pattern_id}, is_deep={self.is_deep})"

class GenericPatternMatcher:
    def __init__(self, language_rules_path: str):
        self.rules_path = language_rules_path
        self.patterns = []
        self.load_patterns()

    def load_patterns(self):
        """Loads semantic frames/patterns from language_rules.json."""
        if not os.path.exists(self.rules_path):
            self.patterns = []
            return
        
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Support both semantic_frames and syntactic_patterns
                patterns = data.get("semantic_frames", [])
                if not patterns:
                    patterns = data.get("syntactic_patterns", [])
                
                # Sort patterns by number of constant tokens (non-variable) descending,
                # and secondarily by pattern length descending to match more specific templates first.
                patterns.sort(
                    key=lambda p: (
                        sum(1 for t in p.get("pattern", []) if isinstance(t, str) and not t.startswith("?")),
                        len(p.get("pattern", [])) if p.get("pattern", []) else 0
                    ),
                    reverse=True
                )
                self.patterns = patterns
        except Exception as e:
            print(f"Warning: Failed to load patterns from {self.rules_path}: {e}")
            self.patterns = []

    def _tokenize(self, text: str) -> List[str]:
        """Cleans and splits text into words preserving order."""
        # Clean punctuation
        cleaned = text.strip()
        for punc in ["؟", "?", "!", "،", ",", ".", ";", "؛"]:
            cleaned = cleaned.replace(punc, " ")
        raw_words = cleaned.split()
        tokens = []
        for w in raw_words:
            if w.startswith("وال") and len(w) > 3:
                tokens.append("و")
                tokens.append(w[1:])
            else:
                tokens.append(w)
        return tokens

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]

    def _fuzzy_match(self, word: str, pattern_token: str, threshold: float = 0.8) -> bool:
        w_clean = word.lower()
        p_clean = pattern_token.lower()
        if w_clean == p_clean:
            return True
            
        # Strip common Arabic prefixes from both for matching
        def strip_ar_prefixes(s):
            for pref in ["ال", "وبال", "بال", "وال", "لل", "ب", "و", "ل", "ف"]:
                if s.startswith(pref) and len(s) > len(pref):
                    return s[len(pref):]
            return s
            
        if strip_ar_prefixes(w_clean) == strip_ar_prefixes(p_clean):
            return True
            
        max_len = max(len(w_clean), len(p_clean))
        if max_len == 0:
            return True
        dist = self.levenshtein_distance(w_clean, p_clean)
        sim = 1.0 - (dist / max_len)
        return sim >= threshold

    def _check_condition(self, value: str, condition: str) -> bool:
        """Evaluates named conditions on variable values."""
        if not os.path.exists(self.rules_path):
            return True
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if condition == "is_location_verb":
                # Check location verbs
                verbs = data.get("location_query_settings", {}).get("verbs", [])
                # Also check morphology roots or direct comparison
                words = [value.lower()]
                # Strip prefixes
                w = value
                for pref in ["ال", "لل", "ب", "و", "ل", "ف", "ي", "ت"]:
                    if w.startswith(pref) and len(w) > len(pref):
                        words.append(w[len(pref):])
                
                # Check morphology roots
                roots = data.get("morphology", {}).get("roots", [])
                for r in roots:
                    if r.get("id") == "عوش":
                        for pattern in r.get("patterns", []):
                            if any(wd in pattern or pattern in wd for wd in words):
                                return True
                return any(v in words or any(wd in v for wd in words) for v in verbs)
        except Exception:
            pass
        return True

    def _match_subsequence(self, pattern_tokens: List[str], text_tokens: List[str], 
                           p_idx: int, t_idx: int, bindings: Dict[str, str], 
                           conditions: Dict[str, str]) -> Optional[Dict[str, str]]:
        if p_idx == len(pattern_tokens) and t_idx == len(text_tokens):
            return bindings
        if p_idx == len(pattern_tokens) or t_idx == len(text_tokens):
            return None
            
        pat_token = pattern_tokens[p_idx]
        
        if pat_token.startswith("?"):
            # Variable matching: must consume at least 1 token.
            # Try matching subsequences of length 1, 2, ..., up to the remaining tokens.
            for length in range(1, len(text_tokens) - t_idx + 1):
                sub_tokens = text_tokens[t_idx : t_idx + length]
                sub_str = " ".join(sub_tokens)
                
                # Check condition if specified
                cond = conditions.get(pat_token)
                if cond and not self._check_condition(sub_str, cond):
                    continue
                    
                new_bindings = bindings.copy()
                new_bindings[pat_token] = sub_str
                
                res = self._match_subsequence(pattern_tokens, text_tokens, p_idx + 1, t_idx + length, new_bindings, conditions)
                if res is not None:
                    return res
            return None
        else:
            # Constant token matching
            text_token = text_tokens[t_idx]
            if self._fuzzy_match(text_token, pat_token):
                return self._match_subsequence(pattern_tokens, text_tokens, p_idx + 1, t_idx + 1, bindings, conditions)
            return None

    def match(self, text: str) -> Optional[MatchResult]:
        """Attempts to match text against all loaded patterns."""
        tokens = self._tokenize(text)
        if not tokens:
            return None
            
        # Re-load to get any runtime-learned patterns
        self.load_patterns()
        
        for pat_data in self.patterns:
            pat_tokens = pat_data.get("pattern", [])
            conditions = pat_data.get("conditions", {})
            
            bindings = self._match_subsequence(pat_tokens, tokens, 0, 0, {}, conditions)
            if bindings is not None:
                # Extract entities based on mapping
                mapping = pat_data.get("mapping", {})
                extracted_entities = {}
                for key, var in mapping.items():
                    if var in bindings:
                        extracted_entities[key] = bindings[var]
                        
                confidence = pat_data.get("confidence", 1.0)
                is_deep = pat_data.get("is_deep", False)
                return MatchResult(
                    intent=pat_data.get("intent"),
                    extracted_entities=extracted_entities,
                    confidence=confidence,
                    pattern_id=pat_data.get("id"),
                    is_deep=is_deep
                )
        return None
