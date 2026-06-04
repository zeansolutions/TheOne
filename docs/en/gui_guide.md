# GUI User Guide (GUI Guide) 🧠💻

Welcome to the **TheOne (Reasoning Engine)** GUI User Guide. This document provides a detailed, practical walkthrough of every tab, button, input, slider, and option in the Graphical User Interface (GUI) to help you fully control the Neuro-Symbolic Cognitive Engine.

---

## 🧭 GUI Layout & Navigation

The interface consists of **5 main tabs** at the top left of the screen, and the **Interactive Knowledge Graph** on the right.

---

## 1. 🧠 Tab: Cognitive Chat
This tab is your primary interface for conversing with the system and querying its logical capabilities.

* **Input Bar:** Where you write questions and queries in Arabic, English, or French.
* **"Reason" Button:** Triggers the logical reasoning pipeline.
* **Detailed Logical Trace:**
  * Shows **every single cognitive step** taken by the reasoning engine to arrive at the answer.
  * Details which inference rules were loaded, what worlds were traversed, and which transitive paths were resolved.
* **Performance Metrics:**
  * **Confidence:** The final accumulated certainty level of the response.
  * **Processing Time:** The duration (in milliseconds) it took the logic engine to complete reasoning.

### 💡 Query Examples:
* **Taxonomy Query:** *"Is a lion an animal?"* (Engine checks the transitive `is_a` path).
* **Hypothetical Sandbox:** *"If a lion lived in the arctic, what would it require?"* (Clones the graph into a sandbox, applies the premise, reasons about the environment, performs an analogy candidate lookup, and deduces the need for `thick_fur`).
* **Comparison:** *"What is the difference between a lion and a polar bear?"* (Performs a property comparison between the two nodes).

---

## 2. 🗄️ Tab: DB & Ingest
This tab provides full control over teaching the engine and managing databases. It is split into four panels:

### A. Teach the System a New Fact
Write custom assertions to build the knowledge graph:
* **Source / Subject:** The subject of the relation (e.g., `gold` or `lion`).
* **Target / Object:** The object or value of the relation (e.g., `metal` or `savanna`).
* **Relation Type:** Select the connection type (e.g., `is_a`, `lives_in`, or any custom relation you define).
* **World:** Select the reasoning world. The default is `reality`. You can write custom worlds (like `fantasy`) to isolate hypothetical facts.
* **Modality Modifier (Optional):**
  * Describes the modal necessity or frequency:
    * `No modifier` (Default): Declarative fact (e.g., "A lion is a carnivore").
    * `Must / Necessarily`: A strict logical requirement (e.g., "A living being must breathe").
    * `Maybe / Possibly`: An optional or tentative connection.
    * `Typically / Usually`: A general default behavior that permits exceptions (e.g., "Birds typically fly"). This feeds the Anomaly Detection engine when exception cases (e.g., "Penguins do not fly") occur.
* **Confidence Slider:**
  * A coefficient from `0.0` to `1.0` reflecting the credibility of the fact. Used in accumulative logical reasoning and resolving contradictions (higher confidence wins).

### B. Define New Relation
Create custom properties for relationships:
* **Relation ID:** The programmatic name of the link (e.g., `contains`, `part_of`).
* **Display Name / Arabic Name:** The verbal representation used in final generated responses (e.g., `يحتوي على`).
* **"Transitive" Checkbox:** Check this if the relation propagates (e.g., if A is a part of B, and B is a part of C, then A is a part of C).
* **"Symmetric" Checkbox:** Check this if the relation is bidirectional (e.g., if A is a sibling of B, then B is a sibling of A).

### C. Ingest Knowledge from JSON
Import entire knowledge bases (concepts, relations, facts, rules) at once by pasting a formatted JSON array.

### D. Danger Zone
* **Clear Facts Database Only:** Purges learned facts while leaving the base ontology intact.
* **Reset Entire Database:** Wipes both facts and the core ontology, resetting the engine to a blank state.
* **Delete World:** Irreversibly deletes a specific custom reasoning world.

#### ⚠️ Contradiction Resolution Popup:
If you try to teach the engine a fact that contradicts an existing assertion (e.g., "Lions are herbivores" vs "Lions are carnivores"), a popup will prompt you to choose:
1. **Overwrite:** Deletes the old fact and stores the new one.
2. **Merge:** Keeps both facts simultaneously (useful for fuzzy systems).
3. **Ignore:** Discards the new fact and keeps the original.

---

## 3. 💤 Tab: Sleep & Curiosity
A maintenance center for the system's self-organization.

* **Cognitive Sleep Cycle:**
  * Clicking **"Execute Sleep Cycle"** runs background consolidation processes:
    1. **Spelling Merges:** Joins duplicate nodes with minor grammatical or spelling differences.
    2. **Pruning:** Deletes low-confidence edges that have never contributed to successful reasoning chains to free memory.
* **Curiosity Engine:**
  * Identifies nodes with a high **Mystery Score** (concepts mentioned in relations but lacking definition details).
  * Prompts you to teach the system about these concepts to resolve knowledge gaps.

---

## 4. ⚡ Tab: Procedures
Allows formulating sequential thinking recipes or step-by-step action plans to solve complex logical puzzles.

* Write plans manually by adding steps.
* Or use an AI provider (e.g. Gemini by supplying an API Key) to analyze a natural-language description of a logical puzzle and auto-generate the sequential reasoning steps.

---

## 5. 📺 Tab: Logic Engine Monitor
Displays real-time logs from the underlying core:
* Parser tokens and grammar matching.
* Morphological affix stripping.
* Spreading activation weights.
* API execution logs.

---

## 📊 Interactive Knowledge Graph
A 2D/3D physics-based visual representation of the neural-symbolic graph:
* **Semantic Color Legend:**
  * **Bright Central Hub:** The active concept you queried.
  * **Super Class / Category:** Class taxonomic nodes (e.g., `animal`, `carnivore`).
  * **Leaf Node / Property:** Attribute nodes (e.g., `savanna`, `thick_fur`).
  * **Isolated Node:** Unconnected concepts.
* **Controls:**
  * Scroll to zoom, click and drag to pan and organize.
  * Click on any edge to trigger `Delete Relation`.
  * Click **"Center View"** to center and scale the graph projection.
