import pytest
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner

def test_sandbox_isolation():
    handler = GraphHandler()
    handler.load_databases(
        "tests/mock_data/animals_ontology_small.json",
        "tests/mock_data/animals_facts.json",
        "tests/mock_data/animals_language_rules.json"
    )
    
    reasoner = SimpleReasoner(handler)
    
    # Original graph has polar_bear lives_in polar_bear_env (which is arctic/polar_bear_env)
    # Check that polar_bear does NOT live in savanna (savanna)
    savanna_check = False
    for _, target, data in handler.graph.out_edges("polar_bear", data=True):
        if data.get("relation") == "lives_in" and target == "savanna":
            savanna_check = True
    assert not savanna_check
    
    # Let's process a hypothetical query: "لو كان الدب القطبي يعيش في السافانا، هل الدب القطبي يعيش في السافانا؟"
    res = reasoner.process_query("لو كان الدب القطبي يعيش في السافانا، هل الدب القطبي يعيش في السافانا؟", language="ar")
    
    # Sandbox result should be True
    assert res.get("type") == "location"
    assert res.get("result") is True
    assert res.get("location") == "savanna"
    assert res.get("is_sandbox") is True
    
    # After query exits, verify that the original graph is UNCHANGED
    savanna_check_after = False
    for _, target, data in handler.graph.out_edges("polar_bear", data=True):
        if data.get("relation") == "lives_in" and target == "savanna":
            savanna_check_after = True
    assert not savanna_check_after
