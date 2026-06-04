import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner

@pytest.fixture
def setup_reasoner():
    handler = GraphHandler()
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "tests", "mock_data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "tests", "mock_data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "tests", "mock_data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    return reasoner, handler

def test_inference_rules_loading(setup_reasoner):
    _, handler = setup_reasoner
    
    # Check that rules were loaded from JSON
    assert len(handler.inference_rules) >= 3
    rule_ids = [r["id"] for r in handler.inference_rules]
    assert "transitive_is_a" in rule_ids
    assert "property_inheritance" in rule_ids
    assert "environment_requirement" in rule_ids

def test_forward_chaining_is_a_transitive(setup_reasoner):
    reasoner, handler = setup_reasoner
    
    # Run chainer on reality
    handler.infer_facts("reality")
    
    # Assert transitive edge was created: feline_carnivore (lion) -> animal
    # (since feline_carnivore is_a carnivore and carnivore is_a animal)
    has_transitive = False
    for _, target, data in handler.graph.out_edges("feline_carnivore", data=True):
        if target == "animal" and data.get("relation") == "is_a" and data.get("type") == "inferred":
            has_transitive = True
            assert "التعدي التصنيفي" in data.get("reason", "")
            break
    assert has_transitive is True

def test_forward_chaining_property_inheritance(setup_reasoner):
    reasoner, handler = setup_reasoner
    
    # Run chainer on reality
    handler.infer_facts("reality")
    
    # Assert property inheritance edge was created: feline_carnivore -> thin_fur
    # (since feline_carnivore is_a feline_carnivore which has thin_fur, or polar_bear is_a polar_bear which has thick_fur)
    # Let's verify polar_bear inherits from itself or parent. Wait, polar_bear is_a carnivore.
    # carnivore does not have property thick_fur directly. polar_bear has it.
    # Let's check polar_bear property inheritance or feline_carnivore property
    # Let's verify is_a transitive has created polar_bear -> animal.
    # Does polar_bear inherit property from animal? Animal has no properties.
    # What about feline_carnivore? It has thin_fur in ontology.
    # Let's add a test concept to verify inheritance:
    # Let's say: animal has_property has_cell.
    handler.graph.add_node("has_cell", type="concept", labels=["خلايا"])
    handler.graph.add_edge("animal", "has_cell", relation="has_property", type="relation")
    
    # Run chainer again
    handler.infer_facts("reality")
    
    # Now polar_bear (is_a carnivore is_a animal) should inherit 'has_cell'
    has_inherited = False
    for _, target, data in handler.graph.out_edges("polar_bear", data=True):
        if target == "has_cell" and data.get("relation") == "has_property" and data.get("type") == "inferred":
            has_inherited = True
            assert "يرث خاصية" in data.get("reason", "")
            break
    assert has_inherited is True

def test_custom_rule_at_runtime(setup_reasoner):
    reasoner, handler = setup_reasoner
    
    # 1. Add a custom rule to the engine
    # Rule: (?x, eats, ?y) -> (?x, is_a, living_thing)
    custom_rule = {
        "id": "eats_implies_living",
        "name": "التغذية تعني الكينونة الحية",
        "conditions": [
            {"subject": "?x", "relation": "eats", "object": "?y"}
        ],
        "conclusion": {
            "subject": "?x",
            "relation": "is_a",
            "object": "living_thing"
        }
    }
    handler.inference_rules.append(custom_rule)
    
    # 2. Add concepts and facts
    handler.graph.add_node("living_thing", type="concept", labels=["كائن حي"])
    handler.graph.add_node("meat", type="concept", labels=["لحم"])
    handler.graph.add_edge("feline_carnivore", "meat", relation="eats", type="fact", world="reality", confidence=1.0)
    
    # 3. Run chainer
    handler.infer_facts("reality")
    
    # 4. Assert inferred fact: feline_carnivore is_a living_thing
    has_inferred = False
    for _, target, data in handler.graph.out_edges("feline_carnivore", data=True):
        if target == "living_thing" and data.get("relation") == "is_a" and data.get("type") == "inferred":
            has_inferred = True
            break
    assert has_inferred is True
