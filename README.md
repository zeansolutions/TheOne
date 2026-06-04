<p align="center">
  <img src="images/logo.png" alt="TheOne Logo" width="220px" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"/>
</p>

<h1 align="center">TheOne — Neuro-Symbolic AI Engine 🧠🔗</h1>

<p align="center">
  <strong>Honest, Transparent, and 100% Hallucination-Free Symbolic-Hybrid Reasoning Engine</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tests-50%20passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests status"/>
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python version"/>
  <img src="https://img.shields.io/badge/Graph-NetworkX-orange?style=for-the-badge" alt="NetworkX"/>
  <img src="https://img.shields.io/badge/Runtime-Zero--LLM-red?style=for-the-badge" alt="Zero LLM Runtime"/>
  <img src="https://img.shields.io/badge/Languages-11--supported-purple?style=for-the-badge" alt="11 Languages"/>
</p>

---

## 📋 Overview

**TheOne** is a hybrid Neuro-Symbolic AI reasoning engine designed to operate as a **100% truthful and logically grounded cognitive mind** in natural language conversations and reasoning.

Unlike generative Large Language Models (LLMs) that rely on probabilistic patterns and statistical correlations—often leading to factual inaccuracies and hallucinations—this system is built upon a **local symbolic Knowledge Graph** powered by **NetworkX**.

The role of any LLM in this ecosystem is strictly restricted to the **knowledge extraction and ingestion phase (Extraction Time)**. At **Runtime**, the system functions as a **100% local, purely symbolic, and independent engine** that runs without calling any external APIs or generating statistical token sequences.

---

## 💡 Core Philosophy

* 🚫 **Zero Hallucination (Zero-Hallucination Policy):** If a fact does not exist in the active Knowledge Graph, the system honestly states: "I do not have this information" instead of guessing.
* 🔍 **Traceable Reasoning (Traceable AI):** Every response generated is backed by a step-by-step logical trace chain explaining exactly how the deduction was reached.
* 🔄 **Continuous Ingestive Learning:** The system learns facts in real-time during conversations, dynamically updating the Knowledge Graph.
* 🛡️ **Zero-Hardcoding Policy:** The reasoning engine is entirely domain-neutral. All grammatical rules, morphological affix tables, logic rules, and factual databases are loaded dynamically from external JSON files.

---

## 📂 Directory Structure

