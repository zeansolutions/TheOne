import os
import sys
import time
import argparse
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine

# Default CLI Language
active_lang = "en"

# Multilingual Translations dictionary for CLI
# Load translations from JSON
import json
base_dir = os.path.dirname(os.path.abspath(__file__))
translations_path = os.path.join(base_dir, "config", "cli_translations.json")
try:
    with open(translations_path, "r", encoding="utf-8") as f:
        translations = json.load(f)
except Exception as e:
    print(f"Warning: could not load translations: {e}")
    translations = {
        "en": {
            "banner_title": "===========================================================================",
            "banner_header": "      TheOne - Neuro-Symbolic AI Engine - MVP      ",
            "banner_sub": "  Honest, Transparent, and 100% Hallucination-Free Logical Reasoning Engine",
            "banner_options": "Available Options:",
            "menu_ask": " 1. Ask the system any question in natural language",
            "menu_graph": " 2. Show current knowledge graph (Concepts & Relations)",
            "menu_teach": " 3. Teach the system a new fact (Add relationship in graph)",
            "menu_worlds": " 4. Show stored fact worlds",
            "menu_lang": " 5. Change CLI Interface Language",
            "menu_exit": " 6. Exit",
            "menu_choice": "\nChoose an option (1-6): ",
            "ask_prompt": "\nAsk the logical mind: ",
            "press_enter": "Press [Enter] to continue..."
        }
    }

