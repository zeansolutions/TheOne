import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_handler import GraphHandler

handler = GraphHandler()
handler.load_databases(
    "data/ontology.json",
    "data/facts.json",
    "data/language_rules.json"
)

handler.add_or_update_fact("انسان", "رأس", "contains", "reality", 1.0)

print("Nodes in graph:", list(handler.graph.nodes()))
print("Edges for انسان:", handler.graph.out_edges("انسان", data=True))
print("Edges for رأس:", handler.graph.out_edges("رأس", data=True))
print("has_edge(انسان, رأس):", handler.graph.has_edge("انسان", "رأس"))
print("has_edge(رأس, انسان):", handler.graph.has_edge("رأس", "انسان"))
