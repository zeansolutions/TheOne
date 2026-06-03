import pytest
import networkx as nx
from src.graph_handler import GraphHandler
from src.reasoner.transitive_chaining import TransitiveChainingEngine

def test_transitive_chaining_basic():
    handler = GraphHandler()
    # Populate a simple graph manually
    handler.graph = nx.MultiDiGraph()
    handler.graph.add_node("A", labels=["أ"], type="concept")
    handler.graph.add_node("B", labels=["ب"], type="concept")
    handler.graph.add_node("C", labels=["ج"], type="concept")
    
    # Add transitive relation is_a
    handler.graph.add_edge("A", "B", relation="is_a", confidence=1.0, type="fact", world="reality")
    handler.graph.add_edge("B", "C", relation="is_a", confidence=0.9, type="fact", world="reality")
    
    engine = TransitiveChainingEngine(handler)
    inferences = engine.apply_transitive_rules("reality")
    
    # Should infer A is_a C
    found = False
    for sub, rel, obj, conf, desc in inferences:
        if sub == "A" and rel == "is_a" and obj == "C":
            found = True
            # decay for is_a is 0.0, so confidence should be 1.0 * 0.9 * (1 - 0.0) = 0.9
            assert abs(conf - 0.9) < 1e-5
            assert "A" in desc or "أ" in desc
            assert "C" in desc or "ج" in desc
    assert found

def test_transitive_chaining_decay():
    handler = GraphHandler()
    handler.graph = nx.MultiDiGraph()
    handler.graph.add_node("A", labels=["أ"], type="concept")
    handler.graph.add_node("B", labels=["ب"], type="concept")
    handler.graph.add_node("C", labels=["ج"], type="concept")
    
    # Add causes relation (decay = 0.1)
    handler.graph.add_edge("A", "B", relation="causes", confidence=1.0, type="fact", world="reality")
    handler.graph.add_edge("B", "C", relation="causes", confidence=0.8, type="fact", world="reality")
    
    engine = TransitiveChainingEngine(handler)
    inferences = engine.apply_transitive_rules("reality")
    
    found = False
    for sub, rel, obj, conf, desc in inferences:
        if sub == "A" and rel == "causes" and obj == "C":
            found = True
            # confidence should decay by (1 - 0.1) = 0.9
            # conf = 1.0 * 0.8 * 0.9 = 0.72
            assert abs(conf - 0.72) < 1e-5
    assert found
