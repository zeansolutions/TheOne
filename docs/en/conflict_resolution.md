# Conflict Resolution & Contradiction Detection

## 📋 Overview
To maintain logical consistency, **TheOne** includes a **Conflict Resolution and Contradiction Detection System**. When teaching the system new facts, it checks for logical collisions (e.g. contradictory properties or multiple objects for functional relations). It automatically resolves these based on confidence scores or prompts the user interactively.

---

## 📂 Responsible Files
* **Source Code:** [src/conflict_resolver.py](file:///home/zean/Projects/TheOne/src/conflict_resolver.py) and [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) (`add_or_update_fact`)
* **Test Suite:** [tests/test_contradiction.py](file:///home/zean/Projects/TheOne/tests/test_contradiction.py)

---

## ⚙️ Python API Details

### `ConflictResolver` Class
Located in `src/conflict_resolver.py`.

#### `resolve_conflict(self, concept_id, relation_type)`
* **Description:** Identifies if a concept has contradicting facts in different worlds.
* **Arguments:**
  * `concept_id` (*str*): Target concept node ID.
  * `relation_type` (*str*): Relation type being checked.
* **Returns:** `list` of conflict detail dictionaries.

### `GraphHandler` (Add/Update Fact)
Located in `src/graph_handler.py`.

#### `add_or_update_fact(self, subj, obj, relation, world, confidence=1.0, reason=None, interactive=False, modality=None, language="en")`
* **Description:** Safely inserts new fact edges, applying the three-tier resolution strategy:
  1. **Auto-Resolution:** Overwrites if new fact confidence is $> 0.3$ higher than current fact, or rejects if current fact is $> 0.3$ higher.
  2. **Interactive Selection / GUI Interception:** If confidence difference is $< 0.3$, raises/indicates a conflict to let the user select between:
     * **Replace:** Delete old fact, add new fact, archive previous fact.
     * **Merge:** Save both parallel facts.
     * **Ignore:** Discard new fact.
* **Returns:** `dict` status report containing success status, conflict flag, and localized message.

---

## 🖥️ Terminal Usage
1. Open the CLI and select Option **3** to teach the system.
2. If teaching a conflicting property in the same world (e.g., teaching `feline_carnivore` $\to$ `thin_fur` when it is already `thick_fur` in world `reality`), the system will halt and prompt you:
   ```text
   ⚠️ [Fact Conflict] The new fact conflicts with a recorded fact in world 'reality'!
   Current fact: [lion] --(has_property)--> [thick fur] (confidence: 1.0)
   New fact: [lion] --(has_property)--> [thin fur] (confidence: 1.0)
   --------------------------------------------------
   Please choose a resolution option:
    1. Replace
    2. Merge
    3. Ignore
   Choose resolution option (1-3): 
   ```

---

## 🚀 HTTP API & Desktop GUI Integration

### REST API Endpoints:
* **POST `/api/teach`** - If a contradiction is detected and confidence difference is $< 0.3$, it returns a status of `"conflict"` along with details of both facts:
  ```json
  {
    "status": "conflict",
    "conflict": {
      "subject": "feline_carnivore",
      "relation": "has_property",
      "old_object": "thick_fur",
      "new_object": "thin_fur",
      "world": "reality"
    }
  }
  ```
* **POST `/api/resolve_conflict`** - Resolves a pending conflict. Accepts body:
  ```json
  {
    "action": "replace | merge | ignore",
    "subject": "subject_concept",
    "relation": "relation_type",
    "old_object": "old_val",
    "new_object": "new_val",
    "world": "world_name",
    "confidence": 1.0,
    "modality": "modality_val",
    "reason": "reason_string"
  }
  ```

### Desktop GUI Conflict Modal:
In the desktop app, when teaching a fact through the Teach dashboard that triggers a logical contradiction, an elegant **Conflict Resolution Glassmorphic Modal** pops up automatically. 
It displays side-by-side cards comparing the current fact and the new conflicting assertion, and presents three clear buttons:
1. **Overwrite / Replace:** Replaces the old assertion with the new one.
2. **Merge Parallel:** Retains both facts concurrently.
3. **Discard / Ignore:** Dismisses the new assertion, keeping the original database intact.