```text
TheOne/
├── config/                           # System and Localization Configurations
│   ├── languages.json                # Supported locales, RTL settings, default personas
│   └── personas_multilingual.json    # Persona archetypes (Sage Friend, Scientist, Witty Mentor)
│
├── data/                             # Zero-State Database & Config Rules (JSON)
│   ├── ontology.json                 # Core concepts and taxonomic relations (Starts empty)
│   ├── facts.json                    # Fact triples segmented by worlds/personas (Starts empty)
│   ├── language_rules.json           # Morphological roots/affixes for translation (Starts empty)
│   ├── inference_rules.json          # Logical inference rules (Horn clauses)
│   ├── semantic_roles.json           # Semantic frames (Agent, Patient, Location)
│   ├── temporal_logic.json           # Temporal relations (BEFORE, AFTER)
│   ├── modality.json                 # Modal logic rules (Necessity, Possibility)
│   ├── causal_chains.json            # Causal propagation rules and chains
│   ├── quantifiers.json              # Quantifier rules (Universal, Existential)
│   ├── negation_rules.json           # Polarity rules and double negation mappings
│   ├── entailment.json               # Propositional entailments and contradictions
│   ├── pragmatic_knowledge.json      # Metaphorical and cultural context mappings
│   ├── comparison.json               # Comparative ordering scales and relations
│   └── anomaly_detection.json        # Exceptional facts and anomaly rules
│
├── tests/                            # Automated Pytest Suite
│   ├── mock_data/                    # Isolated Mock Test Data
│   │   ├── animals_facts.json        # Animals mock facts for test cases
│   │   ├── animals_ontology_small.json # Animals mock ontology for test cases
│   │   └── animals_language_rules.json # Animals mock language rules for test cases
│   └── test_*.py                     # Unit test suites for reasoner layers
├── src/                              # Core Engine Source Code
│   ├── __init__.py
│   ├── graph_handler.py              # NetworkX manager, morphology, rules, and activation
│   ├── simple_reasoner.py            # Coordinate reasoning and cognitive layer routing
│   ├── response_generator_simple.py  # Response formatting, template rendering
│   ├── conversation_manager.py       # Dialogue state tracking and memory
│   ├── entity_resolver.py            # Pronoun and hidden subject reference resolution
│   ├── world_manager.py              # Multi-world sandbox and real-time fact teaching
│   ├── conflict_resolver.py          # Logical contradiction detection across worlds
│   │
│   ├── enrichment/
│   │   └── fuzzy_modal.py            # Fuzzy confidence and modal logic weights
│   ├── maintenance/
│   │   └── sleep_cycle.py            # Consolidation, pruning, deduplication
│   ├── manager/
│   │   ├── language_selection_engine.py # Auto-detects/selects target language
│   │   └── multilingual_persona_engine.py # Coordinates language, persona, and response
│   ├── reasoner/
│   │   ├── persona_selector.py       # Contextual persona classification
│   │   ├── transitive_chaining.py    # Multi-hop transitive deduction
│   │   ├── sandbox_manager.py        # Cloned memory graphs for sandboxes
│   │   ├── curiosity_engine.py       # Curiosity questions generation
│   │   # Cognitive Layer Processors
│   │   ├── semantic_processor.py
│   │   ├── temporal_processor.py
│   │   ├── modality_processor.py
│   │   ├── chain_processor.py
│   │   ├── quantifier_processor.py
│   │   ├── negation_processor.py
│   │   ├── entailment_processor.py
│   │   ├── pragmatic_processor.py
│   │   ├── comparison_processor.py
│   │   └── anomaly_processor.py
│   └── renderer/
│       └── expression_renderer.py    # Translates logical responses and traces
│
├── tests/                            # Automated Testing Suite (pytest)
│   ├── test_basic_reasoning.py       # Core logic and morphological tests
│   ├── test_queries.py               # Dialogue scenarios and multi-hop queries
│   ├── test_contradiction.py         # Collision and update system tests
│   ├── test_multilingual_persona.py  # Language and persona tests
│   ├── test_spreading_activation.py  # Word disambiguation tests
│   ├── test_dynamic_inference.py     # Rule induction and binding tests
│   ├── test_transitive_chaining.py   # Multi-hop chain tests
│   ├── test_sandbox.py               # Hypothetical thought experiments tests
│   ├── test_sleep_cycle.py           # Pruning and dream cycle tests
│   ├── test_curiosity.py             # Curiosity prompt generation tests
│   ├── test_fuzzy_modal.py           # Modals and confidence adjustments tests
│   └── test_advanced_reasoning_layers.py # Tests for the 10 cognitive layers
│
├── docs/                             # Project Feature Documentation
│   ├── en/                           # Feature descriptions in English
│   └── ar/                           # Feature descriptions in Arabic
│
├── main.py                           # Primary Interactive CLI entrypoint
├── start.sh                          # Interactive setup, test, and runner script
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore patterns
└── README.md                         # This readme file
```

---

## 🚀 Quick Start

The interactive wrapper script `start.sh` is provided to simplify dependencies setup, testing, and running the CLI.

### 1. Show Help & Arguments:
```bash
./start.sh --help
```

### 2. Configure Virtual Environment & Setup:
```bash
./start.sh setup
```

### 3. Run the Interactive CLI (Terminal):
```bash
./start.sh run
```

### 4. Run the Automated Tests (pytest):
```bash
./start.sh test
```

---

## 🔬 Core Supported Queries in MVP

