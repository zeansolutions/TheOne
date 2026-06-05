class EntityResolver:
    def __init__(self, conversation_manager, graph_handler):
        self.conversation_manager = conversation_manager
        self.graph_handler = graph_handler

    def resolve(self, query, current_concepts):
        """
        Resolves implicit/pronominal references in Arabic (like 'عاش', 'بياكل', 'هناك', suffix 'ـه')
        to the last active concept in conversation history if no entity concept is in the current query.
        """
        # Load resolver settings dynamically from language rules configuration
        resolver_settings = {}
        if self.graph_handler and hasattr(self.graph_handler, "language_rules") and self.graph_handler.language_rules:
            resolver_settings = self.graph_handler.language_rules.get("resolver_settings", {})
        
        subject_categories = resolver_settings.get("subject_categories", ["animal"])
        subject_concepts = resolver_settings.get("subject_concepts", ["feline_carnivore", "polar_bear"])
        ref_pronouns = resolver_settings.get("reference_pronouns", ["هو", "هي", "عنه", "عنها", "فيه", "فيها", "هناك"])
        implicit_verb_indicators = resolver_settings.get("implicit_verb_indicators", ["عاش", "يعيش", "بياكل", "يأكل", "يحتاج", "يتحمل", "تحمل"])
        question_words = resolver_settings.get("question_words", ["ما", "من", "ماذا"])
        pronouns_copula = resolver_settings.get("pronouns_copula", ["هو", "هي"])
        suffixes = resolver_settings.get("suffixes", ["ه", "ها", "هم"])

        # Check if current_concepts already contains a specific animal/entity or grammar concept
        has_subject = False
        for c in current_concepts:
            if self.graph_handler.graph.has_node(c):
                cat = self.graph_handler.graph.nodes[c].get("category", "")
                if cat in subject_categories or c in subject_concepts:
                    has_subject = True
                    break

        if has_subject:
            return current_concepts

        # Normalize words to look for implicit referential tags
        raw_words = query.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
        
        has_ref = False
        
        # 1. Pronouns (ignoring question copula matches like "ما هي" or "من هو")
        is_question_copula = False
        for idx, w in enumerate(words):
            if w in pronouns_copula and idx > 0 and words[idx - 1] in question_words:
                is_question_copula = True
                
        if any(p in words for p in ref_pronouns) and not is_question_copula:
            has_ref = True
            
        # 2. Suffixes (word ending with suffixes)
        for w in words:
            if len(w) > 2 and any(w.endswith(suff) for suff in suffixes):
                has_ref = True
                break
                
        # 3. Verb indicators starting query
        for w in words:
            # Check prefix particles or direct verb
            for v in implicit_verb_indicators:
                if w == v or w == f"ي{v}" or w.endswith(v):
                    has_ref = True
                    break
                    
        if has_ref:
            last_concept = self.conversation_manager.get_last_concept()
            if last_concept and last_concept not in current_concepts:
                # Insert at the beginning as the active subject
                current_concepts.insert(0, last_concept)
                
        return current_concepts
