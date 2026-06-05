# Unified English Knowledge & Logic Extraction Prompt — TheOne Engine

---

> **USER Instructions:**
> 1. Copy all the content of this file (from the first line to the end).
> 2. Paste it completely into the chat box of any powerful LLM (e.g., Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro).
> 3. Append the story, article, or factual description you want the system to learn.
> 4. The AI model will extract all cognitive, linguistic, and logical layers, generating **exactly ONE consolidated JSON object** ready for direct import via the **DB & Ingest** interface.

---

### <<< START OF PROMPT >>>

You are an expert Knowledge Extraction Agent for **TheOne**, a state-of-the-art Neuro-Symbolic AI Engine. 
Your task is to analyze the user's input text (story, article, or factual description) and extract the complete cognitive and logic layers from it, converting them into **exactly ONE consolidated JSON object** matching the unified schema defined below.

#### ⚠️ CRITICAL ENGINEERING RULES FOR EXTRACTION:
1. **Absolute Concept Coverage (No Missing Concepts):** 
   - Every single concept/entity ID referenced anywhere in the JSON (including in `relations`, `facts`, `rules`, `exceptions`, `temporal_facts`, `causal_chains`, and `comparative_properties`) **MUST be explicitly defined** in the `"concepts"` array with its corresponding labels and category. 
   - For example, if you output a relation, fact, or rule involving a concept (e.g., `"sky"` or `"speech"`), then that exact concept ID **MUST** exist in the `"concepts"` array. Do not use implicit concepts in rules.
2. **Strict Key Separation (Metadata vs Instances):**
   - `"relations"`: Use this array **ONLY** for ontology relation instances (edges between concepts in the graph). Objects here MUST contain only: `"from"`, `"relation"`, and `"to"` (and optional `"causal_purpose"`).
   - `"relations_metadata"`: Use this array **ONLY** for declaring and configuring the logical attributes of a relation. Objects here MUST contain: `"id"`, `"name"`, `"transitive"`, `"symmetric"`, and `"decay"`.
   - Never mix relation instances (e.g. `from`/`to`) and metadata attributes inside the same array!
3. **Logic & Rule Alignment & Completeness:**
   - Any relation predicate used in the `conditions` or `conclusion` of a rule inside `"rules"` (or `"inference_rules"`) MUST be declared in `"relations_metadata"` and instantiated in `"facts"`.
   - If a rule is defined for one instance of a class (e.g. classifying a noun), write equivalent complete rules for the other instances of that class (e.g. verbs, particles) to ensure complete logical coverage.
4. **Complete Morphological Lexicon & Lemmas (CRITICAL):**
   - The morphology section `"morphology"` must contain valid English lemmas/roots (`roots`) and grammatical particles (`particles`).
   - The translation lexicon (`"en"`) must link all English words (including plural forms, inflected forms, and articles like `"lion"` / `"lions"` / `"the lion"`) to their exact concept IDs in `"concepts"`.
5. **Mandatory Question Particles (CRITICAL):**
   - The `"grammar"."question_particles"` array and the `"en"."question_particles"` array MUST ALWAYS be populated with the complete set of question words for English, even if the input text has no questions. Without these, the system cannot recognize user questions at all.
   - English question particles MUST include at minimum: `["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]`
6. **Output Format:**
   - Output ONLY a single JSON code block. Do NOT split the output into multiple markdown blocks or files. Do NOT add introductory or concluding remarks.

---

### UNIFIED JSON SCHEMA STRUCTURAL SPECIFICATION

Your output JSON must have this exact structure (include only the keys that are populated by the text):

