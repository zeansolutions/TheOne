import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine

handler = GraphHandler()
handler.load_databases("data/ontology.json", "data/facts.json", "data/language_rules.json")
reasoner = SimpleReasoner(handler)
persona_engine = MultilingualPersonaEngine(handler)

res = reasoner.process_query("ما العلاقة بين الاسد والغزالة", language="ar")
print("Reasoner res:", res)
engine_res = persona_engine.process_response("ما العلاقة بين الاسد والغزالة", res, user_preference="ar", force_persona_id="scientist")
print("Response:", engine_res["response"])

res2 = reasoner.process_query("ما العلاقة بين النورس والاسماك", language="ar")
print("Reasoner res2:", res2)
engine_res2 = persona_engine.process_response("ما العلاقة بين النورس والاسماك", res2, user_preference="ar", force_persona_id="scientist")
print("Response2:", engine_res2["response"])

