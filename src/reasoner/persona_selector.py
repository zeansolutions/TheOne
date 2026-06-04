import re
import json

class MultilingualPersonaSelector:
    """
    Selects the most appropriate persona for the response in the selected language
    based on query context, keywords, mood, and conversation history.
    """
    
    def __init__(self, personas_data, language=None, graph_handler=None):
        # personas_data can be a parsed list from config/personas_multilingual.json or a path
        if isinstance(personas_data, str):
            with open(personas_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.personas = data.get("personas", [])
        else:
            self.personas = personas_data
            
        self.language = language or "ar"
        self.handler = graph_handler
    
    def analyze_context(self, question, conversation_history, mapped_concepts=None):
        """
        Analyzes query and history to extract features for persona selection.
        """
        if mapped_concepts is None:
            mapped_concepts = []
            
        context = {
            "question_type": self.detect_question_type(question),
            "keywords": self.extract_keywords(question, self.language),
            "mood": self.detect_mood(question),
            "context": self.get_conversation_context(conversation_history),
            "entity_importance": self.measure_entity_importance(mapped_concepts)
        }
        return context
        
    def detect_question_type(self, question):
        """
        Classifies the question type: 'philosophical', 'scientific', 'practical', or 'casual'.
        """
        q = question.lower()
        
        # Load from handler database if available to prevent hardcoding
        philosophical_words = []
        scientific_words = []
        practical_words = []
        
        if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
            for lang in ["ar", "en", "fr"]:
                lang_data = self.handler.language_rules.get(lang, {})
                classification = lang_data.get("question_classification", {})
                philosophical_words.extend(classification.get("philosophical", []))
                scientific_words.extend(classification.get("scientific", []))
                practical_words.extend(classification.get("practical", []))
                
        # If database is empty or not loaded yet, use local fallback
        if not philosophical_words:
            philosophical_words = [
                "ليه", "لماذا", "رأيك", "تفسير", "هل", 
                "why", "opinion", "explain", "philosophical", "reason",
                "pourquoi", "avis", "explication", "est-ce"
            ]
        if not scientific_words:
            scientific_words = [
                "كم", "أين", "اين", "برهان", "دليل", "ما", "من",
                "how many", "where", "evidence", "proof", "what", "scientific", "data", "analytical",
                "combien", "où", "preuve", "évidence", "que", "données", "scientifique"
            ]
        if not practical_words:
            practical_words = [
                "الفرق", "ازاي", "إزاي", "لو", "إذا", "اذا",
                "difference", "how to", "how", "if", "practical", "compare",
                "différence", "comment", "si", "comparer"
            ]
        
        # Check practical first (e.g. comparison or hypothetical)
        if any(w in q for w in practical_words):
            return "practical"
        # Check scientific (factual/lookup)
        if any(w in q for w in scientific_words):
            return "scientific"
        # Check philosophical (why/opinion/explanation)
        if any(w in q for w in philosophical_words):
            return "philosophical"
            
        return "casual"
        
    def extract_keywords(self, question, language):
        """
        Extracts words from query to match against persona triggers.
        """
        # Simple tokenization and cleaning
        words = re.findall(r"\b\w+\b", question.lower())
        return words
        
    def detect_mood(self, question):
        """
        Detects query mood: 'light', 'analytical', or 'calm'.
        """
        q = question.lower()
        
        light_indicators = []
        analytical_indicators = []
        
        if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
            for lang in ["ar", "en", "fr"]:
                lang_data = self.handler.language_rules.get(lang, {})
                mood_ind = lang_data.get("mood_indicators", {})
                light_indicators.extend(mood_ind.get("light", []))
                analytical_indicators.extend(mood_ind.get("analytical", []))
                
        # Fallbacks if database is empty
        if not light_indicators:
            light_indicators = ["!", "😊", "😂", "😄", "😉", "يا هلا", "برو", "يا غالي", "buddy", "cool", "mec", "hey", "hé", "pote", "mdr"]
        else:
            # Always allow basic punctuation like "!" and emojis in light indicators even if loaded dynamically
            extra = ["!", "😊", "😂", "😄", "😉"]
            for ex in extra:
                if ex not in light_indicators:
                    light_indicators.append(ex)
                    
        if not analytical_indicators:
            analytical_indicators = [
                "برهان", "دليل", "كم", "إثبات", "معطيات", "أرقام",
                "evidence", "proof", "data", "stats", "formula", "verify",
                "preuve", "évidence", "données", "chiffres", "statistiques"
            ]
            
        if any(ind in question for ind in light_indicators):
            return "light"
        if any(ind in q for ind in analytical_indicators):
            return "analytical"
            
        return "calm"
        
    def get_conversation_context(self, conversation_history):
        """
        Returns list of active context states: 'conversation_start', 'mid_conversation', 'follow_up_deep'.
        """
        states = []
        if not conversation_history:
            states.append("conversation_start")
        else:
            states.append("mid_conversation")
            # If the last turn was highly factual or reasoning-based, it's follow_up_deep
            last_turn = conversation_history[-1]
            if isinstance(last_turn, dict):
                # check if there's deep reasoning trace
                trace = last_turn.get("trace", [])
                if len(trace) > 2:
                    states.append("follow_up_deep")
        return states
        
    def measure_entity_importance(self, mapped_concepts):
        """
        Scores entity importance: 1.0 if concepts were successfully resolved, 0.0 otherwise.
        """
        return 1.0 if mapped_concepts else 0.0
        
    def score_persona_match(self, context, persona_variant):
        """
        Scores how well a persona matches the query context.
        Formula:
        score = (0.35 * type_score) + 
                (0.25 * keyword_score) + 
                (0.20 * mood_score) + 
                (0.15 * context_score) + 
                (0.05 * entity_score)
        """
        triggers = persona_variant.get("triggers", {})
        
        # 1. Question Type Score
        allowed_types = triggers.get("question_types", [])
        if not allowed_types:
            type_score = 1.0
        else:
            type_score = 1.0 if context["question_type"] in allowed_types else 0.0
            
        # 2. Keyword Match Score
        trigger_keywords = triggers.get("keywords", [])
        if not trigger_keywords:
            keyword_score = 1.0
        else:
            # Check if any trigger keyword is in the question keywords
            matched_keywords = [kw for kw in trigger_keywords if kw in context["keywords"]]
            if not matched_keywords:
                keyword_score = 0.0
            else:
                # Helper: if the only matched keywords are extremely common helper words/verbs, penalize
                helpers = {"is", "does", "did", "can", "has", "are", "est-ce", "est", "a-t-il", "peut-il", "a", "ont", "هل", "ما", "ماذا"}
                if all(kw in helpers for kw in matched_keywords):
                    keyword_score = 0.2
                else:
                    keyword_score = 1.0
            
        # 3. Mood Match Score
        target_mood = triggers.get("mood")
        if not target_mood:
            mood_score = 1.0
        else:
            mood_score = 1.0 if context["mood"] == target_mood else 0.0
            
        # 4. Context Match Score
        target_contexts = triggers.get("context", [])
        if not target_contexts:
            context_score = 1.0
        else:
            # Check overlap between detected contexts and persona triggers
            overlap = set(context["context"]).intersection(set(target_contexts))
            context_score = 1.0 if overlap else 0.0
            
        # 5. Entity Importance Score
        entity_score = context["entity_importance"]
        
        # Calculate total score
        total = (0.35 * type_score) + \
                (0.25 * keyword_score) + \
                (0.20 * mood_score) + \
                (0.15 * context_score) + \
                (0.05 * entity_score)
                
        return total
        
    def select_best_persona(self, context):
        """
        Selects the best persona ID based on highest match score.
        """
        scores = {}
        
        for persona in self.personas:
            # Get the language-specific version of the persona
            persona_variant = persona["versions"].get(self.language)
            if not persona_variant:
                continue # Language not supported by this persona
                
            score = self.score_persona_match(context, persona_variant)
            scores[persona["id"]] = score
            
        if not scores:
            # Return first persona ID as fallback if none matches/supports language
            return self.personas[0]["id"] if self.personas else None
            
        # Select the persona with the highest score
        # In case of tie, priority field can break ties, or we just select the first max
        best_persona_id = max(scores, key=scores.get)
        return best_persona_id
