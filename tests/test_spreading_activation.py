import os
import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner

@pytest.fixture
def setup_reasoner():
    handler = GraphHandler()
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    ontology_path = os.path.join(project_dir, "data", "animals_ontology_small.json")
    facts_path = os.path.join(project_dir, "data", "animals_facts.json")
    language_rules_path = os.path.join(project_dir, "data", "animals_language_rules.json")
    
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    reasoner = SimpleReasoner(handler)
    return reasoner, handler

def test_spreading_activation_direct(setup_reasoner):
    reasoner, handler = setup_reasoner
    
    # 1. Spreading from animal
    activations = handler.spreading_activation(["animal"], max_steps=2)
    # Check that c_eye_human has activation because of the relation: c_eye_human --is_part_of--> animal
    assert "c_eye_human" in activations
    # c_spring_water should not have activation from 'animal' (or very low/zero compared to c_eye_human)
    assert activations.get("c_eye_human", 0.0) > activations.get("c_spring_water", 0.0)

    # 2. Spreading from savanna
    activations = handler.spreading_activation(["savanna"], max_steps=2)
    # Check that c_spring_water has activation because of: c_spring_water --located_in--> savanna
    assert "c_spring_water" in activations
    assert activations.get("c_spring_water", 0.0) > activations.get("c_eye_human", 0.0)

def test_homograph_disambiguation_human_eye(setup_reasoner):
    reasoner, handler = setup_reasoner
    
    # Clear conversation history
    reasoner.conversation_manager.clear()
    
    # First turn: Question about animal/lion
    # This maps feline_carnivore (lion) and animal (animal) to conversation context
    q1 = "هل الأسد حيوان؟"
    res1 = reasoner.process_query(q1)
    
    # Verify the first turn registered mapped concepts
    assert "feline_carnivore" in res1["concept1"] or "feline_carnivore" in res1["concept2"]
    
    # Second turn: Question containing the ambiguous word "عين"
    # The word "العين" should resolve to c_eye_human because it is connected to animal/lion
    q2 = "ما هي وظيفة العين؟"
    res2 = reasoner.process_query(q2)
    
    # Let's inspect the active concept in the last turn
    last_turn_concepts = reasoner.conversation_manager.history[-1]["concepts"]
    assert "c_eye_human" in last_turn_concepts
    assert "c_spring_water" not in last_turn_concepts

def test_homograph_disambiguation_water_spring(setup_reasoner):
    reasoner, handler = setup_reasoner
    
    # Clear conversation history
    reasoner.conversation_manager.clear()
    
    # First turn: Question about Savanna
    # This maps savanna to conversation context
    q1 = "أين يعيش الأسد؟"  # In savanna
    res1 = reasoner.process_query(q1)
    
    # Verify savanna is in mapped concepts or resolved location
    assert res1["location"] == "savanna"
    
    # Ensure savanna is recorded in conversation history concepts
    # (since the answer/response is recorded, or it was mapped in previous turns)
    # Let's record a turn with savanna explicitly to simulate savanna context
    reasoner.conversation_manager.record_turn("هل السافانا حارة؟", ["savanna"])
    
    # Second turn: Question containing the ambiguous word "عين"
    # The word "عين" should resolve to c_spring_water because savanna is in the context
    q2 = "هل توجد عين ماء هناك؟"
    res2 = reasoner.process_query(q2)
    
    last_turn_concepts = reasoner.conversation_manager.history[-1]["concepts"]
    assert "c_spring_water" in last_turn_concepts
    assert "c_eye_human" not in last_turn_concepts
