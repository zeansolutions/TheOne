<p align="center">
  <img src="images/logo.png" alt="TheOne Logo" width="220px" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"/>
</p>

<h1 align="center">TheOne — Neuro-Symbolic AI Engine 🧠🔗</h1>

<p align="center">
  <strong>Honest, Transparent, and 100% Hallucination-Free Symbolic-Hybrid Reasoning Engine</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tests-54%20passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests status"/>
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
│   ├── personas_multilingual.json    # Persona archetypes (Sage Friend, Scientist, Witty Mentor)
│   └── cli_translations.json         # CLI Localization strings for 11 languages
│
├── data/                             # Zero-State Database & Config Rules (JSON)
│   ├── ontology.json                 # Core concepts and taxonomic relations (Starts empty)
│   ├── facts.json                    # Fact triples segmented by worlds/personas (Starts empty)
│   ├── language_rules.json           # Morphological roots/affixes for translation (Starts empty)
│   ├── inference_rules.json          # Logical inference rules (Horn clauses)
│   ├── relations_metadata.json       # Metadata for relation types (Transitive, symmetric, decay)
│   ├── semantic_roles.json           # Semantic frames (Agent, Patient, Location)
│   ├── temporal_logic.json           # Temporal relations (BEFORE, AFTER)
│   ├── modalities.json               # Modal logic rules (Necessity, Possibility)
│   ├── causal_chains.json            # Causal propagation rules and chains
│   ├── quantifiers.json              # Quantifier rules (Universal, Existential)
│   ├── negation_rules.json           # Polarity rules and double negation mappings
│   ├── entailment.json               # Propositional entailments and contradictions
│   ├── pragmatic_knowledge.json      # Metaphorical and cultural context mappings
│   ├── comparison.json               # Comparative ordering scales and relations
│   └── anomaly_detection.json        # Exceptional facts and anomaly rules
│
├── desktop-gui/                      # Futuristic Electron & React Desktop Application
│   ├── main.js                       # Electron Main Process (Spawns Python API & BrowserWindow)
│   ├── package.json                  # GUI dependencies and launch scripts
│   ├── preload.js                    # Secure Electron preload bridging
│   ├── src/                          # React Frontend Source
│   │   ├── main.jsx                  # React entry point
│   │   ├── App.jsx                   # Central layout, state manager, and tools dashboard
│   │   ├── PhysicsGraph.jsx          # Interactive D3-like physics-based graph renderer
│   │   ├── index.css                 # Glassmorphic and futuristic styling
│   │   └── translations.js           # GUI localization for 11 supported languages
│   └── vite.config.js                # React-Vite configurations
│
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
│   │   ├── db_io_handler.py          # Modular Database I/O, save/load, and JSON importer
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
├── tests/                            # Automated Pytest Suite
│   ├── mock_data/                    # Isolated Mock Test Data
│   │   ├── animals_facts.json        # Animals mock facts for test cases
│   │   ├── animals_ontology_small.json # Animals mock ontology for test cases
│   │   └── animals_language_rules.json # Animals mock language rules for test cases
│   └── test_*.py                     # Unit test suites for reasoner layers
│
├── docs/                             # Project Feature Documentation
│   ├── en/                           # Feature descriptions in English
│   └── ar/                           # Feature descriptions in Arabic
│
├── api.py                            # Custom Python HTTP REST API Server
├── main.py                           # Primary Interactive CLI entrypoint
├── start.sh                          # Interactive setup, test, GUI, and runner script
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore patterns
└── README.md                         # This readme file
```

---

## 🚀 Quick Start

The interactive wrapper script `start.sh` is provided to simplify dependencies setup, testing, and running both CLI and GUI interfaces.

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

### 4. Run the Futuristic Electron Desktop GUI:
```bash
./start.sh gui
```
*(This automatically runs npm dependency installations, builds the React app, spawns the local Python REST API on port 8000 in the background, and launches the desktop app. Everything closes cleanly upon window exit.)*

### 5. Run the Automated Tests (pytest):
```bash
./start.sh test
```

---

## 💻 Futuristic Electron Desktop GUI & HTTP API Server

The system features a **Futuristic Glassmorphic Desktop GUI** and a **Custom Python HTTP API Server** designed to provide a rich visual and administrative control panel over the Neuro-Symbolic Cognitive Engine.

### 📺 React & Electron GUI Features:
1. **Interactive Neural Graph Visualizer:** Renders the Knowledge Graph dynamically using a simulated 2D physics layout. Clicking concepts highlights related pathways and loads them directly into the teaching inputs.
2. **Interactive Chat Dashboard:** Chat with the reasoning engine in real-time, select target output personas, observe the elapsed reasoning time in milliseconds, and inspect the structural logical trace chain behind every deduction.
3. **Dynamic Ingestion & Fact Teaching:** Teach the system new assertions by setting Subjects, Objects, Predicates, Worlds, Modality modifiers, and Confidence levels. You can also register custom logical relations (transitive, symmetric, confidence decay).
4. **Interactive Conflict Resolution Modal:** Visual popups guide you when entering contradictory statements. Choose between overwriting the old fact, merging them as parallel paths, or ignoring the new assertion.
5. **Cognitive Sleep Cycle Controller:** Instantly trigger the dream/sleep sequence, set sleep search depths, and monitor memory consolidation logs and pruned connections.
6. **Procedural Step Builder:** Register and delete step-by-step cognitive procedures associated with specific actions or tasks.
7. **Database Import/Export & Clear Panels:** Import knowledge batches directly using JSON, or clear specific worlds, fact DBs, or reset the entire system.
8. **11-Language Layout Engine:** Full localization in 11 languages with automatic LTR (Left-to-Right) and RTL (Right-to-Left) direction shifts for language inputs, text boxes, and sidebar panels.

### 🚀 Python HTTP API Server (`api.py`):
Running on `http://localhost:8000`, the server acts as the bridge between the Electron GUI and the underlying Python symbolic engine.
* **GET `/api/status`** - Retrieves system status, counts of active nodes/facts, active world/language, and registered relations.
* **GET `/api/graph`** - Exports full nodes and edges data for the physics simulation.
* **GET `/api/curiosity`** - Formulates curiosity questions to prompt user for missing knowledge.
* **GET `/api/worlds`** - Lists all current active logic worlds.
* **POST `/api/query`** - Routes natural language queries, running reasoning, persona, and trace generation.
* **POST `/api/teach`** - Dynamic insertion of concepts/facts and automated contradiction detection.
* **POST `/api/resolve_conflict`** - Submits action to resolve logic conflicts (`replace`, `merge`, `ignore`).
* **POST `/api/sleep`** - Triggers a background sleep cycle to optimize memory.
* **POST `/api/set_language`** & **`/api/set_world`** - Controls environment state.
* **POST `/api/add_relation`** & **`/api/delete_edge`** - Performs structural changes to logic definitions.
* **POST `/api/import_json`** & **`/api/clear_db`** - Handles database administration.

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
* **Interactive Resolution:** If the confidence difference is $< 0.3$, the CLI prompts the user or the GUI displays a conflict resolution modal to select whether to overwrite, merge, or ignore the new fact.

