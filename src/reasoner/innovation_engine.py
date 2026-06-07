import os
import json
import networkx as nx
from typing import Dict, List, Any, Optional

class InnovationEngine:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def get_decompositions(self, concept_id: str, world: str) -> Dict[str, List[str]]:
        """Extracts properties, capabilities, and requirements of a concept."""
        properties = []
        capabilities = []
        requirements = []

        if not self.handler.graph.has_node(concept_id):
            return {"properties": [], "capabilities": [], "requirements": []}

        # Query outgoing edges
        for _, to_node, data in self.handler.graph.out_edges(concept_id, data=True):
            rel = data.get("relation")
            edge_type = data.get("type", "relation")
            edge_world = data.get("world", "reality")
            
            # Filter by world if it's a fact/inferred edge
            if edge_type in ["fact", "inferred"] and edge_world != world:
                continue

            if rel in ["has_property", "hasproperty"]:
                properties.append(to_node)
            elif rel in ["capable_of", "capableof", "provides", "produces", "has_behavior", "has_capability"]:
                capabilities.append(to_node)
            elif rel in ["requires", "needs", "has_requirement"]:
                requirements.append(to_node)

        return {
            "properties": list(set(properties)),
            "capabilities": list(set(capabilities)),
            "requirements": list(set(requirements))
        }

    def _find_numerical_value(self, concept_id: str, key: str, world: str) -> Optional[float]:
        """Looks up a numerical value for a property in the graph."""
        if not self.handler.graph.has_node(concept_id):
            return None
        
        # Check node attributes first
        node_data = self.handler.graph.nodes[concept_id]
        if key in node_data:
            try:
                return float(node_data[key])
            except (ValueError, TypeError):
                pass

        # Check connected edges for patterns like "key_value" (e.g. mass_0.5)
        for _, to_node, data in self.handler.graph.out_edges(concept_id, data=True):
            edge_type = data.get("type", "relation")
            edge_world = data.get("world", "reality")
            if edge_type in ["fact", "inferred"] and edge_world != world:
                continue
            
            if isinstance(to_node, str):
                if to_node.startswith(f"{key}_"):
                    try:
                        val_str = to_node[len(key) + 1:]
                        return float(val_str)
                    except (ValueError, TypeError):
                        pass
        return None

    def validate_physics_constraints(self, source: str, target: str, world: str) -> Dict[str, Any]:
        """Reality-Script: Validates thermodynamic heat transfer (Q = m * c * delta_T) if Heat/Solar is involved."""
        # Check if Heat/Solar is involved
        heat_terms = ["heat", "حرارة", "solar_energy", "طاقة_شمسية", "solar", "طاقة شمسية"]
        source_lbl = self.handler.graph.nodes[source].get("labels", [source])[0] if source in self.handler.graph else source
        target_lbl = self.handler.graph.nodes[target].get("labels", [target])[0] if target in self.handler.graph else target
        
        is_heat_related = (
            any(t in source.lower() or t in source_lbl.lower() for t in heat_terms) or
            any(t in target.lower() or t in target_lbl.lower() for t in heat_terms)
        )
        
        if not is_heat_related:
            return {"status": "validated", "message_ar": "تم التحقق منطقياً بنجاح.", "message_en": "Logically validated successfully."}

        # Try to resolve values
        m = self._find_numerical_value(target, "mass", world)
        c = self._find_numerical_value(target, "specific_heat", world)
        dT = self._find_numerical_value(target, "temp_change", world)
        Q_prov = self._find_numerical_value(source, "energy_provided", world)

        missing = []
        if m is None: missing.append("mass (الكتلة)")
        if c is None: missing.append("specific_heat (الحرارة النوعية)")
        if dT is None: missing.append("temp_change (فرق درجة الحرارة)")
        if Q_prov is None: missing.append("energy_provided (الطاقة المتوفرة)")

        if missing:
            missing_str = ", ".join(missing)
            return {
                "status": "incomplete_validation",
                "missing": missing,
                "message_ar": f"التحقق الفيزيائي غير مكتمل (الاستقصاء الموجه): يرجى تحديد قيم للخصائص الفيزيائية ({missing_str}) لكيانات الابتكار.",
                "message_en": f"Physical validation incomplete: please define values for ({missing_str}) in the innovation entities."
            }

        # Calculate Q required: Q = m * c * dT
        Q_req = m * c * dT
        if Q_prov >= Q_req:
            return {
                "status": "validated",
                "message_ar": f"تم التحقق فيزيائياً (Reality-Script): الطاقة المتوفرة ({Q_prov:.1f} جول) كافية لتسخين الهدف (المطلوب {Q_req:.1f} جول).",
                "message_en": f"Physically validated (Reality-Script): energy provided ({Q_prov:.1f} J) is sufficient to heat target (required {Q_req:.1f} J)."
            }
        else:
            return {
                "status": "failed",
                "message_ar": f"فشل التحقق الفيزيائي (Reality-Script): الطاقة المتوفرة ({Q_prov:.1f} جول) غير كافية لتسخين الهدف (المطلوب {Q_req:.1f} جول).",
                "message_en": f"Physical validation failed (Reality-Script): energy provided ({Q_prov:.1f} J) is insufficient to heat target (required {Q_req:.1f} J)."
            }

    def innovate(self, c1: str, c2: str, world: str, language: str = "ar") -> Dict[str, Any]:
        """Performs Cartesian product matching of capabilities and requirements, and runs validation."""
        c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
        c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2

        dec1 = self.get_decompositions(c1, world)
        dec2 = self.get_decompositions(c2, world)

        # 1. Match c1.capabilities with c2.requirements
        matches = []
        for cap in dec1["capabilities"]:
            for req in dec2["requirements"]:
                if cap == req:
                    # Direct match
                    matches.append((cap, "direct", [cap]))
                else:
                    # Search for path between cap and req
                    try:
                        active_undirected = nx.Graph()
                        for node in self.handler.graph.nodes():
                            if node not in ["user_defined", "concept", "category", "unknown"]:
                                active_undirected.add_node(node)
                        for u, v, data in self.handler.graph.edges(data=True):
                            edge_type = data.get("type", "relation")
                            edge_world = data.get("world", "reality")
                            if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                                if u in active_undirected and v in active_undirected:
                                    active_undirected.add_edge(u, v)
                        
                        path = nx.shortest_path(active_undirected, source=cap, target=req)
                        matches.append((cap, "indirect", path))
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        pass

        # 2. Match c2.capabilities with c1.requirements
        for cap in dec2["capabilities"]:
            for req in dec1["requirements"]:
                if cap == req:
                    matches.append((cap, "direct", [cap]))
                else:
                    try:
                        active_undirected = nx.Graph()
                        for node in self.handler.graph.nodes():
                            if node not in ["user_defined", "concept", "category", "unknown"]:
                                active_undirected.add_node(node)
                        for u, v, data in self.handler.graph.edges(data=True):
                            edge_type = data.get("type", "relation")
                            edge_world = data.get("world", "reality")
                            if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                                if u in active_undirected and v in active_undirected:
                                    active_undirected.add_edge(u, v)
                        
                        path = nx.shortest_path(active_undirected, source=cap, target=req)
                        matches.append((cap, "indirect", path))
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        pass

        if not matches:
            return {
                "success": False,
                "message": "No generative path found to connect these two concepts.",
                "concept1_label": c1_lbl,
                "concept2_label": c2_lbl
            }

        # Choose the best match (direct first, or shortest path)
        matches.sort(key=lambda x: (0 if x[1] == "direct" else 1, len(x[2])))
        best_match = matches[0]
        matching_prop = best_match[0]
        match_type = best_match[1]
        path_nodes = best_match[2]

        # Translate path nodes labels
        path_labels = []
        for node in path_nodes:
            lbl = self.handler.graph.nodes[node].get("labels", [node])[0] if node in self.handler.graph else node
            path_labels.append(lbl)
            
        path_str = " -> ".join(path_labels)

        # Run physical validation (Reality-Script)
        validation = self.validate_physics_constraints(c1, c2, world)

        return {
            "success": True,
            "concept1": c1,
            "concept1_label": c1_lbl,
            "concept2": c2,
            "concept2_label": c2_lbl,
            "matching_property": matching_prop,
            "matching_property_label": self.handler.graph.nodes[matching_prop].get("labels", [matching_prop])[0] if matching_prop in self.handler.graph else matching_prop,
            "match_type": match_type,
            "path_str": path_str,
            "validation_status": validation["status"],
            "validation_message": validation["message_ar"] if language == "ar" else validation["message_en"]
        }
