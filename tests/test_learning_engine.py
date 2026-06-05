import os
import json
import pytest
import shutil
from src.graph_handler import GraphHandler
from src.reasoner.learning_engine import InteractiveBootstrapper
from src.reasoner.pattern_matcher import GenericPatternMatcher

@pytest.fixture
def setup_rules_and_handler(tmp_path):
    # Copy animals rules to a temp file so we can modify it
    src_rules = "tests/mock_data/animals_language_rules.json"
    temp_rules_path = str(tmp_path / "temp_rules.json")
    shutil.copy(src_rules, temp_rules_path)
    
    handler = GraphHandler()
    ontology_path = "tests/mock_data/animals_ontology_small.json"
    facts_path = "tests/mock_data/animals_facts.json"
    handler.load_databases(ontology_path, facts_path, temp_rules_path)
    
    return handler, temp_rules_path

def test_learn_new_pattern_simulation(setup_rules_and_handler):
    handler, rules_path = setup_rules_and_handler
    bootstrapper = InteractiveBootstrapper(handler, rules_path)
    
    # 1. Ask for clarification on an unknown phrasing in non-interactive mode.
    # In non-interactive mode, it simulates selection/learning
    # "الأسد ده إيه بالظبط؟" is a classification-like query
    proposal = bootstrapper.ask_for_clarification("الأسد ده إيه بالظبط؟", user_response="نعم", interactive=False)
    assert proposal is not None
    assert "pattern" in proposal
    assert proposal["intent"] == "classification"
    
    # 2. Check if the rules file was actually updated
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Check semantic_frames which is where we save learned rules
        patterns = data.get("semantic_frames", [])
        pattern_ids = [p.get("id") for p in patterns]
        assert any(pid.startswith("learned_classification_") for pid in pattern_ids)

def test_learned_pattern_reuse(setup_rules_and_handler):
    handler, rules_path = setup_rules_and_handler
    bootstrapper = InteractiveBootstrapper(handler, rules_path)
    
    # Run learning on "الأسد ده إيه؟"
    bootstrapper.ask_for_clarification("الأسد ده إيه؟", user_response="نعم", interactive=False)
    
    # Load matcher with updated rules
    matcher = GenericPatternMatcher(rules_path)
    
    # Now it should match a similar structure: "الدب القطبي ده إيه؟"
    result = matcher.match("الدب القطبي ده إيه؟")
    assert result is not None
    assert result.intent == "classification"
    assert result.extracted_entities.get("concept") == "الدب القطبي"