```json
{
  "concepts": [
    {
      "id": "concept_id_in_english_snake_case",
      "labels": ["english_label", "synonym_label"],
      "category": "user_defined"
    }
  ],
  "relations": [
    {
      "from": "subject_concept_id",
      "relation": "relation_type_id",
      "to": "object_concept_id",
      "causal_purpose": "optional_reasoning_string"
    }
  ],
  "relations_metadata": [
    {
      "id": "relation_type_id",
      "name": "english_relation_name",
      "transitive": true,
      "symmetric": false,
      "decay": 0.0
    }
  ],
  "facts": [
    {
      "id": "fact_unique_id",
      "world": "reality",
      "subject": "subject_concept_id",
      "predicate": "relation_type_id",
      "object": "object_concept_id",
      "confidence": 1.0,
      "reason": "optional_reason"
    }
  ],
  "rules": [
    {
      "id": "rule_unique_id",
      "name": "rule_name_in_english",
      "conditions": [
        {"subject": "?x", "relation": "relation_type_id", "object": "?y"},
        {"subject": "?y", "relation": "relation_type_id", "object": "?z"}
      ],
      "conclusion": {
        "subject": "?x",
        "relation": "resulting_relation_type_id",
        "object": "?z"
      },
      "description": "Explanation of the logical rule and how it is used for inference"
    }
  ],
  "personas": [
    {
      "id": "persona_id",
      "name": "persona_name",
      "language_style": {
        "tone": "scientific|sage|witty",
        "particles": ["key_phrases"],
        "filler_words": ["fillers"]
      },
      "knowledge_preferences": {
        "detailed": true,
        "examples": true,
        "analogies": true
      },
      "personality_traits": {
        "humorous": 0.5,
        "formal": 0.5,
        "patient": 0.8
      }
    }
  ],
  "morphology": {
    "roots": [
      {
        "id": "english_lemma_or_root",
        "patterns": ["word_forms", "derivatives"]
      }
    ],
    "particles": [
      {"form": "particle_form", "type": "article|preposition|conjunction"}
    ]
  },
  "grammar": {
    "sentence_types": [
      {"id": "declarative", "pattern": "noun + verb + object", "description": "declarative sentence"}
    ],
    "question_particles": ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]
  },
  "en": {
    "lexicon": {
      "english_word": "concept_id"
    },
    "relations": {
      "english_verb": "relation_type_id"
    },
    "question_particles": ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]
  },
  "weights": {
    "always": 1.0,
    "usually": 0.8,
    "sometimes": 0.5,
    "rarely": 0.2
  },
  "keywords": {
    "en": {
      "always": "always",
      "usually": "usually",
      "sometimes": "sometimes",
      "rarely": "rarely"
    }
  },
  "modalities": {
    "necessity": {
      "description": "absolute_necessity",
      "confidence_threshold": 0.95
    }
  },
  "semantic_frames": {
    "frame_name": {
      "predicate": "core_verb",
      "roles": [
        {
          "role_type": "AGENT|PATIENT|LOCATION",
          "description": "role_description",
          "required": true,
          "constraints": ["is_a:concept_id"]
        }
      ]
    }
  },
  "syntactic_patterns": [
    {
      "id": "pattern_unique_id",
      "pattern": ["word1", "?X", "word2", "?Y"],
      "intent": "target_intent",
      "mapping": {"subject": "?X", "object": "?Y"}
    }
  ],
  "temporal_relations": {
    "BEFORE": {"symbol": "<", "transitivity": true},
    "AFTER": {"symbol": ">", "transitivity": true}
  },
  "temporal_facts": [
    {
      "entity": "concept_id",
      "event": "event_name",
      "time": "BEFORE|AFTER|DURING",
      "reference": "present|event_id",
      "confidence": 1.0
    }
  ],
  "causal_chains": [
    {
      "id": "chain_id",
      "steps": [
        {"step": 1, "event": "event_1", "agent": "concept_id"},
        {"step": 2, "event": "event_2", "causal_link": "causes"}
      ]
    }
  ],
  "negation_rules": [
    {
      "id": "double_negation",
      "rule": "not (not X) -> X"
    }
  ],
  "quantifiers": [
    {
      "id": "universal_quantifier",
      "type": "universal",
      "scope": "concept_id"
    }
  ],
  "entailments": [
    {
      "premise": {"relation": "is_a", "to": "carnivore"},
      "conclusion": {"relation": "eats", "to": "meat"},
      "relation": "entails",
      "confidence": 0.9
    }
  ],
  "pragmatic_facts": [
    {
      "context": "cultural_metaphor",
      "literal": "literal_fact",
      "implied": "implied_meaning"
    }
  ],
  "exceptions": [
    {
      "entity": "concept_id",
      "property": "property_concept_id",
      "typical_rule": "usual_rule_id",
      "exception_type": "exception_type_name",
      "confidence": 0.05,
      "reason": "explanation_of_exception"
    }
  ],
  "comparative_properties": {
    "property_name": {
      "scale": [
        {"entity": "concept_id_1", "value": 0.2},
        {"entity": "concept_id_2", "value": 0.9}
      ]
    }
  }
}
```

---

### FEW-SHOT CONCRETE EXAMPLE (EXAMPLE TEXT AND CORRESPONDING CONSOLIDATED JSON)

**Input Story:**
"The lion is a predatory mammal that usually lives in the savanna. The lion preys on the gazelle. However, some rare lions are born mutant and only eat grass. The lion is stronger than the gazelle."

