# التلقينة الشاملة الموحدة لاستخراج المعرفة والمنطق — محرك TheOne
## The Consolidated Knowledge & Logic Extraction Prompt for TheOne Engine

---

> **تعليمات الاستخدام للـ USER:**
> 1. انسخ كل المحتوى الموجود بداخل هذا الملف (من السطر الأول حتى النهاية).
> 2. ألصقه بالكامل في صندوق المحادثة الخاص بأي نموذج ذكاء اصطناعي قوي (مثل: Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro).
> 3. ألحق به القصة أو النص أو البيانات التي ترغب في أن يتعلمها النظام.
> 4. سيقوم نموذج الـ AI باستخراج كافة الطبقات المعرفية واللغوية والمنطقية الـ 16 وإنتاج **ملف JSON موحد مجمع** جاهز للرفع فوراً للتطبيق عبر واجهة **DB & Ingest**.

---

### <<< START OF PROMPT >>>

You are an expert Knowledge Extraction Agent for **TheOne**, a state-of-the-art Neuro-Symbolic AI Engine. 
Your task is to analyze the user's input text (story, article, or factual description) and extract the complete cognitive and logic layers from it, converting them into **exactly ONE consolidated JSON object** matching the unified schema defined below.

#### ⚠️ CRITICAL ENGINEERING RULES FOR EXTRACTION:
1. **Absolute Concept Coverage (No Missing Concepts):** 
   - Every single concept/entity ID referenced anywhere in the JSON (including in `relations`, `facts`, `rules`, `exceptions`, `temporal_facts`, `causal_chains`, and `comparative_properties`) **MUST be explicitly defined** in the `"concepts"` array with its corresponding labels and category. 
   - For example, if you output a relation, fact, or rule involving a concept (e.g., `"sky"` or `"arabic_speech"`), then that exact concept ID **MUST** exist in the `"concepts"` array. Do not use implicit concepts in rules.
2. **Strict Key Separation (Metadata vs Instances):**
   - `"relations"`: Use this array **ONLY** for ontology relation instances (edges between concepts in the graph). Objects here MUST contain only: `"from"`, `"relation"`, and `"to"` (and optional `"causal_purpose"`).
   - `"relations_metadata"`: Use this array **ONLY** for declaring and configuring the logical attributes of a relation. Objects here MUST contain: `"id"`, `"name"`, `"transitive"`, `"symmetric"`, and `"decay"`.
   - Never mix relation instances (e.g. `from`/`to`) and metadata attributes inside the same array!
3. **Logic & Rule Alignment & Completeness:**
   - Any relation predicate used in the `conditions` or `conclusion` of a rule inside `"rules"` (or `"inference_rules"`) MUST be declared in `"relations_metadata"` and instantiated in `"facts"`.
   - If a rule is defined for one instance of a class (e.g. classifying a noun), write equivalent complete rules for the other instances of that class (e.g. verbs, particles) to ensure complete logical coverage.
4. **Complete Morphological Lexicon & Space-less Roots (CRITICAL):**
   - The Arabic morphology section `"morphology"` must contain valid linguistic roots (`roots`) and particles (`particles`).
   - **Arabic roots MUST be written as a single, continuous string of characters WITHOUT any spaces or separators (e.g., use `"طلب"` not `"ط ل ب"` or `"ط-ل-ب"`).** The system uses exact substring matching for root processing, and spaces will break this.
   - The translation lexicon (`"ar"`, `"en"`, etc.) must link all Arabic words (including root variations and forms like `"نجمة"` / `"نجمة صغيرة"` / `"النجمة"`) to their exact concept IDs in `"concepts"`.
