import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner

@pytest.fixture
def setup_reasoner():
    handler = GraphHandler()
    ontology_path = "tests/mock_data/animals_ontology_small.json"
    facts_path = "tests/mock_data/animals_facts.json"
    rules_path = "tests/mock_data/animals_language_rules.json"
    handler.load_databases(ontology_path, facts_path, rules_path)
    reasoner = SimpleReasoner(handler)
    return reasoner

def test_nlp_mode_library_routing(setup_reasoner):
    reasoner = setup_reasoner
    
    # 1. Set mode to library
    reasoner.handler.nlp_mode = "library"
    assert reasoner.handler.nlp_mode == "library"
    
    # Check that reasoner parses and reasons correctly in library mode
    # A standard query: "هل الأسد حيوان؟"
    res = reasoner.process_query("هل الأسد حيوان؟", language="ar")
    assert res is not None
    assert res.get("type") == "classification"
    assert res.get("result") is True

def test_nlp_mode_database_routing(setup_reasoner):
    reasoner = setup_reasoner
    
    # 1. Set mode to database
    reasoner.handler.nlp_mode = "database"
    assert reasoner.handler.nlp_mode == "database"
    
    # Check that reasoner parses and reasons correctly in database mode
    # A standard query: "هل الأسد حيوان؟"
    res = reasoner.process_query("هل الأسد حيوان؟", language="ar")
    assert res is not None
    assert res.get("type") == "classification"
    assert res.get("result") is True
