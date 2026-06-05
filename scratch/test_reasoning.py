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
    generator = ResponseGeneratorSimple(handler)
    
    print(f"\nQuery: {query_text}")
    res = reasoner.process_query(query_text, language=lang)
    print(f"Reasoner Result: {res}")
    
    response = generator.generate(res, language=lang)
    print(f"Generated Response: {response}")

if __name__ == "__main__":
    run_test_query("هل الانسان كائن حي؟")
    run_test_query("ما العلاقة بين الاسد والغزالة")
    run_test_query("ما العلاقة بين النورس والاسماك")
    run_test_query("ما العلاقة العميقة بين النورس والاسماك")