5. **Mandatory Multilingual Sections and Question Particles (CRITICAL):**
   - You MUST include a language mapping block for ALL 11 supported languages: `"en"`, `"ar"`, `"fr"`, `"es"`, `"zh"`, `"tr"`, `"de"`, `"ru"`, `"pt"`, `"ja"`, and `"ko"`.
   - Each language block MUST contain a `"lexicon"` mapping (associating translated words of the extracted concepts to their concept IDs), a `"relations"` mapping (associating translated relation verbs to relation type IDs), and a `"question_particles"` array.
   - The `"question_particles"` array for each of the 11 languages must be fully populated with its standard question words, even if the text has no questions. Without this, the query engine cannot recognize questions in those languages.
   - Example minimum question particles:
     - `en`: `["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]`
     - `ar`: `["ما", "من", "هل", "أين", "كيف", "لماذا", "ماذا", "متى", "كم", "أي", "هي"]`
     - `fr`: `["que", "qui", "où", "quand", "pourquoi", "comment", "quel", "quelle", "est-ce"]`
     - `es`: `["qué", "quién", "dónde", "cuándo", "por qué", "cómo", "cuál", "es", "son"]`
     - `zh`: `["什么", "谁", "哪里", "什么时候", "为什么", "怎么", "哪个", "吗", "呢"]`
     - `tr`: `["ne", "kim", "nerede", "ne zaman", "neden", "nasıl", "hangi", "mi", "mı"]`
     - `de`: `["was", "wer", "wo", "wann", "warum", "wie", "welcher", "ist", "sind"]`
     - `ru`: `["что", "кто", "где", "когда", "почему", "как", "какой", "ли"]`
     - `pt`: `["o que", "quem", "onde", "quando", "por que", "como", "qual", "é", "são"]`
     - `ja`: `["なに", "だれ", "どこ", "いつ", "なぜ", "どうやって", "どちら", "か", "ね"]`
     - `ko`: `["무엇", "누구", "어디", "언제", "왜", "어떻게", "어느", "가", "이"]`
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
      "labels": ["الاسم بالعربية", "مرادف آخر"],
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
      "name": "الاسم بالعربية",
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
      "name": "اسم القاعدة بالعربية",
      "conditions": [
        {"subject": "?x", "relation": "relation_type_id", "object": "?y"},
        {"subject": "?y", "relation": "relation_type_id", "object": "?z"}
      ],
      "conclusion": {
        "subject": "?x",
        "relation": "resulting_relation_type_id",
        "object": "?z"
      },
      "description": "شرح القاعدة المنطقية وكيفية الاستدلال بها"
    }
  ],
  "personas": [
    {
      "id": "persona_id",
      "name": "اسم الشخصية",
      "language_style": {
        "tone": "scientific|sage|witty",
        "particles": ["عبارات مفتاحية"],
        "filler_words": ["حشو"]
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
        "id": "الجذر_اللغوي_العربي",
        "patterns": ["الكلمات", "المشتقة", "منه"]
      }
    ],
    "particles": [
      {"form": "الحرف", "type": "definite_article|preposition|conjunction"}
    ]
  },
  "grammar": {
    "sentence_types": [
      {"id": "declarative", "pattern": "noun + verb", "description": "جملة خبرية"}
    ],
    "question_particles": ["ما", "من", "هل", "أين", "كيف", "لماذا", "ماذا", "متى", "كم", "أي", "هي"]
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
  "ar": {
    "lexicon": {
      "الكلمة_العربية": "concept_id"
    },
    "relations": {
      "الفعل_أو_الرابط_العربي": "relation_type_id"
    },
    "question_particles": ["ما", "من", "هل", "أين", "كيف", "لماذا", "ماذا", "متى", "كم", "أي", "هي"]
  },
  "fr": {
    "lexicon": {
      "mot_français": "concept_id"
    },
    "relations": {
      "verbe_français": "relation_type_id"
    },
    "question_particles": ["que", "qui", "où", "quand", "pourquoi", "comment", "quel", "quelle", "est-ce"]
  },
  "es": {
    "lexicon": {
      "palabra_española": "concept_id"
    },
    "relations": {
      "verbo_español": "relation_type_id"
    },
    "question_particles": ["qué", "quién", "dónde", "cuándo", "por qué", "cómo", "cuál", "es", "son"]
  },
  "zh": {
    "lexicon": {
      "中文词汇": "concept_id"
    },
    "relations": {
      "中文动词": "relation_type_id"
    },
    "question_particles": ["什么", "谁", "哪里", "什么时候", "为什么", "怎么", "哪个", "吗", "呢"]
  },
  "tr": {
    "lexicon": {
      "türkçe_kelime": "concept_id"
    },
    "relations": {
      "türkçe_fiil": "relation_type_id"
    },
    "question_particles": ["ne", "kim", "nerede", "ne zaman", "neden", "nasıl", "hangi", "mi", "mı"]
  },
  "de": {
    "lexicon": {
      "deutsches_wort": "concept_id"
    },
    "relations": {
      "deutsches_verb": "relation_type_id"
    },
    "question_particles": ["was", "wer", "wo", "wann", "warum", "wie", "welcher", "ist", "sind"]
  },
  "ru": {
    "lexicon": {
      "русское_слово": "concept_id"
    },
    "relations": {
      "русский_глагол": "relation_type_id"
    },
    "question_particles": ["что", "кто", "где", "когда", "почему", "как", "какой", "ли"]
  },
  "pt": {
    "lexicon": {
      "palavra_portuguesa": "concept_id"
    },
    "relations": {
      "verbo_português": "relation_type_id"
    },
    "question_particles": ["o que", "quem", "onde", "quando", "por que", "como", "qual", "é", "são"]
  },
  "ja": {
    "lexicon": {
      "日本語の単語": "concept_id"
    },
    "relations": {
      "日本語の動詞": "relation_type_id"
    },
    "question_particles": ["なに", "だれ", "どこ", "いつ", "なぜ", "どうやって", "どちら", "か", "ね"]
  },
  "ko": {
    "lexicon": {
      "한국어_단어": "concept_id"
    },
    "relations": {
      "한국어_동사": "relation_type_id"
    },
    "question_particles": ["무엇", "누구", "어디", "언제", "왜", "어떻게", "어느", "가", "이"]
  },
  "weights": {
    "always": 1.0,
    "usually": 0.8,
    "sometimes": 0.5,
    "rarely": 0.2
  },
  "keywords": {
    "ar": {
      "دائماً": "always",
      "عادةً": "usually"
    }
  },
  "modalities": {
    "necessity": {
      "description": "ضرورة مطلقة",
      "confidence_threshold": 0.95
    }
  },
  "semantic_frames": {
    "frame_name": {
      "predicate": "الفعل_المحوري",
      "roles": [
        {
          "role_type": "AGENT|PATIENT|LOCATION",
          "description": "دور الفاعل أو المفعول به",
          "required": true,
          "constraints": ["is_a:concept_id"]
        }
      ]
    }
  },
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
      "literal": "fox_is_cunning",
      "implied": "smart_and_deceptive"
    }
  ],
  "exceptions": [
    {
      "entity": "concept_id",
      "property": "property_concept_id",
      "typical_rule": "usual_rule_id",
      "exception_type": "rare_exception",
      "confidence": 0.05,
      "reason": "genetic_variance"
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
"الأسد حيوان ثديي مفترس يعيش عادة في السافانا. يفترس الأسد الغزال. لكن بعض الأسود النادرة تولد طافرة وتأكل العشب فقط. الأسد أقوى من الغزال."

**Generated Consolidated JSON:**
```json
{
  "concepts": [
    {"id": "lion", "labels": ["أسد", "سبع", "الأسد"], "category": "animal"},
    {"id": "mammal", "labels": ["ثديي", "حيوان ثديي"], "category": "class"},
    {"id": "predator", "labels": ["مفترس", "كائن مفترس"], "category": "class"},
    {"id": "savanna", "labels": ["السافانا", "سافانا"], "category": "location"},
    {"id": "gazelle", "labels": ["غزال", "ظبي", "الغزال"], "category": "prey"},
    {"id": "grass", "labels": ["عشب", "نبات", "العشب"], "category": "food"}
  ],
  "relations": [
    {"from": "lion", "relation": "is_a", "to": "mammal"},
    {"from": "mammal", "relation": "is_a", "to": "predator"},
    {"from": "lion", "relation": "lives_in", "to": "savanna"},
    {"from": "lion", "relation": "eats", "to": "gazelle"}
  ],
  "relations_metadata": [
    {"id": "is_a", "name": "نوع من", "transitive": true, "symmetric": false, "decay": 0.0},
    {"id": "lives_in", "name": "يعيش في", "transitive": false, "symmetric": false, "decay": 0.0},
    {"id": "eats", "name": "يأكل", "transitive": false, "symmetric": false, "decay": 0.0}
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
      "name": "التعدي التصنيفي",
      "conditions": [
        {"subject": "?x", "relation": "is_a", "object": "?y"},
        {"subject": "?y", "relation": "is_a", "object": "?z"}
      ],
      "conclusion": {
        "subject": "?x",
        "relation": "is_a",
        "object": "?z"
      },
      "description": "إذا كان ?x نوعاً من ?y، و ?y نوعاً من ?z، فإن ?x نوع من ?z بالتبعية."
    }
  ],
  "morphology": {
    "roots": [
      {"id": "أسد", "patterns": ["أسد", "أسود", "الأسد", "الأسود"]},
      {"id": "غزل", "patterns": ["غزال", "غزلان", "الغزال"]}
    ],
    "particles": [
      {"form": "ال", "type": "definite_article"},
      {"form": "في", "type": "preposition"}
    ]
  },
  "grammar": {
    "sentence_types": [
      {"id": "declarative", "pattern": "noun + verb + object", "description": "جملة خبرية فعلية أو اسمية"}
    ],
    "question_particles": ["هل", "لماذا"]
  },
  "en": {
    "lexicon": {
      "lion": "lion",
      "gazelle": "gazelle",
      "savanna": "savanna",
      "grass": "grass"
    },
    "relations": {
      "lives in": "lives_in",
      "eats": "eats"
    },
    "question_particles": ["what", "who", "where", "when", "why", "how", "which", "is", "are", "do", "does"]
  },
  "ar": {
    "lexicon": {
      "أسد": "lion",
      "الأسد": "lion",
      "غزال": "gazelle",
      "الغزال": "gazelle",
      "السافانا": "savanna",
      "عشب": "grass",
      "العشب": "grass"
    },
    "relations": {
      "يعيش في": "lives_in",
      "يأكل": "eats",
      "يفترس": "eats"
    },
    "question_particles": ["ما", "من", "هل", "أين", "كيف", "لماذا", "ماذا", "متى", "كم", "أي", "هي"]
  },
  "fr": {
    "lexicon": {
      "lion": "lion",
      "gazelle": "gazelle",
      "savane": "savanna",
      "herbe": "grass"
    },
    "relations": {
      "vit dans": "lives_in",
      "mange": "eats"
    },
    "question_particles": ["que", "qui", "où", "quand", "pourquoi", "comment", "quel", "quelle", "est-ce"]
  },
  "es": {
    "lexicon": {
      "león": "lion",
      "gacela": "gazelle",
      "sabana": "savanna",
      "hierba": "grass"
    },
    "relations": {
      "vive en": "lives_in",
      "come": "eats"
    },
    "question_particles": ["qué", "quién", "dónde", "cuándo", "por qué", "cómo", "cuál", "es", "son"]
  },
  "zh": {
    "lexicon": {
      "狮子": "lion",
      "羚羊": "gazelle",
      "稀树草原": "savanna",
      "草": "grass"
    },
    "relations": {
      "居住在": "lives_in",
      "吃": "eats"
    },
    "question_particles": ["什么", "谁", "哪里", "什么时候", "为什么", "怎么", "哪个", "吗", "呢"]
  },
  "tr": {
    "lexicon": {
      "aslan": "lion",
      "ceylan": "gazelle",
      "savan": "savanna",
      "çimen": "grass"
    },
    "relations": {
      "-de yaşar": "lives_in",
      "yer": "eats"
    },
    "question_particles": ["ne", "kim", "nerede", "ne zaman", "neden", "nasıl", "hangi", "mi", "mı"]
  },
  "de": {
    "lexicon": {
      "löwe": "lion",
      "gazelle": "gazelle",
      "savanne": "savanna",
      "gras": "grass"
    },
    "relations": {
      "lebt in": "lives_in",
      "frisst": "eats"
    },
    "question_particles": ["was", "wer", "wo", "wann", "warum", "wie", "welcher", "ist", "sind"]
  },
  "ru": {
    "lexicon": {
      "лев": "lion",
      "газель": "gazelle",
      "саванна": "savanna",
      "трава": "grass"
    },
    "relations": {
      "живет в": "lives_in",
      "ест": "eats"
    },
    "question_particles": ["что", "кто", "где", "когда", "почему", "как", "какой", "ли"]
  },
  "pt": {
    "lexicon": {
      "leão": "lion",
      "gazela": "gazelle",
      "savana": "savanna",
      "grama": "grass"
    },
    "relations": {
      "vive em": "lives_in",
      "come": "eats"
    },
    "question_particles": ["o que", "quem", "onde", "quando", "por que", "como", "qual", "é", "são"]
  },
  "ja": {
    "lexicon": {
      "ライオン": "lion",
      "ガゼル": "gazelle",
      "サバンナ": "savanna",
      "草": "grass"
    },
    "relations": {
      "に生息する": "lives_in",
      "食べる": "eats"
    },
    "question_particles": ["なに", "だれ", "どこ", "いつ", "なぜ", "どうやって", "どちら", "か", "ね"]
  },
  "ko": {
    "lexicon": {
      "사자": "lion",
      "가젤": "gazelle",
      "사바나": "savanna",
      "풀": "grass"
    },
    "relations": {
      "~에 살다": "lives_in",
      "먹다": "eats"
    },
    "question_particles": ["무엇", "누구", "어디", "언제", "왜", "어떻게", "어느", "가", "이"]
  },
  "weights": {
    "usually": 0.8,
    "sometimes": 0.5
  },
  "keywords": {
    "ar": {
      "عادةً": "usually",
      "أحياناً": "sometimes"
    }
  },
  "semantic_frames": {
    "predation": {
      "predicate": "يفترس",
      "roles": [
        {"role_type": "AGENT", "description": "المفترس", "required": true, "constraints": ["is_a:predator"]},
        {"role_type": "PATIENT", "description": "الفريسة", "required": true, "constraints": ["is_a:prey"]}
      ]
    }
  },
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
[ألصق القصة أو النص الخاص بك هنا]
