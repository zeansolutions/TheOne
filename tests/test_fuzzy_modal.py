import pytest
from src.enrichment.fuzzy_modal import FuzzyModalEngine
from src.graph_handler import GraphHandler
from src.world_manager import WorldManager

def test_fuzzy_modal_keyword_detection():
    engine = FuzzyModalEngine()
    
    # Test Arabic
    modality, cleaned = engine.detect_modality("الأسد عادةً يأكل اللحم", "ar")
    assert modality == "usually"
    assert "عادةً" not in cleaned
    
    # Test English
    modality, cleaned = engine.detect_modality("Lions usually eat meat", "en")
    assert modality == "usually"
    assert "usually" not in cleaned

def test_fuzzy_modal_confidence_attenuation():
    handler = GraphHandler()
    handler.load_databases(
        "tests/mock_data/animals_ontology_small.json",
        "tests/mock_data/animals_facts.json",
        "tests/mock_data/animals_language_rules.json"
    )
    
    world_mgr = WorldManager(handler)
    
    # Teach a fact with a modality: "عادةً الأسد يعيش في السافانا"
    # الأسد matches feline_carnivore
    # السافانا matches savanna
    # usually weight is 0.8
    res = world_mgr.parse_and_add_fact("عادةً الأسد يعيش في السافانا", "reality", language="ar")
    
    assert res["success"] is True
    # Verify confidence is decayed (base 1.0 * 0.8 = 0.8)
    edge_data = handler.graph.get_edge_data("feline_carnivore", "savanna")
    # Edge data is a dictionary of keys because it's a MultiDiGraph
    found_conf = None
    for key, data in edge_data.items():
        if data.get("relation") == "lives_in" and data.get("world") == "reality":
            found_conf = data.get("confidence")
            assert data.get("modality") == "usually"
            
    assert found_conf is not None
    assert abs(found_conf - 0.8) < 1e-5
