# 10 Advanced Cognitive Reasoning Layers

## 📋 Overview
To support deep cognitive reasoning without resorting to statistical LLM models at runtime, **TheOne** integrates **10 Advanced Symbolic Reasoning Layers** that handle complex linguistic structures, logical operators, and semantic contexts.

---

## 📂 Responsible Files
* **Processors Folder:** `src/reasoner/`
* **JSON Databases:** `data/`
* **Integration Module:** [src/simple_reasoner.py](file:///home/zean/Projects/TheOne/src/simple_reasoner.py)

---

## ⚙️ Cognitive Layers & Python API Details

Each layer is implemented as a dedicated class model in `src/reasoner/`:

### 1. Semantic Roles Layer (`semantic_processor.py` / `semantic_roles.json`)
* **Role:** Maps verbs to semantic argument frames (`AGENT`, `PATIENT`, `LOCATION`, `TIME`).
* **Method:** `extract_semantic_roles(self, words, language, graph_handler)`

### 2. Temporal Logic Layer (`temporal_processor.py` / `temporal_logic.json`)
* **Role:** Detects event temporal relations (`BEFORE`, `AFTER`, `DURING`) and sorts timelines.
* **Method:** `apply_temporal_reasoning(self, facts, query, language)`

### 3. Modality Layer (`modality_processor.py` / `modality.json`)
* **Role:** Identifies logical necessity, possibility, or impossibility modifiers (e.g. "must", "can").
* **Method:** `process_modality(self, text, language)`

### 4. Causal Chains Layer (`chain_processor.py` / `causal_chains.json`)
* **Role:** Propagates chains of cause and effect through multiple causal hops.
* **Method:** `propagate_causal_chains(self, initial_state, graph_handler)`

### 5. Quantifiers Layer (`quantifier_processor.py` / `quantifiers.json`)
* **Role:** Evaluates universal (`FORALL`), existential (`EXISTS`), and majority scopes in statements.
* **Method:** `evaluate_quantifiers(self, statement, query, graph_handler)`

### 6. Negation Layer (`negation_processor.py` / `negation_rules.json`)
* **Role:** Identifies logical negation and maps negated concepts to opposite antonyms.
* **Method:** `apply_negation(self, query, language)`

### 7. Logical Entailment Layer (`entailment_processor.py` / `entailment.json`)
* **Role:** Assesses if a premise logically entails a hypothesis and flags contradictions.
* **Method:** `check_entailment_and_contradiction(self, premise, hypothesis, graph_handler)`

### 8. Pragmatics Layer (`pragmatic_processor.py` / `pragmatic_knowledge.json`)
* **Role:** Resolves cultural metaphors, non-literal phrases, and implicatures.
* **Method:** `resolve_pragmatics(self, concept_id, query_context)`

### 9. Comparison Layer (`comparison_processor.py` / `comparison.json`)
* **Role:** Evaluates comparative structures (strength, size, speed scales) using transitive sorting.
* **Method:** `evaluate_comparison(self, entity1, entity2, property_name)`

### 10. Anomaly Detection Layer (`anomaly_processor.py` / `anomaly_detection.json`)
* **Role:** Flags unusual attributes or properties violating typical rules, computing an anomaly score.
* **Method:** `detect_anomaly(self, entity, property_name, graph_handler)`

---

## 🖥️ Terminal Usage
1. To run automated tests for all 10 layers, execute:
   ```bash
   ./start.sh test
   ```
2. In the interactive CLI (Option **1**), ask complex questions. For example:
   * **Negation:** `"Is a lion not an animal?"` (System detects negation operator and rejects the premise).
   * **Comparison:** `"Which is faster, a lion or a polar bear?"` (System resolves speeds and returns the comparison result).
   * **Temporal:** `"Does event A happen before event B?"`
   * **Anomaly:** `"A lion that eats grass"` (System flags as an anomaly with confidence deduction).
