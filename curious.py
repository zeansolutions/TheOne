import argparse
from src.graph_handler import GraphHandler
from src.reasoner.curiosity_engine import CuriosityEngine

def main():
    parser = argparse.ArgumentParser(description="Active Curiosity Engine for TheOne")
    parser.add_argument("--limit", type=int, default=5, help="Number of questions to show")
    parser.add_argument("--lang", type=str, default="ar", help="Language for questions")
    args = parser.parse_args()

    handler = GraphHandler()
    handler.load_databases(
        "data/ontology.json",
        "data/facts.json",
        "data/language_rules.json"
    )

    engine = CuriosityEngine(handler)
    questions = engine.generate_questions(limit=args.limit, lang=args.lang)
    
    if not questions:
        print("✨ النظام لا يعاني من أي فجوات معرفية حالياً!")
        return

    print("🤔 لدي فضول لمعرفة المزيد حول هذه المفاهيم:")
    for i, q in enumerate(questions):
        print(f" {i+1}. {q['question']} (معدل الغموض: {q['mystery_score']:.1f}%)")

if __name__ == "__main__":
    main()
