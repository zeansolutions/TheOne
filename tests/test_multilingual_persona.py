import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine

@pytest.fixture
def setup_multilingual_engine():
    handler = GraphHandler()
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    engine = MultilingualPersonaEngine(handler)
    return reasoner, engine

def test_language_detection(setup_multilingual_engine):
    _, engine = setup_multilingual_engine
    
    # Test Arabic detection
    assert engine.language_engine.detect_language("ليه الأسد بياكل لحمة؟") == "ar"
    assert engine.language_engine.detect_language("هل الأسد حيوان؟") == "ar"
    
    # Test English detection
    assert engine.language_engine.detect_language("Why does the lion eat meat?") == "en"
    assert engine.language_engine.detect_language("Is the lion an animal?") == "en"
    
    # Test French detection
    assert engine.language_engine.detect_language("Pourquoi le lion mange-t-il de la viande?") == "fr"
    assert engine.language_engine.detect_language("Est-ce que le lion est un animal?") == "fr"

def test_persona_selection_arabic(setup_multilingual_engine):
    reasoner, engine = setup_multilingual_engine
    
    # 1. Philosophical/Why question -> Sage Friend
    q1 = "ليه الأسد بياكل لحمة؟"
    res1 = reasoner.process_query(q1, language="ar")
    ctx1 = engine.persona_selector.analyze_context(q1, None, res1.get("mapped_concepts", []))
    assert engine.persona_selector.select_best_persona(ctx1) == "sage_friend"
    
    # 2. Scientific/How many/Where question -> Scientist
    q2 = "كم درجة حرارة القطب؟"
    res2 = reasoner.process_query(q2, language="ar")
    ctx2 = engine.persona_selector.analyze_context(q2, None, res2.get("mapped_concepts", []))
    assert engine.persona_selector.select_best_persona(ctx2) == "scientist"
    
    # 3. Practical/Conditional question -> Witty Mentor
    # In Arabic, "لو الأسد..." has conditional keyword "لو" and "الفرق"
    q3 = "ما الفرق بين الأسد والدب القطبي؟"
    res3 = reasoner.process_query(q3, language="ar")
    ctx3 = engine.persona_selector.analyze_context(q3, None, res3.get("mapped_concepts", []))
    assert engine.persona_selector.select_best_persona(ctx3) == "witty_mentor"

def test_persona_selection_english(setup_multilingual_engine):
    reasoner, engine = setup_multilingual_engine
    engine.persona_selector.language = "en"
    
    # 1. Why/Philosophical question -> Sage Friend
    q1 = "Why does the lion eat meat?"
    res1 = reasoner.process_query(q1, language="en")
    ctx1 = engine.persona_selector.analyze_context(q1, None, res1.get("mapped_concepts", []))
    assert engine.persona_selector.select_best_persona(ctx1) == "sage_friend"
    
    # 2. Scientific query -> Scientist
    q2 = "Where does the polar bear live?"
    res2 = reasoner.process_query(q2, language="en")
    ctx2 = engine.persona_selector.analyze_context(q2, None, res2.get("mapped_concepts", []))
    assert engine.persona_selector.select_best_persona(ctx2) == "scientist"
    
    # 3. Practical query (difference / comparison) -> Witty Mentor
    q3 = "What is the difference between lion and bear?"
    res3 = reasoner.process_query(q3, language="en")
    ctx3 = engine.persona_selector.analyze_context(q3, None, res3.get("mapped_concepts", []))
    assert engine.persona_selector.select_best_persona(ctx3) == "witty_mentor"

def test_end_to_end_arabic_sage(setup_multilingual_engine):
    reasoner, engine = setup_multilingual_engine
    
    q = "هل الأسد حيوان؟"
    res = reasoner.process_query(q)
    output = engine.process_response(q, res)
    
    assert output["language"] == "ar"
    assert output["persona"] == "sage_friend"
    # Check that at least one of the possible Arabic sage friend expressions or stylistic markers is in the response
    assert any(marker in output["response"] for marker in ["صديق", "صاحب", "غالي", "بص", "الحقيقة"])
    assert "الاستدلال" in output["response"]

def test_end_to_end_english_scientist(setup_multilingual_engine):
    reasoner, engine = setup_multilingual_engine
    
    q = "Where does the polar bear live?"
    res = reasoner.process_query(q)
    output = engine.process_response(q, res)
    
    assert output["language"] == "en"
    assert output["persona"] == "scientist"
    assert "polar bear lives in the arctic" in output["response"] or "polar bear lives in the pole" in output["response"]
    assert "Logical Reasoning" in output["response"]
    assert "polar bear" in output["response"]

def test_end_to_end_french_witty(setup_multilingual_engine):
    reasoner, engine = setup_multilingual_engine
    
    q = "Quelle est la difference entre lion et ours polaire?"
    res = reasoner.process_query(q)
    output = engine.process_response(q, res)
    
    assert output["language"] == "fr"
    assert output["persona"] == "witty_mentor"
    assert any(marker in output["response"] for marker in ["mec", "allez", "hé", "différence", "tu vois"])
    assert "Raisonnement" in output["response"]

def test_multilingual_teaching_and_switching(setup_multilingual_engine):
    reasoner, engine = setup_multilingual_engine
    
    # 1. Teach fact in English in a clean fantasy world
    q1 = "In fantasy world the sun rises from the west."
    res1 = reasoner.process_query(q1)
    output1 = engine.process_response(q1, res1)
    assert output1["language"] == "en"
    assert "saved successfully" in output1["response"] or "success" in output1["response"]
    
    # 2. Query in English in that fantasy world
    q2 = "Where does the sun rise?"
    res2 = reasoner.process_query(q2)
    output2 = engine.process_response(q2, res2)
    assert "west" in output2["response"]
