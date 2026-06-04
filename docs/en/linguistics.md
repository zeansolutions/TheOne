# Morphological Analysis & Linguistic Lookup

## 📋 Overview
To process natural language inputs locally without LLM parsing at runtime, **TheOne** includes a **Morphological Analysis Engine**. For Arabic, it implements an **Iterative Stripping Algorithm** that strips prefixes (like "ال", "و", "في") and suffixes (like "هم", "ين", "ات") and performs root/pattern mapping to match tokens to the correct graph concept IDs.

---

## 📂 Responsible Files
* **Source Code:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) (`dynamic_morphological_lookup`)
* **Grammar File:** [data/language_rules.json](file:///home/zean/Projects/TheOne/data/language_rules.json)

---

## ⚙️ Python API Details

### `GraphHandler` (Morphological Lookup)
Methods in `GraphHandler` class for linguistic search.

#### `dynamic_morphological_lookup(self, word, language="ar")`
* **Description:** Normalizes the input word, iteratively strips affixes, and matches the stripped word or root against concept labels in the target language.
* **Arguments:**
  * `word` (*str*): The word token to analyze.
  * `language` (*str*): The input language, defaults to `"ar"`.
* **Returns:** `str` concept ID (e.g. `"feline_carnivore"` for `"الأسد"`), or `None`.

#### Morphology Rules JSON Format
Defines affixes and roots in `language_rules.json`:
```json
"morphology": {
  "prefixes": ["ال", "و", "في", "بـ", "لـ", "كـ"],
  "suffixes": ["ه", "ها", "هم", "ين", "ات", "ون"],
  "roots": [
    {
      "id": "عوش",
      "patterns": ["يعيش", "تعيش", "يعيشون", "عيش"]
    }
  ]
}
```

---

## 🖥️ Usage

### Input Parsing:
Ask the system a question using inflected or prefixed words, e.g.:
`"هل الأسد يعيش في السافانا؟"`
The morphological analyzer parses:
* `"الأسد"` $\to$ strips `"ال"` $\to$ `"أسد"` $\to$ maps to `"feline_carnivore"`.
* `"يعيش"` $\to$ maps to root `"عوش"` $\to$ maps to `"lives_in"`.
* `"السافانا"` $\to$ strips `"ال"` $\to$ `"سافانا"` $\to$ maps to `"savanna"`.

The engine translates the sentence into the semantic triple: `(feline_carnivore, lives_in, savanna)`.

### GUI Ingestion:
In the desktop GUI, when teaching facts or typing queries, the morphological analyzer runs on the backend server to resolve inputs dynamically in any of the supported languages.
