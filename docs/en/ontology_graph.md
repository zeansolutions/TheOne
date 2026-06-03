# Ontology & Knowledge Graph Representation

## 📋 Overview
The core of **TheOne** reasoning engine is a local, symbolic **Knowledge Graph** represented as a NetworkX `MultiDiGraph` (directed multigraph supporting multiple parallel edges between concepts). 
The ontology defines concepts (nodes) and taxonomies, while the database records facts (edges) representing specific assertions.

---

## 📂 Responsible Files
* **Source Code:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py)
* **Ontology File:** [data/animals_ontology_small.json](file:///home/zean/Projects/TheOne/data/animals_ontology_small.json)
* **Facts File:** [data/animals_facts.json](file:///home/zean/Projects/TheOne/data/animals_facts.json)

---

## ⚙️ Python API Details

### `GraphHandler` Class
Located in `src/graph_handler.py`. Manages the NetworkX graph, loads databases, and updates relationships.

#### `__init__(self)`
* **Description:** Initializes an empty NetworkX `MultiDiGraph` and default settings.
* **Returns:** None

#### `load_databases(self, ontology_path, facts_path, language_rules_path)`
* **Description:** Parses ontology, facts, and language rules from JSON, populating the nodes and edges.
* **Arguments:**
  * `ontology_path` (*str*): Path to ontology JSON.
  * `facts_path` (*str*): Path to facts JSON.
  * `language_rules_path` (*str*): Path to language rules JSON.
* **Returns:** None

#### `get_parent(self, concept_id, relation="is_a")`
* **Description:** Returns the parent concept ID matching the specified relation (e.g. taxonomic parent).
* **Arguments:**
  * `concept_id` (*str*): The starting concept ID.
  * `relation` (*str*): Relation key, default `"is_a"`.
  * **Returns:** `str` concept ID, or `None`.

---

## 🖥️ Terminal Usage
1. Run the interactive CLI:
   ```bash
   ./start.sh run
   ```
2. Select Option **2** to print the current knowledge graph.
3. The terminal prints all registered concepts (grouped by category) and active links, including the world context.
