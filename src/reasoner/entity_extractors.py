import os

class EntityExtractor:
    def __init__(self, reasoner):
        self.reasoner = reasoner

    @property
    def handler(self):
        return self.reasoner.handler

    @property
    def entity_resolver(self):
        return self.reasoner.entity_resolver

    def resolve_extracted_entity(self, val, language, context_concepts):
        if not val:
            return None
        val_clean = val.replace("؟", "").replace("?", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").strip()
        if language == "ar":
            # Strip prefixes from each word of a multiword entity
            words = val_clean.split()
            cleaned_words = []
            for w in words:
                cw = w
                for pref in ["ال", "وبال", "بال", "وال", "لل", "ب", "و", "ل", "ف"]:
                    if cw.startswith(pref) and len(cw) > len(pref):
                        cw = cw[len(pref):]
                        break
                cleaned_words.append(cw)
            val_clean = " ".join(cleaned_words)
        concept = self.handler.dynamic_morphological_lookup(val_clean, language=language, context_concepts=context_concepts)
        if concept:
            return concept
        norm_val = self.handler.normalize_text(val_clean, language)
        for node, data in self.handler.graph.nodes(data=True):
            if data.get("type") == "concept":
                if any(norm_val == self.handler.normalize_text(lbl, language) for lbl in data.get("labels", [])) or norm_val == self.handler.normalize_text(node, language):
                    return node
        return None

    def resolve_concept(self, val, language, context_concepts, trace=None):
        concept = self.resolve_extracted_entity(val, language, context_concepts)
        resolved = self.entity_resolver.resolve(val, [concept] if concept else [])
        c = resolved[0] if resolved else concept
        
        # If not resolved locally, trigger the on-demand importer!
        if not c and val and not val.startswith("?"):
            if getattr(self.handler, "online_import_enabled", True):
                from src.tools.data_importer import DataImporter
                importer = DataImporter(self.handler)
                if importer.enrich_concept(val, language, trace=trace):
                    # Re-try resolution now that it has been imported
                    concept = self.resolve_extracted_entity(val, language, context_concepts)
                    resolved = self.entity_resolver.resolve(val, [concept] if concept else [])
                    c = resolved[0] if resolved else concept
        return c

    def get_concept_index(self, c, words, language, part=None):
        """Finds the word index of a concept in the query string/words list."""
        # 1. Try finding a word in 'words' that resolves to 'c'
        for w_idx, w in enumerate(words):
            if self.handler.dynamic_morphological_lookup(w, language=language) == c:
                return w_idx
        # 2. Try finding if any label of c is a substring of the query
        c_labels = []
        if self.handler and c in self.handler.graph:
            c_labels = self.handler.graph.nodes[c].get("labels", [])
        c_labels = list(c_labels) + [c]
        query_clean = part.replace("؟", "").replace("?", "").strip() if part else " ".join(words)
        for lbl in sorted(c_labels, key=len, reverse=True):
            lbl_clean = lbl.strip()
            if lbl_clean in query_clean:
                first_word = lbl_clean.split()[0]
                if language == "ar":
                    first_word = self.handler.canonicalize_concept(first_word, "ar")
                for w_idx, w in enumerate(words):
                    w_clean = self.handler.canonicalize_concept(w, language)
                    if w_clean == first_word or first_word in w_clean or w_clean in first_word:
                        return w_idx
        return 999
