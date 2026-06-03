import pytest
import networkx as nx
from src.graph_handler import GraphHandler
from src.maintenance.sleep_cycle import CognitiveSleepCycle

def test_sleep_cycle_spelling_merge():
    handler = GraphHandler()
    handler.graph = nx.MultiDiGraph()
    # Add duplicate nodes "أسد" and "اسد"
    handler.graph.add_node("أسد", labels=["أسد"], type="concept")
    handler.graph.add_node("اسد", labels=["اسد"], type="concept")
    
    # Add edges to verify they are migrated
    handler.graph.add_edge("أسد", "لحم", relation="eats", confidence=0.9, type="fact", world="reality")
    handler.graph.add_node("لحم", labels=["لحم"], type="concept")
    
    sleep_cycle = CognitiveSleepCycle(handler)
    merged = sleep_cycle.merge_similar_nodes()
    
    # One of them should be removed, leaving only one node
    assert merged == 1
    assert handler.graph.number_of_nodes() == 2 # "اسد/أسد" and "لحم"
    
    # The remaining node should have labels from both
    remaining_node = list(handler.graph.nodes())[0] if list(handler.graph.nodes())[0] != "لحم" else list(handler.graph.nodes())[1]
    labels = handler.graph.nodes[remaining_node].get("labels", [])
    assert "أسد" in labels or "اسد" in labels
    
    # The eats edge should be preserved from the remaining node to "لحم"
    assert handler.graph.has_edge(remaining_node, "لحم")

def test_sleep_cycle_prune_weak_edges():
    handler = GraphHandler()
    handler.graph = nx.MultiDiGraph()
    handler.graph.add_node("A", type="concept")
    handler.graph.add_node("B", type="concept")
    
    # Confidence < 0.1 should be pruned
    handler.graph.add_edge("A", "B", relation="resembles", confidence=0.05, type="fact", world="reality")
    
    sleep_cycle = CognitiveSleepCycle(handler)
    pruned = sleep_cycle.remove_low_confidence_edges(threshold=0.1)
    
    assert pruned == 1
    assert not handler.graph.has_edge("A", "B")
