# Multi-World Reasoning & Isolated Sandbox

## 📋 Overview
To support hypothetical reasoning and avoid logic collision, **TheOne** features a **Multi-World System**. Facts are tagged with their specific world context (e.g. `"reality"`, `"arctic_scenario"`, or `"khayali"` / fantasy). 
The **Sandbox** creates an isolated clone of the main Knowledge Graph where hypothetical premises can be tested (e.g. "If a lion lived in the arctic...") without affecting the actual permanent knowledge database.

---

## 📂 Responsible Files
* **Source Code:** [src/world_manager.py](file:///home/zean/Projects/TheOne/src/world_manager.py) and [src/reasoner/sandbox_manager.py](file:///home/zean/Projects/TheOne/src/reasoner/sandbox_manager.py)
* **Configuration:** [data/facts.json](file:///home/zean/Projects/TheOne/data/facts.json) (Fact assertions database)

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
2. Test sandbox hypotheticals by asking questions starting with conditional phrases, e.g.:
   `"If a lion lived in the arctic, what would it require?"`
   The system will automatically clone the graph into a sandbox, inject the condition `lives_in(feline_carnivore, arctic)`, infer the consequences, and display the result.

---

## 🚀 HTTP API & Desktop GUI Integration

### REST API Endpoints:
* **GET `/api/worlds`** - Retrieves the list of all currently tracked logical worlds.
* **POST `/api/set_world`** - Switches the active reasoning world and triggers dynamic forward chaining logic for the target world. Body: `{"world": "world_name"}`.
* **POST `/api/clear_db`** - Deletes a specific world from the database if `type="world"` is passed. Body: `{"type": "world", "world": "world_name"}`.

### Desktop GUI Controls:
* **World Selector Dropdown:** Placed in the top-right corner of the application header, allowing instant swapping between reasoning worlds.
* **Dynamic World Registration:** An inline text box next to the world dropdown allows typing and creating new worlds instantly.
* **World Deletion:** Custom worlds show a delete trash can icon next to them. Clicking it calls `/api/clear_db` to purge all facts associated with that scenario.
