import pytest
from src.graph_handler import GraphHandler
from src.reasoner.curiosity_engine import CuriosityEngine

def test_curiosity_mystery_score():
    handler = GraphHandler()
    handler.load_databases(
        "data/animals_ontology_small.json",
        "data/animals_facts.json",
        "data/animals_language_rules.json"
    )
    
    engine = CuriosityEngine(handler)
    
    # Calculate mystery score for polar_bear
    score = engine.calculate_mystery_score("polar_bear")
    
    # polar bear has taxonomy (is_a feline_carnivore or animal, depth is known), degree is high, so mystery score should be low
    assert score < 100.0
    
    # Add a completely new, empty concept
    handler.graph.add_node("mystery_concept", labels=["مفهوم غامض"], category="animal", type="concept")
    
    # Newly added concept with degree 0 should have a very high mystery score
    new_score = engine.calculate_mystery_score("mystery_concept")
    assert new_score > 70.0
    
    # Generate curiosity questions
    questions = engine.generate_questions(limit=15, lang="ar")
    assert len(questions) > 0
    # The new concept should be one of the top gaps
    concepts_in_questions = [q["concept"] for q in questions]
    assert "mystery_concept" in concepts_in_questions
    assert questions[0]["question"].startswith("ما هو") or questions[0]["question"].startswith("ما هي")
