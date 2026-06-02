class ConversationManager:
    def __init__(self):
        self.history = []
        self.last_active_concept = None

    def record_turn(self, query, mapped_concepts, response=None):
        """Records a conversation turn with mapped concepts and generated response."""
        self.history.append({
            "query": query,
            "concepts": mapped_concepts,
            "response": response
        })
        
        # Determine the last active concept (preferring specific concepts over categories)
        # Note: In the MVP, we tend to prefer feline_carnivore or polar_bear
        for c in mapped_concepts:
            if c in ["feline_carnivore", "polar_bear"]:
                self.last_active_concept = c
                break
        else:
            if mapped_concepts:
                self.last_active_concept = mapped_concepts[0]

    def get_last_concept(self):
        return self.last_active_concept

    def clear(self):
        self.history = []
        self.last_active_concept = None
