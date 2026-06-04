# Multilingual Persona Selection & Expression Rendering

## 📋 Overview
**TheOne** is equipped with a **Multilingual Persona Engine** that wraps raw logical answers in natural language expressions corresponding to a selected persona.
It evaluates query features and dialogue context to select the most appropriate persona, then renders the response using localized templates and translated reasoning traces.

---

## 📂 Responsible Files
* **Persona Engine:** [src/manager/multilingual_persona_engine.py](file:///home/zean/Projects/TheOne/src/manager/multilingual_persona_engine.py)
* **Persona Selector:** [src/reasoner/persona_selector.py](file:///home/zean/Projects/TheOne/src/reasoner/persona_selector.py)
* **Expression Renderer:** [src/renderer/expression_renderer.py](file:///home/zean/Projects/TheOne/src/renderer/expression_renderer.py)
* **Archetypes Configuration:** [config/personas_multilingual.json](file:///home/zean/Projects/config/personas_multilingual.json)

---

## ⚙️ Python API Details

### `MultilingualPersonaEngine` Class
Coordinates the pipeline in `src/manager/multilingual_persona_engine.py`.

#### `process_response(self, question, logical_response, conversation_history=None, user_preference=None, force_persona_id=None)`
* **Description:** Runs the entire rendering pipeline: detects input language, selects output language, classifies context, selects persona, and formats the output.
* **Arguments:**
  * `question` (*str*): The query string.
  * `logical_response` (*dict*): Structural facts response from reasoner.
  * `conversation_history` (*list*): Context memory turns.
  * `user_preference` (*str*): Target language code override.
  * `force_persona_id` (*str*): Persona ID override (`sage_friend`, `scientist`, or `witty_mentor`).
* **Returns:** `dict` containing `"response"`, `"language"`, `"persona"`, and `"confidence"`.

### `MultilingualPersonaSelector` Class
Located in `src/reasoner/persona_selector.py`. Matches contexts to the best persona:
1. **Sage Friend:** Compassionate, thorough, calm.
2. **Scientist:** Formal, objective, data-driven.
3. **Witty Mentor:** Humorous, energetic, uses light slang.

---

## 🖥️ Terminal & GUI Usage

### Terminal Interaction:
1. Ask the system questions in the terminal (Option **1**).
2. The system outputs which persona generated the response, e.g.:
   ```text
   ==================================================
   Active World: 'reality'
   Language: en | Persona: scientist
   Final Response:
   👉 Based on empirical facts, a lion is a subcategory of animal.
   ==================================================
   ```

### Desktop GUI Integration:
* **Persona Selection Dropdown:** Located right next to the message input box, users can explicitly choose between:
  * **Auto-Select:** Let the system automatically choose based on context matching.
  * **Sage Friend:** Force friendly/calm tone.
  * **Scientist:** Force formal/scientific response.
  * **Witty Mentor:** Force humorous/slang tone.
* **REST API integration:** Passes `force_persona_id` in the POST `/api/query` payload body to override dynamic context selection.
