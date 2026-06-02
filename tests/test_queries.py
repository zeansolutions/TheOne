import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

@pytest.fixture
def setup_engine():
    handler = GraphHandler()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    generator = ResponseGeneratorSimple(handler)
    return reasoner, generator

def test_query_classification_animal(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("هل الأسد حيوان؟")
    assert res["type"] == "classification"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "أسد هو حيوان" in response or "الأسد هو حيوان" in response

def test_query_classification_predator(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("هل الأسد مفترس؟")
    assert res["type"] == "classification"
    assert res["result"] is True
    
    response = generator.generate(res)
    assert "أسد هو مفترس" in response or "الأسد هو مفترس" in response

def test_query_location(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("أين يعيش الأسد؟")
    assert res["type"] == "location"
    assert res["location"] == "savanna"
    
    response = generator.generate(res)
    assert "السافانا" in response

def test_query_hypothetical(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("لو الأسد عاش في القطب، ماذا يحتاج؟")
    assert res["type"] == "hypothetical"
    assert res["needs_adaptation"] is True
    assert res["transferred_property"] == "thick_fur"
    assert res["analogy_candidate"] == "polar_bear"
    
    response = generator.generate(res)
    assert "فرو سميك" in response
    assert "دب قطبي" in response

def test_query_comparison(setup_engine):
    reasoner, generator = setup_engine
    
    res = reasoner.process_query("ما الفرق بين الأسد والدب القطبي؟")
    assert res["type"] == "comparison"
    
    response = generator.generate(res)
    assert "أسد" in response
    assert "دب قطبي" in response
    assert "فرو خفيف" in response or "فرو خفيف" in response or "فرو سميك" in response
