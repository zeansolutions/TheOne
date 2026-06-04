import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner

@pytest.fixture
def setup_engine():
    handler = GraphHandler()
    
    # Resolve paths relative to tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "tests", "mock_data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "tests", "mock_data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "tests", "mock_data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    return handler, reasoner

def test_dynamic_morphological_lookup(setup_engine):
    handler, _ = setup_engine
    
    # Test prefix stripping and direct lookup
    assert handler.dynamic_morphological_lookup("الأسد") == "feline_carnivore"
    assert handler.dynamic_morphological_lookup("أسود") == "feline_carnivore"
    assert handler.dynamic_morphological_lookup("الدب") == "polar_bear"
    assert handler.dynamic_morphological_lookup("بالقطب") == "arctic"

def test_is_a_relationship(setup_engine):
    _, reasoner = setup_engine
    
    # Direct relation
    res = reasoner.check_is_a_relationship("feline_carnivore", "carnivore")
    assert res["result"] is True
    
    # Transitive inheritance (Lion -> Carnivore -> Animal)
    res = reasoner.check_is_a_relationship("feline_carnivore", "animal")
    assert res["result"] is True
    
    # Negative case
    res = reasoner.check_is_a_relationship("feline_carnivore", "polar_bear")
    assert res["result"] is False

def test_inheritance_deduction(setup_engine):
    _, reasoner = setup_engine
    
    # Lion inherits from carnivore which inherits from animal
    # Let's verify that
    res = reasoner.check_is_a_relationship("feline_carnivore", "animal")
    assert res["result"] is True

def test_causal_reasoning(setup_engine):
    _, reasoner = setup_engine
    
    # Lion in reality is in savanna and has thin fur.
    # What happens if we evaluate lion in the arctic environment?
    res = reasoner.causal_reasoning("feline_carnivore", "arctic")
    assert res["needs_adaptation"] is True
    assert res["requirement"] == "good_insulation"

def test_analogical_reasoning(setup_engine):
    _, reasoner = setup_engine
    
    # Let's perform analogy transfer for lion in arctic for good_insulation
    res = reasoner.analogical_reasoning("feline_carnivore", "arctic", "good_insulation")
    assert res["success"] is True
    assert res["analogy_candidate"] == "polar_bear"
    assert res["transferred_property"] == "thick_fur"