1. **Direct Taxonomic Reasoning:** `"Is a lion an animal?"`
2. **Inherited Multi-hop Deduction:** `"Is a lion a predator?"`
3. **Fact Retrieval:** `"Where does a lion live?"`
4. **Causal Hypotheticals (Analogical Mapping):** `"If a lion lived in the arctic, what would it require?"`
   *(The system detects the polar climate, identifies a thermal insulation gap for a lion, looks up the polar bear's traits, maps the "thick fur" property to the lion, and shifts food properties).*
5. **Deductive Comparison:** `"What is the difference between a lion and a polar bear?"`

---

## 🧠 Advanced Implemented Features

This version includes robust features going beyond a standard MVP:

### 1. Conversation State & Entity Resolution
The system tracks dialogue history in memory. If a question lacks an explicit subject but contains pronouns or implicit indicators (e.g., `"Where does it live?"` or `"What is its speed?"`), the system automatically resolves the pronoun references using the last active concept in `ConversationManager` and resumes deduction.

### 2. Multi-World Sandbox & Real-time Fact Ingestion
* **Context-Driven Sandbox:** The system recognizes scenario shifts from the input (e.g., `"In a fantasy world..."`) and clones the main graph into an isolated sandbox to run hypothetical reasoning.
* **Zero-LLM Fact Ingestion:** When teaching the system a declarative statement (e.g., `"In a fantasy world, the sun rises from the west"`), the engine parses the sentence structure, extracts concepts/relations locally, and updates the graph without relying on an external AI model.

### 3. Conflict Resolution & Knowledge Update System
When ingesting new facts that conflict with existing ones, the system uses a multi-tier resolution logic:
* **Confidence Auto-Resolution:** If the confidence difference between the new fact and old fact is $> 0.3$, the higher-confidence fact is kept, and the other is archived.
* **Interactive Resolution:** If the confidence difference is $< 0.3$, the CLI prompts the user to select whether to overwrite, merge, or ignore the new fact.

### 4. Spreading Activation (Semantic Disambiguation)
If a word has multiple semantic meanings (e.g., homographs like `"عين"` which can mean `c_eye_human` or `c_spring_water`), the system triggers a Spreading Activation algorithm. Starting from the context concepts tracked in the active session, activation energy flows through adjacent nodes. The node accumulating the highest energy is selected as the correct meaning.

### 5. Multilingual Persona Engine
All responses are formatted based on three variables:
* **Language (ar, en, fr, etc.):** Translated responses and logical trace chains.
* **Persona Selection:** Dynamic assignment of one of three personas:
  1. **Sage Friend:** Compassionate, thorough, calm, and friendly.
  2. **Scientist:** Formal, data-driven, objective, and precise.
  3. **Witty Mentor:** Engaging, energetic, humorous, and uses colloquial tags.
* **Trace Translation:** Translates the graph's internal nodes and relationships (e.g., `is_a` $\to$ `is a subcategory of`) to match the selected output language.

---

## 🔍 Detailed Feature Match & Gap Analysis

| Feature | Implementation Status | Path / File Responsibility |
| :--- | :---: | :--- |
| **1. Morphological Analyzer** | **Fully Implemented** | `src/graph_handler.py` ([dynamic_morphological_lookup](file:///home/zean/Projects/TheOne/src/graph_handler.py#L373)), [language_rules.json](file:///home/zean/Projects/TheOne/data/language_rules.json) |
| **2. Spreading Activation** | **Fully Implemented** | `src/graph_handler.py` ([spreading_activation](file:///home/zean/Projects/TheOne/src/graph_handler.py#L484)) |
| **3. Inference Rules** | **Fully Implemented** | `src/graph_handler.py` ([infer_facts](file:///home/zean/Projects/TheOne/src/graph_handler.py#L585)), [inference_rules.json](file:///home/zean/Projects/TheOne/data/inference_rules.json) |
| **4. Knowledge Update & Conflicts** | **Fully Implemented** | `src/graph_handler.py` ([add_or_update_fact](file:///home/zean/Projects/TheOne/src/graph_handler.py#L65)), `main.py` |
| **5. LLM Prompt Ingestion** | **Design-Only / Not Needed** | Replaced by 100% local, offline Zero-LLM symbolic fact parser |
| **6. Lexicon & Mappings** | **Partially Implemented** | [language_rules.json](file:///home/zean/Projects/TheOne/data/language_rules.json) (Roots, patterns, affixes, and translations) |
| **7. Entity & Pronoun Resolution** | **Fully Implemented** | `src/entity_resolver.py` ([EntityResolver](file:///home/zean/Projects/TheOne/src/entity_resolver.py#L1)), `src/conversation_manager.py` |
| **8. Trace Chain Translation** | **Fully Implemented** | `src/renderer/expression_renderer.py` ([translate_trace_step](file:///home/zean/Projects/TheOne/src/renderer/expression_renderer.py#L96)) |

---

## 🛠️ Technology Stack

* **Programming Language:** `Python 3.12+`
* **Knowledge Graph Engine:** `NetworkX`
* **Testing Framework:** `pytest`
