import os
import sys
import json

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine

def run_tests():
    # Initialize components
    handler = GraphHandler()
    
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ontology_path = os.path.join(project_dir, "data", "ontology.json")
    facts_path = os.path.join(project_dir, "data", "facts.json")
    language_rules_path = os.path.join(project_dir, "data", "language_rules.json")
    inference_rules_path = os.path.join(project_dir, "data", "inference_rules.json")
    
    print("Loading databases...")
    handler.load_databases(ontology_path, facts_path, language_rules_path, inference_rules_path)
    
    # Set the active world to "arabic_language_teacher"
    handler.set_active_world("arabic_language_teacher")
    print(f"Active world set to: {handler.active_world}")
    
    reasoner = SimpleReasoner(handler)
    engine = MultilingualPersonaEngine(handler)
    
    # Define queries to test in Arabic
    queries = [
        # 1. Grammar role cases
        "هل المبتدأ مرفوع؟",
        "هل الخبر مرفوع؟",
        "هل الفاعل مرفوع؟",
        "هل المفعول به منصوب؟",
        # 2. Part of speech inheritance
        "هل الطالب اسم؟",
        "هل الكتاب اسم؟",
        "هل يقرأ فعل؟",
        # 3. Case capability & exclusions (Prohibitions)
        "هل الاسم يجر؟",
        "هل الاسم يجزم؟",
        "هل الفعل يجزم؟",
        "هل الفعل يجر؟",
        # 4. Declinable vs Indeclinable (Behavior)
        "هل المعرب يتغير آخره؟",
        "هل المبني يلزم حركة واحدة؟",
        # 5. Copular Verbs (كان وأخواتها) and Particles (إن وأخواتها)
        "ما هي الحالة الإعرابية لاسم كان؟",
        "ما هي الحالة الإعرابية لخبر كان؟",
        "ما هي الحالة الإعرابية لاسم إن؟",
        "ما هي الحالة الإعرابية لخبر إن؟"
    ]
    
    results = []
    
    for query in queries:
        print(f"\nProcessing query: {query}")
        # Run logical reasoning
        res = reasoner.process_query(query, language="ar")
        # Run multilingual persona output generator
        persona_output = engine.process_response(query, res)
        
        results.append({
            "query": query,
            "reasoner_res": res,
            "persona_output": persona_output
        })
        
        print(f"Result Type: {res.get('type')}")
        print(f"Logical Outcome (result): {res.get('result')}")
        print("Reasoning Chain (trace):")
        for step in res.get("trace", []):
            print(f"  - {step}")
        print(f"Natural Response (Arabic): {persona_output.get('response')}")
        print("-" * 60)
        
    # Let's save results in a structured markdown file
    output_md_path = os.path.join(project_dir, "artifacts", "arabic_test_results.md")
    os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
    
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("# Arabic Grammar Reasoning Engine Test Report\n\n")
        f.write("This report presents the validation results of the LEGEND Neuro-Symbolic Cognitive Reasoning Engine ")
        f.write("on rules and facts belonging to the **Arabic Language Teacher (`arabic_language_teacher`)** world.\n\n")
        f.write("## Test Summary Table\n\n")
        f.write("| Arabic Question (السؤال) | Query Type | Logical Result | Natural Persona Response (الرد) | Reasoner Trace Steps (سلسلة الاستدلال) |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        
        for r in results:
            q = r["query"]
            res_type = r["reasoner_res"].get("type", "unknown")
            logic_val = "✅ True" if r["reasoner_res"].get("result") else "❌ False"
            resp = r["persona_output"].get("response", "").replace("\n", " ")
            trace_steps = "<br>".join(r["reasoner_res"].get("trace", []))
            f.write(f"| {q} | {res_type} | {logic_val} | {resp} | {trace_steps} |\n")
            
        f.write("\n## Detailed Logs\n\n")
        for r in results:
            f.write(f"### Question: {r['query']}\n\n")
            f.write(f"- **Query Type:** `{r['reasoner_res'].get('type')}`\n")
            f.write(f"- **Result:** `{r['reasoner_res'].get('result')}`\n")
            f.write("- **Trace (سلسلة الاستدلال):**\n")
            for step in r["reasoner_res"].get("trace", []):
                f.write(f"  - {step}\n")
            f.write(f"- **Response (الرد):**\n\n> {r['persona_output'].get('response')}\n\n")
            
    print(f"\nSaved test results report to: {output_md_path}")

if __name__ == "__main__":
    run_tests()
