import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

handler = GraphHandler()
handler.load_databases(
    "data/ontology.json",
    "data/facts.json",
    "data/language_rules.json"
)
reasoner = SimpleReasoner(handler)
generator = ResponseGeneratorSimple(handler)

handler.add_or_update_fact("اسد", "حمار", "eats", "reality", 1.0)
handler.add_or_update_fact("انسان", "رأس", "contains", "reality", 1.0)
handler.add_or_update_fact("رأس", "انسان", "part_of", "reality", 1.0)
handler.add_or_update_fact("رأس", "مستديرة", "has_property", "reality", 1.0)
handler.add_or_update_fact("كرة", "مستديرة", "has_property", "reality", 1.0)

def query(q, is_deep=False):
    print(f"\nQuery: {q} (is_deep={is_deep})")
    # Let's inspect the internal parsing step
    words = q.replace("؟", "").strip().split()
    mapped_concepts = []
    for w in words:
        concept = handler.dynamic_morphological_lookup(w, "ar")
        if concept:
            mapped_concepts.append(concept)
    print(f"Internal Mapped Concepts: {mapped_concepts}")
    
    res = reasoner.process_query(q, language="ar", is_deep=is_deep)
    print(f"Result Type: {res.get('type')}, Result: {res.get('result')}")
    print(f"Trace: {res.get('trace')}")
    response = generator.generate(res, language="ar")
    print(f"Response: {response}")

query("هل الاسد يأكل حمار؟")
query("هل الانسان يمتلك رأس؟")
query("هل رأس الانسان مستديرة؟")
query("ما العلاقة بين الانسان والكرة؟")
query("ما العلاقة بين الانسان والكرة؟", is_deep=True)
