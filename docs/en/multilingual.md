# Language Selection & Detection Engine

## 📋 Overview
**TheOne** supports automated multi-language interaction. The **Language Selection Engine** automatically detects the input language from the query using character pattern checking (e.g. Arabic unicode range check) and keyword dictionaries. It then selects the optimal output language based on user preference, detected language, and context history.

---

## 📂 Responsible Files
* **Source Code:** [src/manager/language_selection_engine.py](file:///home/zean/Projects/TheOne/src/manager/language_selection_engine.py)
* **Configuration:** [config/languages.json](file:///home/zean/Projects/TheOne/config/languages.json)

---

## ⚙️ Python API Details

### `LanguageSelectionEngine` Class
Located in `src/manager/language_selection_engine.py`.

#### `__init__(self, languages_data)`
* **Description:** Initializes supported languages and sets default locale to `"en"`.
* **Arguments:**
  * `languages_data` (*dict* or *str*): Parsed JSON config or path to `languages.json`.

#### `detect_language(self, text)`
* **Description:** Inspects characters and vocabulary tokens to return the language ID (e.g. `"ar"`, `"en"`, or `"fr"`).
* **Arguments:**
  * `text` (*str*): The query string.
* **Returns:** `str` language ID.

#### `select_language(self, detected_lang, user_preference=None, conversation_history=None)`
* **Description:** Applies selection priority: `user_preference` $\to$ `detected_lang` $\to$ `history` $\to$ `default_language`.
* **Returns:** Verified `str` language ID.

---

## 🖥️ Terminal Usage
1. Start the CLI:
   ```bash
   ./start.sh run
   ```
2. You can switch the CLI menu interface language to any of the 11 supported languages by choosing Option **5** and entering its code (e.g. `ar` for Arabic, `fr` for French, `tr` for Turkish, `zh` for Chinese).
3. The prompt automatically translates itself to the selected language, while maintaining the primary reasoner's ability to answer in the same language.
