from typing import Dict, Any, List

class CuriosityEngine:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        self.templates = {
            "ar": {
                "taxonomy": "ما هو '{concept}' بالضبط؟ هل هو نوع من الفئات الأخرى؟ (مثال: {concept} هو نوع من الثدييات)",
                "property": "ما هي صفات '{concept}'؟ كيف يبدو لونه أو شكله أو ملمسه؟",
                "action": "ما هي سلوكيات أو أفعال '{concept}'؟ ماذا يفعل أو يسبّب في العادة؟"
            },
            "en": {
                "taxonomy": "What exactly is '{concept}'? What is it a type of? (Example: {concept} is a type of Mammal)",
                "property": "What are the properties of '{concept}'? How does it look, feel, or weigh?",
                "action": "What are the behaviors or actions of '{concept}'? What does it usually do or cause?"
            },
            "fr": {
                "taxonomy": "Qu'est-ce que '{concept}' exactement? De quel type s'agit-il? (Exemple: {concept} est un type de Mammifère)",
                "property": "Quelles sont les propriétés de '{concept}'? À quoi ressemble-t-il, quelle est sa texture ou sa couleur?",
                "action": "Quels sont les comportements ou les actions de '{concept}'? Que fait-il ou cause-t-il généralement?"
            }
        }

    def get_taxonomic_depth(self, node: str) -> int:
        graph = self.handler.graph
        depth = 0
        queue = [(node, 0)]
        visited = set()
        while queue:
            curr, d = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            depth = max(depth, d)
            for _, to_node, data in graph.out_edges(curr, data=True):
                if data.get("relation") == "is_a":
                    queue.append((to_node, d + 1))
        return depth

    def count_properties(self, node: str) -> int:
        graph = self.handler.graph
        count = 0
        for _, to_node, data in graph.out_edges(node, data=True):
            if data.get("type") in ["fact", "relation"] and data.get("relation") not in ["is_a", "مرادف_لـ"]:
                count += 1
        return count

    def count_actions(self, node: str) -> int:
        graph = self.handler.graph
        count = 0
        action_relations = {"causes", "requires", "provides", "rises_from", "يفعل", "يسبب", "يؤدي_إلى", "ينتج_عنه", "يقوم_بـ"}
        for _, to_node, data in graph.out_edges(node, data=True):
            if data.get("relation") in action_relations:
                count += 1
        return count

    def calculate_mystery_score(self, concept: str) -> float:
        """
        Calculates mystery score of a concept from 0 to 100.
        """
        graph = self.handler.graph
        if not graph.has_node(concept):
            return 100.0

        depth = self.get_taxonomic_depth(concept)
        props = self.count_properties(concept)
        actions = self.count_actions(concept)
        degree = graph.degree(concept)

        t_term = 0.3 * (1.0 - depth / 10.0)
        p_term = 0.3 * (1.0 - props / 20.0)
        a_term = 0.2 * (1.0 - actions / 10.0)
        d_term = 0.2 * (1.0 - degree / 50.0)

        # Clip terms to >= 0
        t_term = max(0.0, t_term)
        p_term = max(0.0, p_term)
        a_term = max(0.0, a_term)
        d_term = max(0.0, d_term)

        score = 100.0 * (t_term + p_term + a_term + d_term)
        return max(0.0, min(100.0, score))

    def find_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Scans ontology and returns concepts with mystery scores > 30.
        """
        graph = self.handler.graph
        gaps = []
        
        for node in graph.nodes():
            data = graph.nodes[node]
            if data.get("type") != "concept":
                continue
            # Skip metadata/internal structures
            if str(node).startswith("ST_") or str(node).startswith("event_"):
                continue
                
            score = self.calculate_mystery_score(node)
            if score > 30.0:
                has_taxonomy = any(d.get("relation") == "is_a" for _, to_n, d in graph.out_edges(node, data=True))
                props_count = self.count_properties(node)
                actions_count = self.count_actions(node)
                
                gaps.append({
                    "concept": node,
                    "mystery_score": score,
                    "missing_taxonomy": not has_taxonomy,
                    "missing_properties": props_count < 2,
                    "missing_actions": actions_count < 1
                })
                
        gaps.sort(key=lambda x: x["mystery_score"], reverse=True)
        return gaps

    def generate_questions(self, limit: int = 5, lang: str = "ar") -> List[Dict[str, Any]]:
        gaps = self.find_knowledge_gaps()
        questions = []
        
        t = self.templates.get(lang, self.templates["en"])
        
        for gap in gaps[:limit]:
            concept = gap["concept"]
            # Get label
            label = self.handler.graph.nodes[concept].get("labels", [concept])[0]
            score = gap["mystery_score"]
            
            if gap["missing_taxonomy"]:
                questions.append({
                    "concept": concept,
                    "type": "taxonomy",
                    "mystery_score": score,
                    "question": t["taxonomy"].format(concept=label)
                })
            elif gap["missing_properties"]:
                questions.append({
                    "concept": concept,
                    "type": "property",
                    "mystery_score": score,
                    "question": t["property"].format(concept=label)
                })
            else:
                questions.append({
                    "concept": concept,
                    "type": "action",
                    "mystery_score": score,
                    "question": t["action"].format(concept=label)
                })
        return questions
