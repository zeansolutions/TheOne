import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner

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
    return handler, reasoner

def get_world_facts(handler, concept_id, world):
    return [
        (v, data.get("relation"))
        for _, v, data in handler.graph.out_edges(concept_id, data=True)
        if data.get("type") == "fact" and data.get("world") == world and data.get("status", "active") == "active"
    ]

def test_identical_fact_handling(setup_engine):
    handler, reasoner = setup_engine
    
    # 1. Add fact that is already there in reality
    # feline_carnivore lives_in savanna is fact_1 in reality
    res = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="savanna",
        relation="lives_in",
        world="reality",
        confidence=1.0,
        interactive=False
    )
    assert res["status"] == "identical"
    assert "موجودة بالفعل" in res["message"]

def test_auto_resolution_replace_higher_confidence(setup_engine):
    handler, reasoner = setup_engine
    
    # 1. Add initial fact with confidence 1.0
    res1 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="arctic",
        relation="lives_in",
        world="custom_world",
        confidence=1.0,
        interactive=False
    )
    assert res1["status"] == "added"
    
    # 2. Add conflicting fact with confidence 1.5 (> 1.0 + 0.3)
    res2 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="savanna",
        relation="lives_in",
        world="custom_world",
        confidence=1.5,
        interactive=False
    )
    assert res2["status"] == "auto_replaced"
    assert "تلقائياً" in res2["message"]
    
    # Check that new fact is active and old one is removed
    facts = get_world_facts(handler, "feline_carnivore", "custom_world")
    destinations = [obj for obj, rel in facts if rel == "lives_in"]
    assert "savanna" in destinations
    assert "arctic" not in destinations

def test_auto_resolution_reject_lower_confidence(setup_engine):
    handler, reasoner = setup_engine
    
    # 1. Add initial fact with confidence 1.0
    res1 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="arctic",
        relation="lives_in",
        world="custom_world",
        confidence=1.0,
        interactive=False
    )
    assert res1["status"] == "added"
    
    # 2. Add conflicting fact with confidence 0.5 (< 1.0 - 0.3)
    res2 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="savanna",
        relation="lives_in",
        world="custom_world",
        confidence=0.5,
        interactive=False
    )
    assert res2["status"] == "auto_rejected"
    assert "رفض" in res2["message"]
    
    # Check that old fact is still active and new one is rejected
    facts = get_world_facts(handler, "feline_carnivore", "custom_world")
    destinations = [obj for obj, rel in facts if rel == "lives_in"]
    assert "arctic" in destinations
    assert "savanna" not in destinations

def test_non_interactive_fallback(setup_engine):
    handler, reasoner = setup_engine
    
    # 1. Add initial fact with confidence 1.0
    res1 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="savanna",
        relation="lives_in",
        world="custom_world",
        confidence=1.0,
        interactive=False
    )
    assert res1["status"] == "added"
    
    # 2. Add conflicting fact with confidence 1.0 (equal confidence, interactive=False)
    res2 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="arctic",
        relation="lives_in",
        world="custom_world",
        confidence=1.0,
        interactive=False
    )
    assert res2["status"] == "non_interactive_rejected"
    assert "تجاهل" in res2["message"]
    
    # Check that old fact is preserved and new one rejected
    facts = get_world_facts(handler, "feline_carnivore", "custom_world")
    destinations = [obj for obj, rel in facts if rel == "lives_in"]
    assert "savanna" in destinations
    assert "arctic" not in destinations

def test_opposite_properties_contradiction(setup_engine):
    handler, reasoner = setup_engine
    
    # 1. Add thin_fur property in a custom world with confidence 1.0
    res1 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="thin_fur",
        relation="has_property",
        world="custom_world",
        confidence=1.0,
        interactive=False
    )
    assert res1["status"] == "added"
    
    # 2. Add thick_fur (which is opposite of thin_fur) with confidence 1.5
    res2 = handler.add_or_update_fact(
        subj="feline_carnivore",
        obj="thick_fur",
        relation="has_property",
        world="custom_world",
        confidence=1.5,
        interactive=False
    )
    assert res2["status"] == "auto_replaced"
    
    # Verify the property was replaced
    facts = get_world_facts(handler, "feline_carnivore", "custom_world")
    props = [obj for obj, rel in facts if rel == "has_property"]
    assert "thick_fur" in props
    assert "thin_fur" not in props
