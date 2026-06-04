# Dynamic Inference & Forward Chaining Engine

## 📋 Overview
**TheOne** implements a dynamic, symbolic **Forward Chaining Inference Engine** (Zero-LLM at runtime). Instead of hardcoding logic, it loads logical rules (Horn clauses) represented as conditional patterns (premises) with variables. It evaluates these against the active Knowledge Graph to iteratively deduce new relationships until it reaches a fixpoint (no new relations can be inferred).

---

## 📂 Responsible Files
* **Source Code:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) (`infer_facts`, `find_bindings`) and [src/reasoner/transitive_chaining.py](file:///home/zean/Projects/TheOne/src/reasoner/transitive_chaining.py)
* **Rules Configuration:** [data/inference_rules.json](file:///home/zean/Projects/TheOne/data/inference_rules.json) and [data/relations_metadata.json](file:///home/zean/Projects/TheOne/data/relations_metadata.json)

---

## ⚙️ Python API Details

### `GraphHandler` (Rules & Forward Chaining)
Methods in `GraphHandler` class to run logic induction.

#### `find_bindings(self, conditions, bindings=None)`
* **Description:** Recurses and searches the graph for concept variable bindings (e.g. matching `?x` to a specific concept) that satisfy all condition triples.
* **Arguments:**
  * `conditions` (*list*): List of condition dictionaries.
  * `bindings` (*dict*): Current variable assignments, defaults to `None`.
* **Returns:** `list` of matching `dict` bindings.

#### `infer_facts(self, world_name)`
* **Description:** Runs the iterative forward chaining loop. Evaluates loaded rules against the active world facts and inserts new edges of type `"inferred"`. Stops when no new edges are added.
* **Arguments:**
  * `world_name` (*str*): Target world to run reasoning on.
* **Returns:** `list` of inferred facts trace descriptions.

### `TransitiveChainingReasoner` Class
Located in `src/reasoner/transitive_chaining.py`. Handles relations configured as transitive (like `is_a`, `part_of`).

#### `compute_transitive_relations(self, concept, relation_type, world)`
* **Description:** Traverses the graph to trace multi-hop transitive paths (e.g. A is-a B, B is-a C $\implies$ A is-a C).
* **Returns:** `list` of target concepts reached.

---

## 🖥️ Terminal Usage
1. Inference rules are executed automatically whenever you ask a question (Option **1**).
2. If trace level is set to `"detailed"` (default), the step-by-step logic trace is printed in the terminal:
   ```text
   👉 Final Response:
   Yes, a lion is a predator.
   
   Reasoning Trace:
   - Inference: lion is_a feline_carnivore based on database ontology
   - Inference: feline_carnivore is_a carnivore based on database ontology
   - Inferred Fact: lion is_a carnivore based on rule 'Taxonomic Inheritance'
   ```

---

## 🚀 HTTP API & Desktop GUI Integration

### REST API Trace Outputs:
When submitting a POST query to `/api/query`, the response JSON payload includes a `"trace"` array showing each inference step:
```json
{
  "response": "Yes, a lion is a predator.",
  "trace": [
    "Inference: lion is_a feline_carnivore based on database ontology",
    "Inference: feline_carnivore is_a carnivore based on database ontology",
    "Inferred Fact: lion is_a carnivore based on rule 'Taxonomic Inheritance'"
  ],
  "elapsed_ms": 12.5
}
```

### Desktop GUI Inferred Representations:
* **Interactive Physics Graph:** Inferred edges are rendered dynamically as **dashed pink lines**, distinguishing them from ground-truth database facts (rendered as solid colored lines).
* **Chat Trace Accordion:** Below each chat response bubble, a collapsable "Reasoning Trace" panel shows the step-by-step deduction path along with the reasoning duration in milliseconds.
* **Trace Translation:** The renderer translates the internal concepts and relationship IDs (e.g., `lives_in` or `is_a`) to the active GUI language so that the trace is readable to the user in their selected language.