**Generated Consolidated JSON:**
```json
{
  "concepts": [
    {"id": "lion", "labels": ["lion", "lions", "the lion"], "category": "animal"},
    {"id": "mammal", "labels": ["mammal", "mammals"], "category": "class"},
    {"id": "predator", "labels": ["predator", "predators"], "category": "class"},
    {"id": "savanna", "labels": ["savanna", "savannah"], "category": "location"},
    {"id": "gazelle", "labels": ["gazelle", "gazelles", "the gazelle"], "category": "prey"},
    {"id": "grass", "labels": ["grass"], "category": "food"}
  ],
  "relations": [
    {"from": "lion", "relation": "is_a", "to": "mammal"},
    {"from": "mammal", "relation": "is_a", "to": "predator"},
    {"from": "lion", "relation": "lives_in", "to": "savanna"},
    {"from": "lion", "relation": "eats", "to": "gazelle"}
  ],
  "relations_metadata": [
    {"id": "is_a", "name": "is a", "transitive": true, "symmetric": false, "decay": 0.0},
    {"id": "lives_in", "name": "lives in", "transitive": false, "symmetric": false, "decay": 0.0},
    {"id": "eats", "name": "eats", "transitive": false, "symmetric": false, "decay": 0.0}
  ],
  "facts": [
    {
      "id": "fact_lion_mammal",
      "world": "reality",
      "subject": "lion",
      "predicate": "is_a",
      "object": "mammal",
      "confidence": 1.0
    },
    {
      "id": "fact_lion_savanna",
      "world": "reality",
      "subject": "lion",
      "predicate": "lives_in",
      "object": "savanna",
      "confidence": 0.8,
      "reason": "usually lives in savanna as stated in text"
    }
  ],
  "rules": [
    {
      "id": "transitive_is_a",
      "name": "Taxonomic Transitivity",
      "conditions": [
        {"subject": "?x", "relation": "is_a", "object": "?y"},
        {"subject": "?y", "relation": "is_a", "object": "?z"}
      ],
      "conclusion": {
        "subject": "?x",
        "relation": "is_a",
        "object": "?z"
      },
      "description": "If ?x is a ?y, and ?y is a ?z, then ?x is a ?z by transitivity."
    }
  ],
  "morphology": {
    "roots": [
      {"id": "lion", "patterns": ["lion", "lions", "lioness"]},
      {"id": "gazelle", "patterns": ["gazelle", "gazelles"]}
    ],
    "particles": [
      {"form": "the", "type": "definite_article"},
      {"form": "in", "type": "preposition"},
      {"form": "a", "type": "indefinite_article"}
    ]
  },
  "grammar": {
    "sentence_types": [
      {"id": "declarative", "pattern": "noun + verb + object", "description": "Declarative verbal or nominal sentence"}
    ],
    "question_particles": ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]
  },
  "en": {
    "lexicon": {
      "lion": "lion",
      "lions": "lion",
      "gazelle": "gazelle",
      "gazelles": "gazelle",
      "savanna": "savanna",
      "savannah": "savanna",
      "grass": "grass"
    },
    "relations": {
      "lives in": "lives_in",
      "eats": "eats",
      "preys on": "eats"
    },
    "question_particles": ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]
  },
  "weights": {
    "usually": 0.8,
    "sometimes": 0.5
  },
  "keywords": {
    "en": {
      "usually": "usually",
      "sometimes": "sometimes"
    }
  },
  "semantic_frames": {
    "predation": {
      "predicate": "preys on",
      "roles": [
        {"role_type": "AGENT", "description": "Predator", "required": true, "constraints": ["is_a:predator"]},
        {"role_type": "PATIENT", "description": "Prey", "required": true, "constraints": ["is_a:prey"]}
      ]
    }
  },
  "syntactic_patterns": [
    {
      "id": "predation_pattern_01",
      "pattern": ["?X", "preys", "on", "?Y"],
      "intent": "teaching_statement",
      "mapping": {"subject": "?X", "relation": "eats", "object": "?Y"}
    }
  ],
  "exceptions": [
    {
      "entity": "lion",
      "property": "grass",
      "typical_rule": "lion_eats_meat",
      "exception_type": "mutant_vegetarian",
      "confidence": 0.05,
      "reason": "genetic mutation as exception to the rule"
    }
  ],
  "comparative_properties": {
    "strength": {
      "scale": [
        {"entity": "gazelle", "value": 0.3},
        {"entity": "lion", "value": 0.9}
      ]
    }
  }
}
```

---

### <<< END OF PROMPT >>>

**USER INPUT TEXT TO PROCESS:**
[Paste your story or text here]
