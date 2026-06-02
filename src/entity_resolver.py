class EntityResolver:
    def __init__(self, conversation_manager, graph_handler):
        self.conversation_manager = conversation_manager
        self.graph_handler = graph_handler

    def resolve(self, query, current_concepts):
        """
        Resolves implicit/pronominal references in Arabic (like 'عاش', 'بياكل', 'هناك', suffix 'ـه')
        to the last active concept in conversation history if no entity concept is in the current query.
        """
        # Check if current_concepts already contains a specific animal/entity
        has_subject = False
        for c in current_concepts:
            if self.graph_handler.graph.has_node(c):
                cat = self.graph_handler.graph.nodes[c].get("category", "")
                # If we have an animal or polar bear or feline carnivore, it's our subject
                if cat == "animal" or c in ["feline_carnivore", "polar_bear"]:
                    has_subject = True
                    break

        if has_subject:
            return current_concepts

        # Normalize words to look for implicit referential tags
        raw_words = query.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
        
        has_ref = False
        
        # 1. Pronouns
        ref_pronouns = ["هو", "هي", "عنه", "عنها", "فيه", "فيها", "هناك"]
        if any(p in words for p in ref_pronouns):
            has_ref = True
            
        # 2. Suffixes (word ending with ه/ها/هم)
        for w in words:
            if len(w) > 2 and (w.endswith("ه") or w.endswith("ها") or w.endswith("هم")):
                has_ref = True
                break
                
        # 3. Verb indicators starting query
        verbs = ["عاش", "يعيش", "بياكل", "يأكل", "يحتاج", "يتحمل", "تحمل"]
        for w in words:
            # Check prefix particles or direct verb
            for v in verbs:
                if w == v or w == f"ي{v}" or w.endswith(v):
                    has_ref = True
                    break
                    
        if has_ref:
            last_concept = self.conversation_manager.get_last_concept()
            if last_concept and last_concept not in current_concepts:
                # Insert at the beginning as the active subject
                current_concepts.insert(0, last_concept)
                
        return current_concepts
