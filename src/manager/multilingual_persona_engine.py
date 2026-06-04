import os
import json
from src.manager.language_selection_engine import LanguageSelectionEngine
from src.reasoner.persona_selector import MultilingualPersonaSelector
from src.renderer.expression_renderer import MultilingualExpressionRenderer

class MultilingualPersonaEngine:
    """
    Unified manager class that brings together:
    - Language selection
    - Persona selection
    - Expression rendering
    To provide natural localized responses with personality.
    """
    
    def __init__(self, graph_handler, personas_path=None, languages_path=None):
        self.handler = graph_handler
        
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Load paths or fallbacks
        if not personas_path:
            personas_path = os.path.join(project_dir, "config", "personas_multilingual.json")
            if not os.path.exists(personas_path):
                personas_path = "config/personas_multilingual.json"
                
        if not languages_path:
            languages_path = os.path.join(project_dir, "config", "languages.json")
            if not os.path.exists(languages_path):
                languages_path = "config/languages.json"
                
        # Load JSON data
        with open(personas_path, 'r', encoding='utf-8') as f:
            self.personas_db = json.load(f).get("personas", [])
            
        with open(languages_path, 'r', encoding='utf-8') as f:
            self.languages_db = json.load(f)
            
        # Initialize sub-engines
        self.language_engine = LanguageSelectionEngine(self.languages_db)
        self.persona_selector = MultilingualPersonaSelector(self.personas_db, language=None, graph_handler=graph_handler)
        self.expression_renderer = MultilingualExpressionRenderer(self.personas_db, graph_handler)
        
    def process_response(self, question, logical_response, conversation_history=None, user_preference=None, force_persona_id=None):
        """
        Runs the complete rendering pipeline:
        1. Detects input language.
        2. Selects output language.
        3. Analyzes context features & selects persona.
        4. Renders the final localized persona-styled response.
        """
        # 1. Detect & select language
        detected_lang = self.language_engine.detect_language(question)
        selected_language = self.language_engine.select_language(
            detected_lang,
            user_preference=user_preference,
            conversation_history=conversation_history
        )
        
        # 2. Select persona
        self.persona_selector.language = selected_language
        context = self.persona_selector.analyze_context(
            question, 
            conversation_history, 
            mapped_concepts=logical_response.get("mapped_concepts", [])
        )
        
        if force_persona_id and any(p["id"] == force_persona_id for p in self.personas_db):
            selected_persona_id = force_persona_id
        else:
            selected_persona_id = self.persona_selector.select_best_persona(context)
        
        # 3. Render response
        final_response = self.expression_renderer.render_response(
            logical_response,
            selected_persona_id,
            selected_language,
            context
        )
        
        return {
            "response": final_response,
            "language": selected_language,
            "persona": selected_persona_id,
            "confidence": logical_response.get("confidence", 1.0)
        }
