import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

def run_test_query(query_text, lang="ar"):
    handler = GraphHandler()
    handler.load_databases(
        "data/ontology.json",
        "data/facts.json",
        "data/language_rules.json"
    )
    reasoner = SimpleReasoner(handler)
    
    print(f"\nQuery: {query_text} (lang: {lang})")
    res = reasoner.process_query(query_text, language=lang)
    print(f"Reasoner Result:")
    import pprint
    pprint.pprint(res)

if __name__ == "__main__":
    run_test_query("ما هي الشمس؟", "ar")
    run_test_query("what is sun?", "en")
    run_test_query("ماذا تعرف عن الشمس؟", "ar")