def t(key, **kwargs):
    global active_lang
    lang_dict = translations.get(active_lang, translations["en"])
    text = lang_dict.get(key, translations["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def print_banner(handler):
    print(t("banner_title"))
    print(t("banner_header"))
    print(t("banner_sub"))
    print(t("banner_title"))
    print(t("banner_options"))
    print(t("menu_ask"))
    print(t("menu_graph"))
    print(t("menu_teach"))
    print(t("menu_worlds"))
    print(t("menu_lang"))
    mode_lbl = "Libraries (NLP Drivers)" if handler.nlp_mode == "library" else "Database Rules (Dynamic)"
    print(t("menu_nlp_mode", mode=mode_lbl))
    print(t("menu_exit"))
    print("-" * 75)

def show_graph(handler):
    print(t("graph_title"))
    print(t("graph_concepts_count", count=handler.graph.number_of_nodes()))
    print(t("graph_relations_count", count=handler.graph.number_of_edges()))
    print("-" * 50)
    
    # Display concepts grouped by category
    categories = {}
    for node, data in handler.graph.nodes(data=True):
        if data.get("type") == "concept":
            cat = data.get("category") or "other"
            lbl = data.get("labels", [node])[0]
            categories.setdefault(cat, []).append(f"{lbl} ({node})")
            
    print(t("graph_registered"))
    for cat, nodes in categories.items():
        print(t("graph_cat_nodes", cat=cat, nodes=', '.join(nodes)))
        
    print(t("graph_active_rels"))
    for from_node, to_node, data in handler.graph.edges(data=True):
        rel = data.get("relation")
        world = data.get("world", "reality")
        # Get labels
        from_lbl = handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in handler.graph else from_node
        to_lbl = handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in handler.graph else to_node
        print(t("graph_rel_format", from_lbl=from_lbl, rel=rel, to_lbl=to_lbl, world=world))
    print("-" * 50)

def show_worlds(handler):
    print(t("worlds_title"))
    worlds = set()
    for _, _, data in handler.graph.edges(data=True):
        if data.get("type") == "fact":
            worlds.add(data.get("world", "reality"))
            
    print(t("worlds_available", worlds=list(worlds)))
    print(t("worlds_active", world=handler.active_world))
    print("-" * 50)

def teach_system(handler):
    print(t("teach_title"))
    print(t("teach_warning"))
    print("-" * 50)
    
    # Simple interactive teaching
    print(t("teach_concepts_available"))
    concepts = [node for node, data in handler.graph.nodes(data=True) if data.get("type") == "concept"]
    for idx, c in enumerate(concepts):
        lbl = handler.graph.nodes[c].get("labels", [c])[0]
        print(f" {idx + 1}. {lbl} ({c})")
        
    try:
        from_idx = int(input(t("teach_choose_from"))) - 1
        to_idx = int(input(t("teach_choose_to"))) - 1
        
        if 0 <= from_idx < len(concepts) and 0 <= to_idx < len(concepts):
            from_c = concepts[from_idx]
            to_c = concepts[to_idx]
            
            print(t("teach_relations_available"))
            print(" 1. is_a")
            print(" 2. lives_in")
            print(" 3. has_property")
            print(" 4. requires")
            print(" 5. provides")
            
            rel_choice = input(t("teach_choose_rel"))
            rel_map = {
                "1": "is_a",
                "2": "lives_in",
                "3": "has_property",
                "4": "requires",
                "5": "provides"
            }
            rel = rel_map.get(rel_choice, "has_property")
            
            world_choice = input(t("teach_which_world")).strip() or "reality"
            
            # Use add_or_update_fact to handle duplicates and contradictions
            update_res = handler.add_or_update_fact(
                from_c,
                to_c,
                relation=rel,
                world=world_choice,
                confidence=1.0,
                interactive=True,
                language=active_lang
            )
            print(f"\n{update_res['message']}")
        else:
            print(t("teach_invalid_concept"))
    except Exception as e:
        print(t("teach_error", error=e))

def change_language():
    global active_lang
    print(t("lang_switch_title"))
    choice = input(t("lang_switch_prompt")).strip().lower()
    if choice in translations:
        active_lang = choice
        print(t("lang_switch_success"))
    else:
        print(f"⚠️ Unsupported language choice: {choice}. Retaining current language: {active_lang}")

def change_nlp_mode(handler):
    choice = input(t("nlp_mode_switch_prompt")).strip()
    if choice == "1":
        handler.nlp_mode = "library"
        mode_lbl = "Libraries (NLP Drivers)" if active_lang != "ar" else "المكتبات الخارجية (NLP Drivers)"
        print(t("nlp_mode_toggle_success", mode=mode_lbl))
    elif choice == "2":
        handler.nlp_mode = "database"
        mode_lbl = "Database Rules (Dynamic)" if active_lang != "ar" else "قواعد البيانات الديناميكية (Dynamic Rules)"
        print(t("nlp_mode_toggle_success", mode=mode_lbl))
    else:
        print("⚠️ Invalid choice. Retaining current NLP mode.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="TheOne Neuro-Symbolic AI CLI")
    parser.add_argument("--trace-level", type=str, choices=["detailed", "minimal"], default="detailed", help="Trace level verbosity")
    parser.add_argument("--nlp-mode", type=str, choices=["library", "database"], default="library", help="NLP mode to run in (library or database)")
    args = parser.parse_args()
    
    trace_level = args.trace_level

    # 1. Initialize databases
    handler = GraphHandler()
    handler.nlp_mode = args.nlp_mode
    
    ontology_path = "data/ontology.json"
    facts_path = "data/facts.json"
    language_rules_path = "data/language_rules.json"
    
    # Resolve paths relative to working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(ontology_path):
        ontology_path = os.path.join(base_dir, ontology_path)
        facts_path = os.path.join(base_dir, facts_path)
        language_rules_path = os.path.join(base_dir, language_rules_path)
        
    try:
        handler.load_databases(ontology_path, facts_path, language_rules_path)
    except Exception as e:
        print(f"Error loading databases: {e}")
        sys.exit(1)
        
    reasoner = SimpleReasoner(handler)
    persona_engine = MultilingualPersonaEngine(handler)
    
    # Print welcome
    print_banner(handler)
    
    while True:
        choice = input(t("menu_choice")).strip()
        
        if choice == "1":
            query = input(t("ask_prompt")).strip()
            if not query:
                continue
                
            # Run pipeline
            # 1. Detect language to parse query correctly
            detected_lang = persona_engine.language_engine.detect_language(query)
            selected_lang = persona_engine.language_engine.select_language(detected_lang, user_preference=active_lang)
            
            # 2. Logical reasoning
            start_time = time.perf_counter()
            res = reasoner.process_query(query, interactive=True, language=selected_lang)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            # 3. Multilingual Persona response generation
            history = reasoner.conversation_manager.get_history()
            engine_res = persona_engine.process_response(query, res, conversation_history=history, user_preference=active_lang)
            response = engine_res["response"]
            lang = engine_res["language"]
            persona = engine_res["persona"]
            
            print("\n" + "=" * 50)
            print(f"{t('active_world')}: '{handler.active_world}'")
            print(f"{t('language')}: {lang} | {t('persona')}: {persona}")
            print(f"{t('final_response')}:\n👉 {response}")
            print("=" * 50)
            
            # Print logical trace and performance if trace level is detailed
            if trace_level == "detailed":
                formatted_trace = persona_engine.expression_renderer.format_trace(res.get("trace", []), lang)
                print(formatted_trace)
                print(f"🎯 {t('confidence')}: {res.get('confidence', 1.0):.2f}")
                print(t("perf_took", elapsed=elapsed_ms))
                print("=" * 50)
            
        elif choice == "2":
            show_graph(handler)
        elif choice == "3":
            teach_system(handler)
        elif choice == "4":
            show_worlds(handler)
        elif choice == "5":
            change_language()
            print_banner(handler)
        elif choice == "6":
            change_nlp_mode(handler)
            print_banner(handler)
        elif choice == "7" or choice.lower() == "q":
            print(t("exit_msg"))
            break
        else:
            print(t("invalid_choice"))

if __name__ == "__main__":
    main()
