import os
import json
from typing import Dict, List, Tuple, Set

class TransitiveChainingEngine:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        self.relations_metadata = {}
        self.load_metadata()

    def load_metadata(self):
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        metadata_path = os.path.join(project_dir, "data", "relations_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for rel in data.get("relations", []):
                    if rel.get("transitive"):
                        self.relations_metadata[rel["id"]] = rel.get("decay", 0.0)

    def apply_transitive_rules(self, active_world: str, max_depth: int = 3) -> List[Tuple[str, str, str, float, str]]:
        """
        Applies transitive chaining on the graph handler's graph for the active world.
        Finds paths like (A, rel, B) and (B, rel, C) for transitive relations and infers (A, rel, C)
        with decayed confidence.
        Returns a list of tuples: (start_node, relation, target_node, final_confidence, trace_reason)
        """
        inferred_triples = []
        graph = self.handler.graph

        for rel_id, decay in self.relations_metadata.items():
            # Build adjacency dict for this specific relation in this specific world
            adj = {}
            for u, v, d in graph.edges(data=True):
                edge_rel = d.get("relation")
                edge_world = d.get("world", "reality")
                edge_type = d.get("type", "relation")
                
                # Relations are global, facts/inferred have worlds
                if edge_rel == rel_id:
                    if edge_type == "relation" or edge_world == active_world:
                        conf = d.get("confidence", 1.0)
                        adj.setdefault(u, []).append((v, conf))

            # Run DFS for each starting node
            for start_node in adj:
                visited = {}
                # Record path trace to reconstruct the chain
                path_traces = {}
                self._dfs_transitive(start_node, adj, visited, 1.0, [], 0, max_depth, path_traces)

                for target_node, confidence in visited.items():
                    if target_node == start_node:
                        continue
                    
                    # Check if a direct relation already exists (of same relation type and in this world/global)
                    exists = False
                    for _, target, data in graph.out_edges(start_node, data=True):
                        if target == target_node and data.get("relation") == rel_id:
                            if data.get("type") == "relation" or (data.get("type") in ["fact", "inferred"] and data.get("world") == active_world):
                                exists = True
                                break
                    
                    if exists:
                        continue

                    # Final confidence calculation: path confidence * (1 - decay)^length
                    path_len = len(path_traces.get(target_node, []))
                    final_conf = confidence * ((1.0 - decay) ** max(1, path_len - 1))
                    
                    # Build trace details
                    trace_hops = path_traces.get(target_node, [])
                    sub_lbl = graph.nodes[start_node].get("labels", [start_node])[0]
                    obj_lbl = graph.nodes[target_node].get("labels", [target_node])[0]
                    
                    # Format human readable trace in Arabic
                    trace_desc_steps = []
                    for idx, (h_from, h_to) in enumerate(trace_hops):
                        f_lbl = graph.nodes[h_from].get("labels", [h_from])[0]
                        t_lbl = graph.nodes[h_to].get("labels", [h_to])[0]
                        trace_desc_steps.append(f"({f_lbl} --[{rel_id}]--> {t_lbl})")
                    
                    if rel_id == "is_a":
                        hops_lbls = []
                        for h_from, h_to in trace_hops:
                            f_lbl = graph.nodes[h_from].get("labels", [h_from])[0]
                            t_lbl = graph.nodes[h_to].get("labels", [h_to])[0]
                            hops_lbls.append(f"{f_lbl} هو {t_lbl}")
                        desc = f"{sub_lbl} هو {obj_lbl} (استنتاج بالتعدي التصنيفي: " + "، و ".join(hops_lbls) + ")"
                    else:
                        desc = f"استنتاج بالتعدي لعلاقة [{rel_id}]: " + " و ".join(trace_desc_steps) + f" -> ({sub_lbl} --[{rel_id}]--> {obj_lbl}) بمعدل ثقة {final_conf:.2f}"
                    
                    inferred_triples.append((start_node, rel_id, target_node, final_conf, desc))

        return inferred_triples

    def _dfs_transitive(self, current: str, adj: Dict[str, List[Tuple[str, float]]], visited: Dict[str, float], current_conf: float, current_path: List[Tuple[str, str]], depth: int, max_depth: int, path_traces: Dict[str, List[Tuple[str, str]]]):
        if depth >= max_depth:
            return
        for neighbor, edge_conf in adj.get(current, []):
            # Check for cycle
            if any(h_from == neighbor or h_to == neighbor for h_from, h_to in current_path):
                continue
                
            new_conf = current_conf * edge_conf
            new_path = current_path + [(current, neighbor)]
            
            if neighbor not in visited or new_conf > visited[neighbor]:
                visited[neighbor] = new_conf
                path_traces[neighbor] = new_path
                self._dfs_transitive(neighbor, adj, visited, new_conf, new_path, depth + 1, max_depth, path_traces)
