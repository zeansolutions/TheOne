import os
import sys
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.response_generator_simple import ResponseGeneratorSimple

def print_banner():
    print("=" * 70)
    print("      نظام عقل منطقي (TheOne - Neuro-Symbolic AI Engine) - MVP      ")
    print("         عقل منطقي صادق وشفاف وخالٍ تماماً من الهلوسة الإحصائية         ")
    print("=" * 70)
    print("الخيارات المتاحة:")
    print(" 1. اسأل النظام أي سؤال باللغة الطبيعية (بالعربية)")
    print(" 2. اعرض شبكة المعرفة الحالية (Concepts & Relations)")
    print(" 3. علم النظام حقيقة جديدة (اضف علاقة في الرسم البياني)")
    print(" 4. اعرض عوالم الحقائق المخزنة")
    print(" 5. خروج")
    print("-" * 70)

def show_graph(handler):
    print("\n--- شبكة المفاهيم والعلاقات الحالية في قاعدة البيانات ---")
    print(f"إجمالي المفاهيم (العقد): {handler.graph.number_of_nodes()}")
    print(f"إجمالي العلاقات والروابط: {handler.graph.number_of_edges()}")
    print("-" * 50)
    
    # Display concepts grouped by category
    categories = {}
    for node, data in handler.graph.nodes(data=True):
        if data.get("type") == "concept":
            cat = data.get("category") or "أخرى"
            lbl = data.get("labels", [node])[0]
            categories.setdefault(cat, []).append(f"{lbl} ({node})")
            
    print("المفاهيم المسجلة:")
    for cat, nodes in categories.items():
        print(f"  * تصنيف [{cat}]: {', '.join(nodes)}")
        
    print("\nالعلاقات والروابط النشطة:")
    for from_node, to_node, data in handler.graph.edges(data=True):
        rel = data.get("relation")
        world = data.get("world", "المعرفة العامة")
        # Get labels
        from_lbl = handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in handler.graph else from_node
        to_lbl = handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in handler.graph else to_node
        print(f"  - [{from_lbl}] --({rel})--> [{to_lbl}]   (عالم: {world})")
    print("-" * 50)

def show_worlds(handler):
    print("\n--- عوالم الحقائق المخزنة في النظام ---")
    worlds = set()
    for _, _, data in handler.graph.edges(data=True):
        if data.get("type") == "fact":
            worlds.add(data.get("world", "reality"))
            
    print(f"العوالم المتاحة: {list(worlds)}")
    print(f"العالم الفعال حالياً: '{handler.active_world}'")
    print("-" * 50)

def teach_system(handler):
    print("\n--- تعليم النظام حقيقة جديدة ---")
    print("تنبيه: سيتم إضافة العلاقة للرسم البياني وتفعيلها فوراً في محرك الاستدلال!")
    print("-" * 50)
    
    # Simple interactive teaching
    print("المفاهيم المتاحة:")
    concepts = [node for node, data in handler.graph.nodes(data=True) if data.get("type") == "concept"]
    for idx, c in enumerate(concepts):
        lbl = handler.graph.nodes[c].get("labels", [c])[0]
        print(f" {idx + 1}. {lbl} ({c})")
        
    try:
        from_idx = int(input("\nاختر المفهوم الأول (المصدر): ")) - 1
        to_idx = int(input("اختر المفهوم الثاني (الهدف): ")) - 1
        
        if 0 <= from_idx < len(concepts) and 0 <= to_idx < len(concepts):
            from_c = concepts[from_idx]
            to_c = concepts[to_idx]
            
            print("\nأنواع العلاقات المتاحة:")
            print(" 1. is_a (تصنيف فرعي)")
            print(" 2. lives_in (يعيش في)")
            print(" 3. has_property (يمتلك خاصية)")
            print(" 4. requires (يستدعي / يحتاج)")
            print(" 5. provides (يوفر)")
            
            rel_choice = input("اختر رقم العلاقة: ")
            rel_map = {
                "1": "is_a",
                "2": "lives_in",
                "3": "has_property",
                "4": "requires",
                "5": "provides"
            }
            rel = rel_map.get(rel_choice, "has_property")
            
            world_choice = input("ما هو العالم الذي تنتمي إليه هذه الحقيقة؟ (افتراضياً reality): ") or "reality"
            
            # Add to graph
            handler.graph.add_edge(
                from_c,
                to_c,
                relation=rel,
                world=world_choice,
                type="fact",
                confidence=1.0
            )
            
            print(f"\nتم بنجاح! إضافة العلاقة: [{handler.graph.nodes[from_c].get('labels')[0]}] --({rel})--> [{handler.graph.nodes[to_c].get('labels')[0]}] في العالم '{world_choice}'")
        else:
            print("اختيار غير صالح.")
    except Exception as e:
        print(f"خطأ أثناء التعليم: {e}")

def main():
    # 1. Initialize databases
    handler = GraphHandler()
    
    ontology_path = "data/animals_ontology_small.json"
    facts_path = "data/animals_facts.json"
    language_rules_path = "data/animals_language_rules.json"
    
    # Resolve paths relative to working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(ontology_path):
        ontology_path = os.path.join(base_dir, ontology_path)
        facts_path = os.path.join(base_dir, facts_path)
        language_rules_path = os.path.join(base_dir, language_rules_path)
        
    try:
        handler.load_databases(ontology_path, facts_path, language_rules_path)
    except Exception as e:
        print(f"خطأ في تحميل قواعد البيانات: {e}")
        sys.exit(1)
        
    reasoner = SimpleReasoner(handler)
    generator = ResponseGeneratorSimple(handler)
    
    # Print welcome
    print_banner()
    
    while True:
        choice = input("\nاختر رقماً من القائمة (1-5): ").strip()
        
        if choice == "1":
            query = input("\nاسأل عقل منطقي (مثال: 'هل الأسد حيوان؟' أو 'لو الأسد في القطب ماذا يحتاج؟'): ").strip()
            if not query:
                continue
                
            # Run pipeline
            res = reasoner.process_query(query)
            response = generator.generate(res)
            
            print("\n" + "=" * 50)
            print(f"العالم النشط: '{handler.active_world}'")
            print(f"الرد النهائي:\n👉 {response}")
            print("=" * 50)
            
            # Print logical trace
            print("\n📋 مسار الاستدلال المنطقي والتتبع:")
            for idx, step in enumerate(res.get("trace", [])):
                print(f"  [{idx + 1}] {step}")
            print(f"🎯 معامل اليقين/الثقة: {res.get('confidence', 1.0):.2f}")
            print("=" * 50)
            
        elif choice == "2":
            show_graph(handler)
        elif choice == "3":
            teach_system(handler)
        elif choice == "4":
            show_worlds(handler)
        elif choice == "5" or choice.lower() == "q":
            print("\nشكراً لك! إلى اللقاء في جلسة تفكير جديدة.")
            break
        else:
            print("اختيار غير صحيح، يرجى إدخال رقم بين 1 و 5.")

if __name__ == "__main__":
    main()
