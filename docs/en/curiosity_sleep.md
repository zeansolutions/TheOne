# Curiosity Engine & Cognitive Sleep Cycle

## 📋 Overview
To support continuous learning and memory consolidation, **TheOne** implements two background maintenance systems:
1. **Curiosity Engine:** Identifies gaps in the Knowledge Graph (missing attributes, isolated nodes) and automatically formulates questions to ask the user.
2. **Cognitive Sleep Cycle:** Simulates biological sleep to consolidate memories. It executes transitive chaining, strengthens links repeated in similar contexts, prunes weak probabilistic relationships, and deduplicates nodes.

---

## 📂 Responsible Files
* **Curiosity Engine:** [src/reasoner/curiosity_engine.py](file:///home/zean/Projects/TheOne/src/reasoner/curiosity_engine.py) and [curious.py](file:///home/zean/Projects/TheOne/curious.py)
* **Sleep Cycle:** [src/maintenance/sleep_cycle.py](file:///home/zean/Projects/TheOne/src/maintenance/sleep_cycle.py) and [sleep.py](file:///home/zean/Projects/TheOne/sleep.py)

---

## ⚙️ Python API Details

### `CuriosityEngine` Class
Located in `src/reasoner/curiosity_engine.py`.

#### `generate_curiosity_questions(self, limit=3)`
* **Description:** Identifies nodes with low degrees or missing key semantic relationships, computes a "Mystery Score", and formats natural language questions.
* **Arguments:**
  * `limit` (*int*): Max questions to return.
* **Returns:** `list` of question dictionaries.

### `CognitiveSleepCycle` Class
Located in `src/maintenance/sleep_cycle.py`.

#### `run_sleep_cycle(self)`
* **Description:** Runs consolidation tasks:
  * **Transitive Closure:** Infers and commits transitive links.
  * **Strengthening:** Amplifies confidence weights for active edges.
  * **Pruning:** Deletes edges with confidence $< 0.15$.
  * **Deduplication:** Merges nodes with identical synonyms.
* **Returns:** `dict` summary statistics.

---

## 🖥️ Terminal Usage

### Ingesting Curiosity
You can run the standalone curiosity generator in the background:
```bash
python curious.py
```
This prints active questions generated from Knowledge Graph gaps, e.g.:
`"I notice feline_carnivore is a subcategory of animal, but I don't know where it lives. Where does feline_carnivore live?"`

### Triggering Sleep Cycle
To trigger cognitive sleep and clean the network:
```bash
python sleep.py
```
Output logs:
```text
🌙 Starting Cognitive Sleep Cycle...
  - Running transitive chaining consolidation...
  - Running edge pruning (removing confidence < 0.15)...
  - Running node deduplication...
✅ Sleep cycle finished!
Summary of changes:
  * Synonym links merged: 0
  * Transitive links committed: 2
  * Edges pruned: 1
```
