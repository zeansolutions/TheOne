class ConflictResolver:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def resolve_conflict(self, concept_id, relation_type):
        """
        Checks if there are contradicting facts for a concept and relation in different worlds.
        E.g. lives_in savanna in reality vs lives_in arctic in khayali.
        """
        conflicts = []
        if not self.handler.graph.has_node(concept_id):
            return conflicts

        # Get edges of type 'fact' or 'relation' from this concept
        edges = []
        for u, v, data in self.handler.graph.out_edges(concept_id, data=True):
            if data.get("relation") == relation_type:
                edges.append((u, v, data))

        # Group by world
        world_targets = {}
        for u, v, data in edges:
            world = data.get("world", "reality")
            world_targets.setdefault(world, []).append(v)

        # If there are multiple worlds with different targets, we have a conflict
        worlds = list(world_targets.keys())
        if len(worlds) > 1:
            for i in range(len(worlds)):
                for j in range(i+1, len(worlds)):
                    w1, w2 = worlds[i], worlds[j]
                    # Compare list contents (order independent)
                    if set(world_targets[w1]) != set(world_targets[w2]):
                        lbl_concept = self.handler.graph.nodes[concept_id].get("labels", [concept_id])[0]
                        lbl_w1 = ", ".join([self.handler.graph.nodes[x].get("labels", [x])[0] for x in world_targets[w1]])
                        lbl_w2 = ", ".join([self.handler.graph.nodes[x].get("labels", [x])[0] for x in world_targets[w2]])
                        
                        conflicts.append({
                            "concept": concept_id,
                            "relation": relation_type,
                            "worlds": (w1, w2),
                            "targets": (world_targets[w1], world_targets[w2]),
                            "description": f"تعارض في العوالم للمفهوم [{lbl_concept}]: في عالم '{w1}' هو [{lbl_w1}]، بينما في عالم '{w2}' هو [{lbl_w2}]"
                        })
        return conflicts
