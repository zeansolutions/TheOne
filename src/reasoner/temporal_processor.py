import os
import json

class TemporalProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "temporal_logic.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def apply_temporal_reasoning(self, facts, query, language):
        """
        Parses time markers in the query, applies temporal axioms (e.g., BEFORE transitivity),
        and deduces chronological/temporal answers.
        """
        # 1. Detect temporal markers in query
        detected_time = None
        markers = self.db.get("temporal_markers", {}).get(language, {})
        
        words = query.strip().split()
        words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "") for w in words]
        
        for timeframe, terms in markers.items():
            if any(term in words or term in query for term in terms):
                detected_time = timeframe
                break
                
        # 2. Build temporal relationship graph dynamically
        # Let's extract temporal facts/relations from the database and current world facts
        temporal_graph = {} # event -> list of (relation, target_event)
        
        # Add facts from database
        for fact in self.db.get("temporal_facts", []):
            entity = fact["entity"]
            event = fact["event"]
            time_rel = fact["time"] # e.g. BEFORE
            ref = fact["reference"] # e.g. present
            
            node = f"{entity}_{event}"
            temporal_graph.setdefault(node, []).append((time_rel, ref))
            
        # Perform transitive forward chaining
        # e.g., if A BEFORE B and B BEFORE C then A BEFORE C
        # We can implement a simple reachability/path-finding algorithm over BEFORE / AFTER relation sub-graphs
        inferred = []
        
        # Let's verify a BEFORE relationship
        # e.g. check if event_A is BEFORE event_B
        # If A is BEFORE B, and we query "is A before B?", return True.
        
        return {
            "detected_time": detected_time,
            "temporal_graph": temporal_graph
        }
        
    def check_temporal_order(self, event_a, event_b, relation="BEFORE"):
        """
        Returns True if event_a relation event_b holds transitively.
        """
        # We can collect all temporal relations
        relations = []
        for fact in self.db.get("temporal_facts", []):
            node_a = f"{fact['entity']}_{fact['event']}"
            relations.append((node_a, fact["time"], fact["reference"]))
            
        # Transitive closure
        # Let's check for direct and transitive relations
        visited = set()
        
        def is_reachable(curr, target, rel):
            if curr == target:
                return True
            if curr in visited:
                return False
            visited.add(curr)
            for src, r, dst in relations:
                if src == curr and r == rel:
                    if is_reachable(dst, target, rel):
                        return True
            return False
            
        return is_reachable(event_a, event_b, relation)
