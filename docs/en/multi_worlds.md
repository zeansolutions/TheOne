# Multi-World Reasoning & Isolated Sandbox

## 📋 Overview
To support hypothetical reasoning and avoid logic collision, **TheOne** features a **Multi-World System**. Facts are tagged with their specific world context (e.g. `"reality"`, `"arctic_scenario"`, or `"خيالي"` / fantasy). 
The **Sandbox** creates an isolated clone of the main Knowledge Graph where hypothetical premises can be tested (e.g. "If a lion lived in the arctic...") without affecting the actual permanent knowledge.

---

## 📂 Responsible Files
* **Source Code:** [src/world_manager.py](file:///home/zean/Projects/TheOne/src/world_manager.py) and [src/reasoner/sandbox_manager.py](file:///home/zean/Projects/TheOne/src/reasoner/sandbox_manager.py)
* **Configuration:** [data/animals_facts.json](file:///home/zean/Projects/TheOne/data/animals_facts.json)

---

## ⚙️ Python API Details

### `WorldManager` Class
Located in `src/world_manager.py`. Manages active world state, detects scenario modifiers in user questions, and extracts facts from statements.

#### `parse_query_context(self, query)`
* **Description:** Detects if the query specifies a hypothetical or fantasy world, changes the active world state, and returns a cleaned query.
* **Arguments:**
  * `query` (*str*): The raw user query.
* **Returns:** `tuple` of `(cleaned_query, world_name)`

#### `parse_and_add_fact(self, text, world, interactive=False, language="en")`
* **Description:** Extracts subject-relation-object triples from text offline and adds them to the graph.
* **Arguments:**
  * `text` (*str*): The declarative statement text.
  * `world` (*str*): Target world to save the fact in.
  * `interactive` (*bool*): Enable user interactive prompts for contradictions.
  * `language` (*str*): Ingestion language.
* **Returns:** `dict` status report.

### `SandboxManager` Class
Located in `src/reasoner/sandbox_manager.py`. Clones and manages temporary graphs.

#### `create_sandbox(self, temporary_facts=None)`
* **Description:** Clones the active Graph, marks it as `is_sandbox=True`, and applies temporary facts for isolated evaluation.
* **Returns:** Cloned NetworkX graph instance.

---

## 🖥️ Terminal Usage
1. Run the interactive CLI:
   ```bash
   ./start.sh run
   ```
2. Select Option **4** to display all stored fact worlds and check which world is currently active.
3. Test sandbox hypotheticals by asking questions starting with conditional phrases, e.g.:
   `"If a lion lived in the arctic, what would it require?"`
   The system will automatically clone the graph into a sandbox, inject the condition `lives_in(feline_carnivore, arctic)`, infer the consequences, and display the result.
