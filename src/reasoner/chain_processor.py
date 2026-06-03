import os
import json

class ChainProcessor:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "causal_chains.json")
            
        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)
            
    def propagate_causal_chains(self, initial_state, graph_handler):
        """
        Traces multi-hop causal links from the initial state concept (e.g. hunger) 
        and propagates consequences based on causal rules and chains.
        """
        # Look for matching causal chains
        matched_chains = []
        
        for chain in self.db.get("causal_chains", []):
            first_step = chain["steps"][0]
            if first_step.get("event") == initial_state or first_step.get("agent") == initial_state:
                matched_chains.append(chain)
                
        # Also check causal rules
        inferred_events = []
        for rule in self.db.get("causal_rules", []):
            # Parse simple condition
            # For simplicity, if initial_state matches part of the rule condition
            cond_str = rule["condition"]
            if initial_state in cond_str:
                inferred_events.append({
                    "conclusion": rule["conclusion"],
                    "confidence": rule["confidence"]
                })
                
        return {
            "initial_state": initial_state,
            "matched_chains": matched_chains,
            "inferred_events": inferred_events
        }
