# Language Selection & Detection Engine

## 📋 Overview
**TheOne** supports dynamic multi-language interaction at both the terminal and graphical layers. The **Language Selection Engine** automatically detects the input language from the query using character pattern checking (e.g. Arabic Unicode range matching) and vocabulary lookup, and selects the optimal output language based on user preference, detected language, and context history.

---

## 📂 Responsible Files
* **Source Code:** [src/manager/language_selection_engine.py](file:///home/zean/Projects/TheOne/src/manager/language_selection_engine.py)
* **Configuration:** [config/languages.json](file:///home/zean/Projects/TheOne/config/languages.json)
* **Localization Files:** [config/cli_translations.json](file:///home/zean/Projects/TheOne/config/cli_translations.json) (CLI) and [desktop-gui/src/translations.js](file:///home/zean/Projects/TheOne/desktop-gui/src/translations.js) (GUI)

---

## ⚙️ Python API Details

### `LanguageSelectionEngine` Class
Located in `src/manager/language_selection_engine.py`.

#### `__init__(self, languages_data)`
* **Description:** Initializes supported languages and sets default locale to `"en"`.
* **Arguments:**
  * `languages_data` (*dict* or *str*): Parsed JSON config or path to `languages.json`.

#### `detect_language(self, text)`
* **Description:** Inspects characters and vocabulary tokens to return the language ID (e.g., `"ar"`, `"en"`, or `"fr"`). Supports detecting 11 languages.
* **Arguments:**
  * `text` (*str*): The query string.
* **Returns:** `str` language ID.

#### `select_language(self, detected_lang, user_preference=None, conversation_history=None)`
* **Description:** Applies selection priority: `user_preference` $\to$ `detected_lang` $\to$ `history` $\to$ `default_language`.
* **Returns:** Verified `str` language ID.

---

## 🖥️ Terminal & GUI Usage

### Supported Languages (11 Locales):
The system fully supports 11 languages:
1. **English (en)**
2. **Arabic (ar)** (RTL)
3. **French (fr)**
4. **Spanish (es)**
5. **Chinese (zh)**
6. **Turkish (tr)**
7. **German (de)**
8. **Russian (ru)**
9. **Portuguese (pt)**
10. **Japanese (ja)**
11. **Korean (ko)**

### Terminal Interface:
1. Start the CLI:
   ```bash
   ./start.sh run
   ```
2. Switch the CLI menu language to any of the 11 supported languages by choosing Option **5** and entering its code (e.g. `ar` for Arabic, `fr` for French, `tr` for Turkish, `zh` for Chinese).
3. The prompt automatically translates itself to the selected language, while maintaining the primary reasoner's ability to answer in the same language.

### Desktop GUI Interface:
* **Language Selector Dropdown:** Located in the top header, allowing the user to select the primary language.
* **Dynamic Direction (RTL/LTR) Shifts:** If Arabic (`ar`) is selected, the application layout dynamically flips into a Right-to-Left (RTL) layout. The sidebars, chat bubbles, buttons, and inputs align correctly to support Arabic reading and writing flows. Selecting any of the other 10 LTR languages automatically reverts the layout direction back to LTR.
