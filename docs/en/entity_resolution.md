# Entity Resolution & Pronoun Reference Tracking

## 📋 Overview
To maintain conversational coherence in continuous dialogues, **TheOne** features an **Entity Resolution Engine**. If a user enters a question lacking an explicit subject but containing pronouns (e.g. `"Where does it live?"` or `"Is he a predator?"`), the engine resolves the implicit references using the active history of concepts.

---

## 📂 Responsible Files
* **Source Code:** [src/entity_resolver.py](file:///home/zean/Projects/TheOne/src/entity_resolver.py) and [src/conversation_manager.py](file:///home/zean/Projects/TheOne/src/conversation_manager.py)
* **Test Suite:** [tests/test_queries.py](file:///home/zean/Projects/TheOne/tests/test_queries.py)

---

## ⚙️ Python API Details

### `EntityResolver` Class
Located in `src/entity_resolver.py`.

#### `resolve_implicit_subject(self, query, language="en", conversation_manager=None)`
* **Description:** Parses query text to detect implicit pronouns or gender/number agreement markers. If detected, retrieves the last active concept from context memory.
* **Arguments:**
  * `query` (*str*): The raw user query.
  * `language` (*str*): Active locale, defaults to `"en"`.
  * `conversation_manager` (*ConversationManager*): Active state tracker.
* **Returns:** `str` concept ID of resolved subject, or `None`.

### `ConversationManager` Class
Located in `src/conversation_manager.py`.

#### `record_turn(self, query, mapped_concepts, response=None)`
* **Description:** Appends conversational turn details to history and updates the last active concept ID.
* **Returns:** None

#### `get_history(self)`
* **Description:** Returns the complete history list of dialogue turns.
* **Returns:** `list` of turns.

---

## 🖥️ Terminal Usage
1. Open the interactive CLI and select Option **1** (Ask a question).
2. Enter a query with an explicit subject:
   `"Is a lion a predator?"`
   The system answers and stores `feline_carnivore` as the active concept.
3. Immediately follow up with a pronoun-only question:
   `"Where does it live?"`
   The Entity Resolver detects the pronoun `"it"`, maps it to the stored `feline_carnivore` concept, and resolves the query to: `"Where does a lion live?"`, responding with:
   `👉 The lion lives in the savanna.`
