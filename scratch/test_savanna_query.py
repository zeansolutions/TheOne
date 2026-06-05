import os
import sys
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine

# User JSON data
user_json = {
  "concepts": [
    {"id": "lion", "labels": ["الأسد", "أسد"], "category": "animal"},
    {"id": "savanna", "labels": ["غابات السافانا", "السافانا", "سافانا"], "category": "location"},
    {"id": "gazelle", "labels": ["الغزالة", "غزالة", "غزال"], "category": "animal"}
  ],
  "relations": [
    {"from": "lion", "relation": "eats", "to": "gazelle"},
    {"from": "lion", "relation": "located_in", "to": "savanna"},
    {"from": "gazelle", "relation": "located_in", "to": "savanna"}
  ],
  "relations_metadata": [
    {"id": "eats", "name": "يأكل", "transitive": False, "symmetric": False, "decay": 0.0},
    {"id": "located_in", "name": "يتواجد في", "transitive": False, "symmetric": False, "decay": 0.0}
  ],
  "facts": [
    {
      "id": "fact_lion_eats_gazelle",
      "world": "عالم الحيوان",  # Change to "عالم الحيوان" to match active world request
      "subject": "lion",
      "predicate": "eats",
      "object": "gazelle",
      "confidence": 1.0
    },
    {
      "id": "fact_lion_in_savanna",
      "world": "عالم الحيوان",  # Change to "عالم الحيوان"
      "subject": "lion",
      "predicate": "located_in",
      "object": "savanna",
      "confidence": 1.0
    },
    {
      "id": "fact_gazelle_in_savanna",
      "world": "عالم الحيوان",  # Change to "عالم الحيوان"
      "subject": "gazelle",
      "predicate": "located_in",
      "object": "savanna",
      "confidence": 1.0
    }
  ],
  "rules": [],
  "morphology": {
    "roots": [
      {"id": "أسد", "patterns": ["الأسد", "أسد"]},
      {"id": "أكل", "patterns": ["يأكل", "أكل"]},
      {"id": "غزل", "patterns": ["الغزالة", "غزالة"]},
      {"id": "غيب", "patterns": ["غابات"]},
      {"id": "سفن", "patterns": ["السافانا"]}
    ],
    "particles": [
      {"form": "ال", "type": "definite_article"},
      {"form": "في", "type": "preposition"}
    ]
  },
  "grammar": {
    "sentence_types": [
      {"id": "declarative_verbal", "pattern": "subject + verb + object + prepositional_phrase", "description": "جملة خبرية فعلية تبدأ باسم متبوع بفعل ومفعول به وجار ومجرور"}
    ],
    "question_particles": ["ما", "من", "هل", "أين", "كيف", "لماذا", "ماذا", "متى", "كم", "أي", "هي"]
  },
  "ar": {
    "lexicon": {
      "الأسد": "lion",
      "أسد": "lion",
      "الغزالة": "gazelle",
      "غزالة": "gazelle",
      "غابات السافانا": "savanna",
      "السافانا": "savanna"
    },
    "relations": {
      "يأكل": "eats",
      "في": "located_in"
    },
    "question_particles": ["ما", "من", "هل", "أين", "كيف", "لماذا", "ماذا", "متى", "كم", "أي", "هي"]
  },
  "en": {
    "lexicon": {
      "lion": "lion",
      "gazelle": "gazelle",
      "savanna": "savanna",
      "savanna woodlands": "savanna"
    },
    "relations": {
      "eats": "eats",
      "is in": "located_in"
    },
    "question_particles": ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]
  },
  "semantic_frames": {
    "feeding_scene": {
      "predicate": "يأكل",
      "roles": [
        {"role_type": "AGENT", "description": "الكائن الآكل", "required": True, "constraints": ["is_a:lion"]},
        {"role_type": "PATIENT", "description": "الكائن المأكول", "required": True, "constraints": ["is_a:gazelle"]},
        {"role_type": "LOCATION", "description": "مكان الحدث", "required": False, "constraints": ["is_a:savanna"]}
      ]
    }
  }
}

def test_flow():
    # Initialize handler
    handler = GraphHandler()
    ontology_path = os.path.join(project_root, "data/ontology.json")
    facts_path = os.path.join(project_root, "data/facts.json")
    language_rules_path = os.path.join(project_root, "data/language_rules.json")
    
    # Load base databases
    handler.load_databases(ontology_path, facts_path, language_rules_path)
    
    # Import user JSON data (temporarily in-memory)
    # Since we don't want to permanently write to user's databases yet, we import it to our graph handler instance.
    print("📥 Importing JSON data...")
    stats = handler.import_json_data(user_json)
    print(f"Stats of import: {stats}")
    
    # Set active world
    handler.set_active_world("عالم الحيوان")
    print(f"Active world set to: {handler.active_world}")
    
    # Run dynamic inference rules on the active world
    handler.infer_facts(handler.active_world)
    
    # Create reasoner and persona engine
    reasoner = SimpleReasoner(handler)
    
    # Let's test with the query from user: "اين يأكل الاسد العزالة؟"
    query = "اين يأكل الاسد العزالة؟"
    print(f"\n--- Running query 1: '{query}' ---")
    res1 = reasoner.process_query(query, interactive=True, language="ar")
    print("Response JSON:")
    print(json.dumps(res1, ensure_ascii=False, indent=2))
    
    # Let's also test the corrected query: "اين يأكل الاسد الغزالة؟" to see the difference
    query_corrected = "اين يأكل الاسد الغزالة؟"
    print(f"\n--- Running query 2 (Corrected): '{query_corrected}' ---")
    res2 = reasoner.process_query(query_corrected, interactive=True, language="ar")
    print("Response JSON:")
    print(json.dumps(res2, ensure_ascii=False, indent=2))
    
    # Let's also test the fully corrected query with proper hamzas: "اين يأكل الأسد الغزالة؟"
    query_fully_corrected = "اين يأكل الأسد الغزالة؟"
    print(f"\n--- Running query 3 (Fully Corrected - with hamza): '{query_fully_corrected}' ---")
    res3 = reasoner.process_query(query_fully_corrected, interactive=True, language="ar")
    print("Response JSON:")
    print(json.dumps(res3, ensure_ascii=False, indent=2))
    
    # Let's print semantic roles extraction trace to see if semantic frames worked
    print("\n--- Semantic Roles analysis for Query 3 ---")
    words_q3 = query_fully_corrected.strip().replace("؟", "").split()
    roles_res = reasoner.semantic_processor.extract_semantic_roles(words_q3, "ar", handler)
    print("Semantic Roles Output:", roles_res)


if __name__ == "__main__":
    test_flow()