### 4. Spreading Activation (Semantic Disambiguation)
If a word has multiple semantic meanings (e.g., homographs like `"عين"` which can mean `c_eye_human` or `c_spring_water`), the system triggers a Spreading Activation algorithm. Starting from the context concepts tracked in the active session, activation energy flows through adjacent nodes. The node accumulating the highest energy is selected as the correct meaning.

### 5. Multilingual Persona Engine
All responses are formatted based on three variables:
* **Language (ar, en, fr, etc.):** Translated responses and logical trace chains.
* **Persona Selection:** Dynamic assignment or forced override of one of three personas:
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
| **4. Knowledge Update & Conflicts** | **Fully Implemented** | `src/graph_handler.py` ([add_or_update_fact](file:///home/zean/Projects/TheOne/src/graph_handler.py#L65)), `api.py`, `main.py` |
| **5. LLM Prompt Ingestion** | **Design-Only / Not Needed** | Replaced by 100% local, offline Zero-LLM symbolic fact parser |
| **6. Lexicon & Mappings** | **Partially Implemented** | [language_rules.json](file:///home/zean/Projects/TheOne/data/language_rules.json) (Roots, patterns, affixes, and translations) |
| **7. Entity & Pronoun Resolution** | **Fully Implemented** | `src/entity_resolver.py` ([EntityResolver](file:///home/zean/Projects/TheOne/src/entity_resolver.py#L1)), `src/conversation_manager.py` |
| **8. Trace Chain Translation** | **Fully Implemented** | `src/renderer/expression_renderer.py` ([translate_trace_step](file:///home/zean/Projects/TheOne/src/renderer/expression_renderer.py#L96)) |

---

## 🛠️ Technology Stack

* **Programming Language:** `Python 3.12+`
* **Knowledge Graph Engine:** `NetworkX`
* **Desktop Application:** `Electron 41.7+` & `React 19.2+` (bundled via `Vite 8.0+`)
* **Styling (CSS):** Custom Vanilla CSS (with cyber-dark and glassmorphic designs)
* **Testing Framework:** `pytest`
