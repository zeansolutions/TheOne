# Ontology & Knowledge Graph Representation

## 📋 Overview
The core of **TheOne** reasoning engine is a local, symbolic **Knowledge Graph** represented as a NetworkX `MultiDiGraph` (directed multigraph supporting multiple parallel edges between concepts). 
The ontology defines concepts (nodes) and taxonomies, while the database records facts (edges) representing specific assertions.

---

## 📂 Responsible Files
* **Source Code:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) and [src/maintenance/db_io_handler.py](file:///home/zean/Projects/TheOne/src/maintenance/db_io_handler.py)
* **Ontology File:** [data/ontology.json](file:///home/zean/Projects/TheOne/data/ontology.json) (Zero-state base concepts and taxonomy)
* **Facts File:** [data/facts.json](file:///home/zean/Projects/TheOne/data/facts.json) (Zero-state fact assertions)

---

## ⚙️ Python API Details

### `GraphHandler` & `DbIoHandler`
Located in `src/graph_handler.py` and `src/maintenance/db_io_handler.py`. Manages the NetworkX graph, loads/saves databases, and handles data ingestion.

#### `load_databases(self, ontology_path, facts_path, language_rules_path)`
* **Description:** Parses ontology, facts, and language rules from JSON, populating the nodes and edges by delegating to `DbIoHandler`.
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

## 🚀 HTTP API & Desktop GUI Integration

### REST API Endpoint:
* **GET `/api/graph`**: Exports the entire list of nodes and edges in the graph in a format compatible with front-end visualizers:
  ```json
  {
    "nodes": [{"id": "concept_id", "label": "Concept Label", "category": "category_name", "type": "concept"}],
    "edges": [{"source": "u", "target": "v", "relation": "relation_name", "world": "reality", "confidence": 1.0, "type": "fact"}]
  }
  ```

### Desktop GUI Visualizer:
The Electron GUI provides a beautiful **Interactive Neural Graph Visualizer** built with Canvas-based physics simulations. 
* Concepts are rendered as nodes (color-coded by category).
* Relationships are rendered as directed lines.
* Dashed pink lines represent dynamically inferred relationships.
* Clicking any node selects it, highlighting its active pathways and populating it into the facts-teaching form for ease of use.
