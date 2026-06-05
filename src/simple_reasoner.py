import os
import json
import networkx as nx
from src.world_manager import WorldManager
from src.conflict_resolver import ConflictResolver
from src.conversation_manager import ConversationManager
from src.entity_resolver import EntityResolver
from src.manager.language_selection_engine import LanguageSelectionEngine

# Import 10 Advanced Cognitive Reasoning Processors
from src.reasoner.semantic_processor import SemanticProcessor
from src.reasoner.temporal_processor import TemporalProcessor
from src.reasoner.modality_processor import ModalityProcessor
from src.reasoner.chain_processor import ChainProcessor
from src.reasoner.quantifier_processor import QuantifierProcessor
from src.reasoner.negation_processor import NegationProcessor
from src.reasoner.entailment_processor import EntailmentProcessor
from src.reasoner.pragmatic_processor import PragmaticProcessor
from src.reasoner.comparison_processor import ComparisonProcessor
from src.reasoner.anomaly_processor import AnomalyProcessor

class SimpleReasoner:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        self.conversation_manager = ConversationManager()
        self.entity_resolver = EntityResolver(self.conversation_manager, self.handler)
        self.world_manager = WorldManager(self.handler)
        self.conflict_resolver = ConflictResolver(self.handler)
        
        # Instantiate the 10 Cognitive Processors
        self.semantic_processor = SemanticProcessor()
        self.temporal_processor = TemporalProcessor()
        self.modality_processor = ModalityProcessor()
        self.chain_processor = ChainProcessor()
        self.quantifier_processor = QuantifierProcessor()
        self.negation_processor = NegationProcessor()
        self.entailment_processor = EntailmentProcessor()
        self.pragmatic_processor = PragmaticProcessor()
        self.comparison_processor = ComparisonProcessor()
        self.anomaly_processor = AnomalyProcessor()
        
        # Load language engine
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        languages_path = os.path.join(project_dir, "config", "languages.json")
        if not os.path.exists(languages_path):
            languages_path = "config/languages.json"
        
        self.language_engine = None
        if os.path.exists(languages_path):
            self.language_engine = LanguageSelectionEngine(languages_path)

    def _get_concept_index(self, c, words, language, part=None):
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

    def check_is_a_relationship(self, concept_id, target_category_id):
        """Checks if concept_id is a target_category_id directly or via transitive inheritance."""
        self.handler.infer_facts(self.handler.active_world)
        trace = []
        path = [concept_id, target_category_id]
        
        # Check direct or inferred edge
        for _, to_node, data in self.handler.graph.out_edges(concept_id, data=True):
            if data.get("relation") == "is_a" and to_node == target_category_id:
                reason = data.get("reason")
                if reason:
                    trace.append(reason)
                else:
                    # Translate labels to Arabic for trace readability
                    sub_lbl = self.handler.graph.nodes[concept_id].get("labels", [concept_id])[0]
                    obj_lbl = self.handler.graph.nodes[target_category_id].get("labels", [target_category_id])[0]
                    trace.append(f"{sub_lbl} هو تصنيف فرعي من {obj_lbl} (علاقة is_a)")
                return {
                    "result": True,
                    "path": path,
                    "trace": trace
                }
        return {
            "result": False,
            "path": path,
            "trace": trace
        }

    def inheritance_deduction(self, entity_id, property_id):
        """
        Deduces if an entity inherits a property from any of its taxonomic parent categories.
        """
        self.handler.infer_facts(self.handler.active_world)
        trace = []
        for _, to_node, data in self.handler.graph.out_edges(entity_id, data=True):
            if data.get("relation") == "has_property" and to_node == property_id:
                reason = data.get("reason")
                if reason:
                    trace.append(reason)
                else:
                    sub_lbl = self.handler.graph.nodes[entity_id].get("labels", [entity_id])[0]
                    obj_lbl = self.handler.graph.nodes[property_id].get("labels", [property_id])[0]
                    trace.append(f"{sub_lbl} لديه الخاصية [{obj_lbl}] بشكل مباشر")
                return {
                    "result": True,
                    "source": entity_id,
                    "trace": trace
                }
        return {"result": False, "trace": trace}

    def causal_reasoning(self, entity_id, environment_id):
        """
        Causal/Teleological reasoning.
        Identifies requirements of the environment, matches them against the entity's current properties,
        and determines what adaptation is needed based on functional causal purposes.
        """
        self.handler.infer_facts(self.handler.active_world)
        trace = []
        trace.append(f"بدء الاستدلال السببي للـ {entity_id} في البيئة {environment_id}")
        
        # 1. Look for inferred requirements of the entity (requires)
        entity_reqs = []
        for _, to_node, data in self.handler.graph.out_edges(entity_id, data=True):
            if data.get("relation") == "requires":
                entity_reqs.append((to_node, data.get("reason")))
                
        if not entity_reqs:
            # Fallback to base graph lookup
            base_reqs = self.handler.get_requirements(environment_id)
            if not base_reqs:
                trace.append(f"البيئة {environment_id} لا تفرض أي متطلبات خاصة مسجلة في قاعدة المعرفة")
                return {"needs_adaptation": False, "trace": trace}
            for req in base_reqs:
                entity_reqs.append((req["requirement"], f"البيئة {environment_id} بها {req['condition']} مما يستدعي متطلب: {req['requirement']}"))

        if not entity_reqs:
            return {"needs_adaptation": False, "trace": trace}
            
        sub_lbl = self.handler.graph.nodes[entity_id].get("labels", [entity_id])[0]
        properties = self.handler.get_properties(entity_id)
        
        # We check all requirements to see if any are unfulfilled
        unfulfilled_req = None
        unfulfilled_reason = ""
        current_property = None
        
        for req, reason in entity_reqs:
            # Check if any of the entity's properties provides this requirement
            fulfilled = False
            for p in properties:
                prop_node = p["property"]
                # Look at graph edges to see if this property provides the requirement
                if self.handler.graph.has_node(prop_node):
                    for _, to_node, edge_data in self.handler.graph.out_edges(prop_node, data=True):
                        if edge_data.get("relation") == "provides" and to_node == req:
                            fulfilled = True
                            current_property = prop_node
                            break
                if fulfilled:
                    break
            
            if not fulfilled:
                unfulfilled_req = req
                unfulfilled_reason = reason
                # Pick one of the entity's properties related to the category of the requirement if possible, or just the first property
                if properties:
                    current_property = properties[0]["property"]
                break
                
        if not unfulfilled_req:
            trace.append(f"جميع متطلبات الكائن {sub_lbl} مستوفاة بالخصائص الحالية")
            return {"needs_adaptation": False, "trace": trace}
            
        prop_lbl = self.handler.graph.nodes[current_property].get("labels", [current_property])[0] if current_property else "لا يوجد خصائص مسجلة"
        req_lbl = self.handler.graph.nodes[unfulfilled_req].get("labels", [unfulfilled_req])[0] if unfulfilled_req in self.handler.graph else unfulfilled_req
        
        trace.append(unfulfilled_reason)
        trace.append(f"الفحص الصرفي/الفيزيائي للـ {sub_lbl}: يمتلك [{prop_lbl}]")
        trace.append(f"الخاصية الحالية للـ {sub_lbl} ({prop_lbl}) لا توفر المتطلب المطلوب ({req_lbl})")
        trace.append(f"← النتيجة: {sub_lbl} بحاجة إلى {req_lbl} في {environment_id}")
        
        return {
            "needs_adaptation": True,
            "requirement": unfulfilled_req,
            "current_property": current_property,
            "trace": trace
        }

    def analogical_reasoning(self, target_entity_id, environment_id, requirement):
        """
        Analogical Transfer.
        Finds a similar entity (analogical candidate) that lives in environment_id and possesses
        a property solving the given requirement, and transfers that property to target_entity_id.
        """
        trace = []
        trace.append(f"بدء استدلال التناظر والقياس للـ {target_entity_id} في البيئة {environment_id}")
        
        # 1. Find entities living in this environment
        candidates = []
        for node, data in self.handler.graph.nodes(data=True):
            if data.get("type") == "concept" and node != target_entity_id:
                # Check if it lives in environment_id in reality or ontology
                properties = self.handler.get_properties(node, world="reality")
                for p in properties:
                    if p["relation"] == "lives_in" and p["property"] == environment_id:
                        candidates.append(node)
        candidates = list(set(candidates))
        trace.append(f"الكائنات البديلة التي تعيش في {environment_id}: {candidates}")
        
        # 2. Calculate similarity and find best match solving the requirement
        best_candidate = None
        best_similarity = 0.0
        solution_property = None
        
        for cand in candidates:
            sim = self.handler.calculate_similarity(target_entity_id, cand)
            trace.append(f"مقياس التشابه الجاكاردي (Ancestry Similarity) بين {target_entity_id} و {cand} هو {sim:.2f}")
            
            # Check properties of candidate to see if it solves requirement
            cand_props = self.handler.get_properties(cand, world="reality")
            for p in cand_props:
                prop = p["property"]
                # Does this property provide the requirement?
                for _, to_node, data in self.handler.graph.out_edges(prop, data=True):
                    if data.get("relation") == "provides" and to_node == requirement:
                        if sim > best_similarity:
                            best_similarity = sim
                            best_candidate = cand
                            solution_property = prop
                            
        if best_candidate and solution_property:
            trace.append(f"المرشح الأنسب للقياس هو: {best_candidate} (معدل تشابه: {best_similarity:.2f})")
            trace.append(f"نقوم بنقل الخاصية {solution_property} من {best_candidate} إلى {target_entity_id} لحل مشكلة البيئة")
            return {
                "success": True,
                "analogy_candidate": best_candidate,
                "transferred_property": solution_property,
                "similarity": best_similarity,
                "trace": trace
            }
            
        trace.append("لم نجد أي كائن مماثل يعيش في تلك البيئة ولديه الخاصية المطلوبة لقياسها")
        return {"success": False, "trace": trace}

    def detect_conditional_and_query(self, query: str, language: str) -> tuple:
        """
        Detects if query contains conditional particles (like لو, إذا, if, etc.).
        Returns (is_conditional, premise_text, question_text).
        """
        words = query.strip().split()
        cleaned_words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "") for w in words]
        
        conditionals = {
            "ar": ["لو", "إذا", "اذا", "افترض"],
            "en": ["if", "assume", "suppose"],
            "fr": ["si", "supposons", "suppose"]
        }
        
        lang_conds = conditionals.get(language, conditionals["ar"])
        is_conditional = any(c in cleaned_words for c in lang_conds) or any(c in query for c in ["لو كان", "إذا كان", "اذا كان"])
        
        if not is_conditional:
            return False, "", query
            
        import re
        parts = re.split(r'[،,;\?؟]', query)
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) >= 2:
            premise = parts[0]
            question = " ".join(parts[1:])
        else:
            premise = query
            question = query
            
        # Clean premise from conditional words
        for cond in lang_conds + ["كان", "افترضنا", "أن", "ان", "assumed", "we assume"]:
            premise = re.sub(rf'{cond}', '', premise).strip()
            
        return True, premise, question

    def process_query(self, query, interactive=False, language=None):
        """
        Wrapper that detects conditional thought experiments (sandbox)
        and executes query inside the sandbox or directly.
        """
        # Detect and set language if not provided
        if language is None:
            if self.language_engine:
                detected = self.language_engine.detect_language(query)
                language = self.language_engine.select_language(detected)
            else:
                language = "ar"

        # Check for conditional
        is_cond, premise, question = self.detect_conditional_and_query(query, language)
        
        if is_cond:
            from src.reasoner.sandbox_manager import SandboxManager
            sandbox = SandboxManager(self.handler)
            sandbox.enter_sandbox(premise)
            
            sandbox_trace = [
                f"[SANDBOX] دخول عالم الافتراض للسيناريو: '{premise}'",
                f"[SANDBOX] استنساخ الرسم البياني المعرفي بأكمله بشكل آمن"
            ]
            
            try:
                # Add the temporary fact to the sandbox graph
                teach_res = self.world_manager.parse_and_add_fact(premise, self.handler.active_world, interactive=False, language=language)
                if teach_res.get("success"):
                    sandbox_trace.append(f"[SANDBOX] إضافة حقيقة افتراضية مؤقتة: {teach_res.get('msg')}")
                else:
                    sandbox_trace.append(f"[SANDBOX] لم نتمكن من تلقين الفرضية الافتراضية بشكل كامل: {premise}")
                
                # Now run the reasoner pipeline on the original query
                res = self._process_query_internal(query, interactive, language)
                
                # Add sandbox trace to the result
                res["trace"] = sandbox_trace + [f"[SANDBOX] تشغيل الاستدلال الاستنتاجي التناظري..."] + res.get("trace", []) + [
                    f"[SANDBOX] الخروج من عالم الافتراض واستعادة الرسم البياني الأصلي بأمان"
                ]
                res["is_sandbox"] = True
                res["scenario"] = premise
                return res
            finally:
                sandbox.exit_sandbox()
        else:
            return self._process_query_internal(query, interactive, language)

    def _process_query_internal(self, query, interactive=False, language=None):
        """
        Pipeline: Parsing -> Dynamic Morphological Lookup -> Logical Reasoning.
        Supports 5 dynamic queries, multi-world state, dynamic fact teaching, and dialog context.
        Supports multilingual execution (ar, en, fr).
        """
        if language is None:
            if self.language_engine:
                detected = self.language_engine.detect_language(query)
                language = self.language_engine.select_language(detected)
            else:
                language = "ar"

        query, world = self.world_manager.detect_and_set_world(query)
        self.handler.infer_facts(world)
        
        normalized_query = query.replace("؟", "؟.").replace("?", "?.")
        parts = [p.strip() for p in normalized_query.split(".") if p.strip()]
        
        last_result = None
        
        for idx, part in enumerate(parts):
            raw_words = part.strip().split()
            words = []
            for w in raw_words:
                cleaned_w = w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "")
                if language == "ar":
                    if cleaned_w.startswith("وال") and len(cleaned_w) > 3:
                        cleaned_w = cleaned_w[1:]
                    elif cleaned_w.startswith("و") and len(cleaned_w) > 2:
                        stem = cleaned_w[1:]
                        is_known = False
                        ar_lex = self.handler.language_rules.get("ar", {}).get("lexicon", {})
                        if stem in ar_lex:
                            is_known = True
                        else:
                            for node, ndata in self.handler.graph.nodes(data=True):
                                if ndata.get("type") == "concept" and stem in ndata.get("labels", []):
                                    is_known = True
                                    break
                        if is_known:
                            cleaned_w = stem
                elif language in ["en", "fr"]:
                    cleaned_w = cleaned_w.lower()
                words.append(cleaned_w)
            
            lang_rules = self.handler.language_rules.get(language, {})
            question_particles = lang_rules.get("question_particles", [])
            if not question_particles:
                question_particles = self.handler.language_rules.get("grammar", {}).get("question_particles", [])
                
            is_question = any(q in words for q in question_particles) or \
                          part.endswith("؟") or part.endswith("?") or \
                          any(w in words for w in ["الفرق", "إزاي", "ازاي", "difference", "différence", "comment", "how"])
            
            if not is_question:
                teach_res = self.world_manager.parse_and_add_fact(part, world, interactive=interactive, language=language)
                last_result = {
                    "type": "teaching",
                    "result": teach_res["success"],
                    "message": teach_res["msg"],
                    "status": teach_res.get("status"),
                    "world": world,
                    "trace": [f"تحليل الجملة الخبرية وإدخالها في العالم النشط '{world}'"],
                    "confidence": 1.0
                }
                if idx == len(parts) - 1:
                    return last_result
            else:
                prag_trace = []
                pragmatic_res = self.pragmatic_processor.resolve_metaphor(part)
                if pragmatic_res:
                    metaphor = pragmatic_res["metaphor"]
                    literal = pragmatic_res["literal"]
                    literal_lbl = self.handler.graph.nodes[literal].get("labels", [literal])[0] if literal in self.handler.graph else literal
                    part = part.replace(metaphor, literal_lbl)
                    raw_words = part.strip().split()
                    words = [w.replace("؟", "").replace("!", "").replace("،", "").replace(",", "").replace(".", "").replace("?", "") for w in raw_words]
                    if language in ["en", "fr"]:
                        words = [w.lower() for w in words]
                    prag_trace.append(f"[PRAGMATICS] تم حل المجاز/الاستعارة '{metaphor}' إلى المعنى الحرفي '{literal_lbl}'")

                context_concepts = []
                for turn in self.conversation_manager.history[-3:]:
                    context_concepts.extend(turn.get("concepts", []))
                context_concepts = list(set(context_concepts))
                
                mapped_concepts = []
                
                # Phrase matching (both raw and prefix-stripped)
                for ngram_size in range(min(4, len(words)), 1, -1):
                    for i in range(len(words) - ngram_size + 1):
                        raw_phrase = " ".join(words[i:i + ngram_size])
                        
                        # Generate prefix-stripped version of the subphrase
                        cleaned_subwords = []
                        for w in words[i:i + ngram_size]:
                            cw = w
                            if language == "ar":
                                for pref in ["ال", "ل", "ب", "ف", "و"]:
                                    if cw.startswith(pref) and len(cw) > len(pref):
                                        cw = cw[len(pref):]
                                        break
                            cleaned_subwords.append(cw)
                        cleaned_phrase = " ".join(cleaned_subwords)
                        
                        # Match either raw or cleaned phrase
                        for phrase in [raw_phrase, cleaned_phrase]:
                            if not phrase:
                                continue
                            ar_lexicon = self.handler.language_rules.get(language, {}).get("lexicon", {})
                            if phrase in ar_lexicon:
                                concept = ar_lexicon[phrase]
                                if concept not in mapped_concepts:
                                    mapped_concepts.append(concept)
                                break
                            matched_label = False
                            for node, ndata in self.handler.graph.nodes(data=True):
                                if ndata.get("type") == "concept" and phrase in ndata.get("labels", []):
                                    if node not in mapped_concepts:
                                        mapped_concepts.append(node)
                                    matched_label = True
                            if matched_label:
                                break
                
                # Single word fallback
                for word in words:
                    if not word:
                        continue
                    concept = self.handler.dynamic_morphological_lookup(word, language=language, context_concepts=context_concepts)
                    if concept and concept not in mapped_concepts:
                        mapped_concepts.append(concept)
                        
                mapped_concepts = self.entity_resolver.resolve(part, mapped_concepts)
                self.conversation_manager.record_turn(part, mapped_concepts)
                
                # ROUTING WITH REFACTORED SUB-HANDLERS
                res = self._route_logical_reasoning(mapped_concepts, words, language, world, part, prag_trace)
                last_result = res
                
        return last_result

    def _is_wh_query(self, words):
        wh_words = {
            "why", "where", "how", "who", "what", "when", "which", "whose", "whom",
            "pourquoi", "où", "comment", "qui", "quand", "quel", "quelle", "quels", "quelles", "que", "quoi",
            "لماذا", "ليه", "أين", "كيف", "من", "ماذا", "ما", "متى", "أي"
        }
        return any(w.lower().strip("?,.!") in wh_words for w in words)

    def _is_classification_word_query(self, words, language):
        if language == "ar" and "هل" in words:
            return True
        if language == "fr" and "est-ce" in words:
            return True
        if self._is_wh_query(words):
            return False
        if language == "en" and any(w in words for w in ["does", "is", "did", "can", "has", "are"]):
            return True
        elif language == "fr" and any(w in words for w in ["est-ce", "est", "a-t-il", "peut-il", "a", "ont"]):
            return True
        return False

    def _route_logical_reasoning(self, mapped_concepts, words, language, world, part, prag_trace):
        """Routes logic parsing to distinct sub-handlers for high modularity."""
        # 1. Anomaly & Exception Detection (Level 10)
        res = self._handle_anomaly(mapped_concepts, words, prag_trace)
        if res: return res
        
        # 2. Comparison & Similarity Scales (Level 9)
        res = self._handle_comparison_scale(mapped_concepts, words, language, prag_trace)
        if res: return res
        
        # 3. Temporal Logic (Level 2)
        res = self._handle_temporal_logic(mapped_concepts, words, prag_trace)
        if res: return res
        
        # 4. Modality (Level 3)
        res = self._handle_modality(mapped_concepts, part, language, world, prag_trace)
        if res: return res
        
        # 5. Causal Chain (Level 4)
        res = self._handle_causal_chain(mapped_concepts, words, prag_trace)
        if res: return res
        
        # 6. Quantifier Rules (Level 5)
        res = self._handle_quantifiers(mapped_concepts, part, world, prag_trace)
        if res: return res
        
        # 7. Negation & Polarity Rules (Level 6)
        res = self._handle_negation(mapped_concepts, part, language, world, prag_trace)
        if res: return res
        
        # 8. Semantic Roles (Level 1)
        res = self._handle_semantic_roles(words, language, prag_trace)
        if res: return res
        
        # 9. Celestial
        res = self._handle_celestial(mapped_concepts, words, language, world, prag_trace)
        if res: return res
        
        # 10. Comparison
        res = self._handle_comparison_diff(mapped_concepts, words, world, prag_trace)
        if res: return res
        
        # 11. Hypothetical
        res = self._handle_hypothetical(mapped_concepts, words, prag_trace)
        if res: return res
        
        # 12. Location
        res = self._handle_location(mapped_concepts, words, world, prag_trace)
        if res: return res
        
        # 13. Causal Why
        res = self._handle_causal_why(mapped_concepts, words, world, part, prag_trace)
        if res: return res
        
        # Bypass classification/describe/knowledge fallback for causal questions
        is_why = any(w.lower().strip("?,.!") in ["لماذا", "ليه", "بسبب", "علل", "why", "because", "pourquoi", "cause"] for w in words)
        if is_why:
            return {
                "type": "unknown",
                "result": False,
                "trace": prag_trace + ["لم نجد مسار استدلالي منطقي أو تصنيفي واضح يربط بين الكلمات المدخلة في قاعدة المعرفة المتاحة"],
                "confidence": 0.0
            }
        
        # 14. Classification
        res = self._handle_classification(mapped_concepts, words, language, part, prag_trace)
        if res: return res
        
        # 15. Relation Path / Connection Search
        res = self._handle_relation_path(mapped_concepts, part, world, prag_trace, words)
        if res: return res
        
        # 16. Generic "What is X?"
        res = self._handle_describe(mapped_concepts, words, world, prag_trace)
        if res: return res
        
        # 17. Generic concept knowledge fallback
        res = self._handle_knowledge_fallback(mapped_concepts, world, prag_trace)
        if res: return res
        
        # Default unknown fail-safe
        return {
            "type": "unknown",
            "result": False,
            "trace": prag_trace + ["لم نجد مسار استدلالي منطقي أو تصنيفي واضح يربط بين الكلمات المدخلة في قاعدة المعرفة المتاحة"],
            "confidence": 0.0
        }

    # --- SUB-HANDLERS ---

    def _handle_anomaly(self, mapped_concepts, words, prag_trace):
        exceptions = self.anomaly_processor.db.get("exceptions", [])
        for ex in exceptions:
            ex_entity = ex.get("entity")
            ex_property = ex.get("property")
            if ex_entity in mapped_concepts:
                has_property_ref = False
                if ex_property in mapped_concepts:
                    has_property_ref = True
                else:
                    prop_labels = []
                    if self.handler.graph.has_node(ex_property):
                        prop_labels = self.handler.graph.nodes[ex_property].get("labels", [])
                    if any(w in prop_labels or w == ex_property for w in words):
                        has_property_ref = True
                    else:
                        prop_parts = ex_property.replace("_", " ").split()
                        translation_map = {
                            "vegetarian": ["نباتي", "نبات", "vegetarian", "نباتية"],
                            "meat": ["لحم", "لحوم", "meat"],
                            "cold": ["بارد", "برودة", "cold"]
                        }
                        for p_part in prop_parts:
                            if p_part in translation_map:
                                if any(t in words for t in translation_map[p_part]):
                                    has_property_ref = True
                                    break
                                    
                if has_property_ref:
                    anomaly_res = self.anomaly_processor.check_anomaly(ex_entity, "has_property", ex_property)
                    if anomaly_res:
                        entity_lbl = self.handler.graph.nodes[ex_entity].get("labels", [ex_entity])[0] if ex_entity in self.handler.graph else ex_entity
                        return {
                            "type": "anomaly",
                            "result": True,
                            "entity": ex_entity,
                            "anomaly_type": anomaly_res["anomaly_type"],
                            "anomaly_score": anomaly_res["anomaly_score"],
                            "reason": anomaly_res["reason"],
                            "typical_rule": anomaly_res["typical_rule"],
                            "trace": prag_trace + [f"كشف الشذوذ: البحث عن استثناءات للـ {entity_lbl}", f"العثور على استثناء: {anomaly_res['anomaly_type']}"],
                            "confidence": anomaly_res["anomaly_score"]
                        }
        return None

    def _handle_comparison_scale(self, mapped_concepts, words, language, prag_trace):
        comp_prop = None
        if any(w in words for w in ["أقوى", "stronger", "fort"]):
            comp_prop = "strength"
        elif any(w in words for w in ["أسرع", "faster", "rapide"]):
            comp_prop = "speed"
            
        if comp_prop and len(mapped_concepts) >= 2:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            try:
                idx1 = self._get_concept_index(c1, words, language, " ".join(words))
                idx2 = self._get_concept_index(c2, words, language, " ".join(words))
                if idx1 > idx2:
                    c1, c2 = c2, c1
            except Exception:
                pass
                
            comparison_val = self.comparison_processor.compare_entities(c1, c2, comp_prop)
            trace_msg = self.comparison_processor.get_comparison_rule_trace(c1, c2, comp_prop)
            
            return {
                "type": "comparison_scale",
                "result": comparison_val > 0,
                "entity1": c1,
                "entity2": c2,
                "property_name": comp_prop,
                "comparison_value": comparison_val,
                "trace": prag_trace + [f"مقارنة الكائنات على مقياس {comp_prop}", trace_msg],
                "confidence": 1.0
            }
        return None

    def _handle_temporal_logic(self, mapped_concepts, words, prag_trace):
        is_temporal = any(w in words for w in ["قبل", "بعد", "أثناء", "الماضي", "كان", "مستقبلا", "مستقبلاً", "الآن", "before", "after", "during", "past", "present", "future"])
        if is_temporal:
            event = None
            temporal_facts = self.temporal_processor.db.get("temporal_facts", [])
            for tf in temporal_facts:
                tf_entity = tf.get("entity")
                tf_event = tf.get("event")
                entity_match = False
                if tf_entity in mapped_concepts:
                    entity_match = True
                else:
                    labels = []
                    if self.handler.graph.has_node(tf_entity):
                        labels = self.handler.graph.nodes[tf_entity].get("labels", [])
                    if any(w in labels or w == tf_entity for w in words):
                        entity_match = True
                        
                if entity_match:
                    event_labels = [tf_event, "extinction", "انقراض", "shone", "قرار", "ضلال", "advice", "shone_brightly_for_child", "advice_from_old_star"]
                    if any(w in tf_event or tf_event in w or w in event_labels for w in words):
                        event = f"{tf_entity}_{tf_event}"
                        break
            
            if event:
                is_before = self.temporal_processor.check_temporal_order(event, "present", "BEFORE")
                rel_str = "قبل" if is_before else "ليس قبل"
                return {
                    "type": "temporal_logic",
                    "result": is_before,
                    "event": event,
                    "reference": "present",
                    "relation": "BEFORE",
                    "trace": prag_trace + [f"الاستدلال الزمني: التحقق من الترتيب الزمني للحدث {event}", f"الحدث {event} يقع {rel_str} present بالتعدي الزمني"],
                    "confidence": 1.0
                }
        return None

    def _handle_modality(self, mapped_concepts, part, language, world, prag_trace):
        modal_info = self.modality_processor.process_modality(part, language)
        if modal_info["modality"] != "certainty":
            c1 = mapped_concepts[0] if len(mapped_concepts) >= 1 else None
            c2 = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            if c1 and c2:
                res_check = self.check_is_a_relationship(c1, c2)
                if not res_check["result"]:
                    props = self.handler.get_properties(c1, world=world)
                    has_prop = any(p["property"] == c2 for p in props)
                    res_check = {"result": has_prop, "trace": [f"فحص الخاصية {c2} للـ {c1}"]}
                    
                if modal_info["modality"] == "impossibility":
                    result = not res_check["result"]
                elif modal_info["modality"] == "necessity":
                    result = res_check["result"]
                else:
                    result = res_check["result"] or modal_info["confidence"] > 0
                    
                return {
                    "type": "modality",
                    "result": result,
                    "modality": modal_info["modality"],
                    "modality_confidence": modal_info["confidence"],
                    "trace": prag_trace + res_check["trace"] + [f"الاستدلال الموجه بالجهة (Modality): الحالة المكتشفة هي '{modal_info['modality']}' وثقتها {modal_info['confidence']}"],
                    "confidence": modal_info["confidence"]
                }
        return None

    def _handle_causal_chain(self, mapped_concepts, words, prag_trace):
        is_chain_query = any(w in words for w in ["سلسلة", "أسباب", "يؤدي", "causes", "chain"])
        if is_chain_query and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            chain_res = self.chain_processor.propagate_causal_chains(concept, self.handler)
            matched = chain_res["matched_chains"]
            if matched:
                steps = matched[0]["steps"]
                trace = prag_trace + [f"الاستدلال السببي متعدد الخطوات (Causal Chain): بدءاً من {concept}"]
                for step in steps:
                    trace.append(f"الخطوة {step['step']}: الحدث {step['event']}")
                return {
                    "type": "causal_chain",
                    "result": True,
                    "initial_state": concept,
                    "chain": matched[0],
                    "trace": trace,
                    "confidence": matched[0]["total_confidence"]
                }
        return None

    def _handle_quantifiers(self, mapped_concepts, part, world, prag_trace):
        quantifier_info = self.quantifier_processor.detect_quantifier(part)
        if quantifier_info:
            c1 = mapped_concepts[0] if len(mapped_concepts) >= 1 else None
            c2 = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            if c1 and c2:
                res_check = self.check_is_a_relationship(c1, c2)
                if not res_check["result"]:
                    props = self.handler.get_properties(c1, world=world)
                    has_prop = any(p["property"] == c2 for p in props)
                    res_check = {"result": has_prop, "trace": [f"فحص الخاصية {c2} للـ {c1}"]}
                    
                statement_q = {"name": "universal", "confidence": 1.0}
                result = self.quantifier_processor.evaluate_quantifiers(statement_q, quantifier_info) and res_check["result"]
                
                return {
                    "type": "quantifier",
                    "result": result,
                    "quantifier": quantifier_info["name"],
                    "trace": prag_trace + res_check["trace"] + [f"الاستدلال بسور القضية (Quantifiers): السور المكتشف هو '{quantifier_info['name']}'"],
                    "confidence": quantifier_info["confidence"]
                }
        return None

    def _handle_negation(self, mapped_concepts, part, language, world, prag_trace):
        is_negated = self.negation_processor.has_negation(part, language)
        if is_negated:
            c1 = mapped_concepts[0] if len(mapped_concepts) >= 1 else None
            c2 = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            if c1 and c2:
                res_check = self.check_is_a_relationship(c1, c2)
                if not res_check["result"]:
                    props = self.handler.get_properties(c1, world=world)
                    has_prop = any(p["property"] == c2 for p in props)
                    res_check = {"result": has_prop, "trace": [f"فحص الخاصية {c2} للـ {c1}"]}
                    
                return {
                    "type": "negation",
                    "result": not res_check["result"],
                    "trace": prag_trace + res_check["trace"] + [f"الاستدلال بالنفي والتقابل (Negation): تم تطبيق قاعدة نفي النفي وعكس القطبية"],
                    "confidence": 1.0
                }
        return None

    def _handle_semantic_roles(self, words, language, prag_trace):
        is_roles_query = any(w in words for w in ["من", "ماذا", "أين", "من الذي", "who", "what", "where"]) and \
                         any(w in words or any(r["id"] in ["فرس", "عوش"] for r in self.handler.language_rules.get("morphology", {}).get("roots", []) if w in r["patterns"]) for w in words)
        if is_roles_query:
            roles_res = self.semantic_processor.extract_semantic_roles(words, language, self.handler)
            if roles_res:
                return {
                    "type": "semantic_roles",
                    "result": True,
                    "predicate": roles_res["predicate"],
                    "roles": roles_res["roles"],
                    "trace": prag_trace + [f"تحليل الأدوار الدلالية (Semantic Roles): استخلاص أدوار الفعل '{roles_res['predicate']}'"],
                    "confidence": 1.0
                }
        return None

    def _handle_celestial(self, mapped_concepts, words, language, world, prag_trace):
        if "c_sun" in mapped_concepts:
            props = self.handler.get_properties("c_sun", world=world)
            target = None
            for p in props:
                if p["relation"] == "rises_from":
                    target = p["property"]
                    break
                    
            conflicts = self.conflict_resolver.resolve_conflict("c_sun", "rises_from")
            conflict_trace = [c["description"] for c in conflicts]
            
            is_classification_query = self._is_classification_word_query(words, language)
                
            if is_classification_query:
                dir_concept = None
                for c in mapped_concepts:
                    if c in ["c_east", "c_west"]:
                        dir_concept = c
                        break
                if dir_concept and target:
                    is_correct = (target == dir_concept)
                    return {
                        "type": "classification",
                        "result": is_correct,
                        "concept1": "c_sun",
                        "concept2": dir_concept,
                        "trace": prag_trace + [f"الاستعلام عن شروق الشمس في العالم النشط '{world}'", f"الشمس تشرق من {target} في هذا العالم"] + conflict_trace,
                        "confidence": 1.0
                    }
                    
            if target:
                target_lbl = self.handler.graph.nodes[target].get("labels", [target])[0]
                return {
                    "type": "location",
                    "result": True,
                    "concept": "c_sun",
                    "location": target,
                    "location_label": target_lbl,
                    "trace": prag_trace + [f"الاستعلام عن شروق الشمس في العالم النشط '{world}'", f"الشمس تشرق من {target_lbl} في هذا العالم"] + conflict_trace,
                    "confidence": 1.0
                }
        return None

    def _handle_comparison_diff(self, mapped_concepts, words, world, prag_trace):
        if ("الفرق" in words or "difference" in words or "différence" in words or "differance" in words) and len(mapped_concepts) >= 2:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            props1 = self.handler.get_properties(c1, world=world)
            props2 = self.handler.get_properties(c2, world=world)
            return {
                "type": "comparison",
                "result": True,
                "concept1": c1,
                "concept2": c2,
                "props1": props1,
                "props2": props2,
                "trace": prag_trace + [f"مقارنة الخصائص للـ {c1} والـ {c2} في العالم النشط '{world}'"],
                "confidence": 1.0
            }
        return None

    def _handle_hypothetical(self, mapped_concepts, words, prag_trace):
        if ("لو" in words or "إذا" in words or "اذا" in words or "if" in words or "si" in words) and len(mapped_concepts) >= 2:
            entity = None
            env = None
            for c in mapped_concepts:
                cat = self.handler.graph.nodes[c].get("category", "") if c in self.handler.graph else ""
                if c == "feline_carnivore" or cat == "animal":
                    entity = c
                elif c == "arctic" or cat == "environment":
                    env = c
                    
            if entity and env:
                causal_res = self.causal_reasoning(entity, env)
                trace = list(causal_res["trace"])
                
                if causal_res.get("needs_adaptation"):
                    req = causal_res["requirement"]
                    analogy_res = self.analogical_reasoning(entity, env, req)
                    trace.extend(analogy_res["trace"])
                    
                    if analogy_res.get("success"):
                        return {
                            "type": "hypothetical",
                            "result": True,
                            "entity": entity,
                            "environment": env,
                            "needs_adaptation": True,
                            "transferred_property": analogy_res["transferred_property"],
                            "analogy_candidate": analogy_res["analogy_candidate"],
                            "trace": prag_trace + trace,
                            "confidence": analogy_res["similarity"]
                        }
                return {
                    "type": "hypothetical",
                    "result": False,
                    "entity": entity,
                    "environment": env,
                    "needs_adaptation": False,
                    "trace": prag_trace + trace,
                    "confidence": 1.0
                }
        return None

    def _handle_location(self, mapped_concepts, words, world, prag_trace):
        loc_settings = self.handler.language_rules.get("location_query_settings", {})
        loc_particles = loc_settings.get("question_particles", ["أين", "اين", "where", "où", "ou"])
        loc_verbs = loc_settings.get("verbs", ["يعيش", "عاش", "يسكن", "live", "lives", "vit", "vivent", "located"])
        
        is_location_query = any(w in words for w in loc_particles + loc_verbs)
        
        if is_location_query and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            props = self.handler.get_properties(concept, world=world)
            location = None
            relation_used = "lives_in"
            
            for p in props:
                rel = p.get("relation")
                prop_node = p.get("property")
                prop_data = self.handler.graph.nodes.get(prop_node, {}) if self.handler.graph.has_node(prop_node) else {}
                if rel in ["lives_in", "located_in"] or prop_data.get("category") == "location":
                    location = prop_node
                    relation_used = rel
                    break
                    
            if location:
                loc_label = self.handler.graph.nodes[location].get("labels", [location])[0] if location in self.handler.graph else location
                conflicts = self.conflict_resolver.resolve_conflict(concept, relation_used)
                conflict_trace = [c["description"] for c in conflicts]
                
                # Dynamic translation of relation verb in trace
                rel_label = relation_used
                for lang in ["ar", "en", "fr"]:
                    lang_rels = self.handler.language_rules.get(lang, {}).get("relations", {})
                    for k, v in lang_rels.items():
                        if v == relation_used:
                            rel_label = k
                            break
                    if rel_label != relation_used:
                        break
                
                if "ar" in self.handler.language_rules and any(v == relation_used for v in self.handler.language_rules.get("ar", {}).get("relations", {}).values()):
                    trace_msg = f"← وجدنا أن {concept} {rel_label} {loc_label}"
                else:
                    trace_msg = f"← وجدنا أن {concept} {relation_used} {location}"
                
                return {
                    "type": "location",
                    "result": True,
                    "concept": concept,
                    "location": location,
                    "location_label": loc_label,
                    "trace": prag_trace + [f"البحث عن موطن {concept} في العالم '{world}'", trace_msg] + conflict_trace,
                    "confidence": 1.0
                }
        return None

    def _handle_causal_why(self, mapped_concepts, words, world, part, prag_trace):
        is_why_query = any(w in words for w in ["لماذا", "ليه", "بسبب", "علل", "why", "because", "pourquoi", "cause"])
        if is_why_query and len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            target_concept = mapped_concepts[1] if len(mapped_concepts) >= 2 else None
            
            found_edge = None
            if self.handler.graph.has_node(concept):
                for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                    if data.get("type") == "inferred" and data.get("world") == world:
                        if target_concept:
                            if to_node == target_concept:
                                found_edge = (concept, to_node, data)
                                break
                        else:
                            target_labels = self.handler.graph.nodes[to_node].get("labels", [])
                            if any(w in target_labels for w in words):
                                found_edge = (concept, to_node, data)
                                break
                                
                if not found_edge and not target_concept:
                    for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                        if data.get("type") == "inferred" and data.get("world") == world:
                            found_edge = (concept, to_node, data)
                            break
                            
            if found_edge:
                sub, obj, data = found_edge
                sub_lbl = self.handler.graph.nodes[sub].get("labels", [sub])[0] if sub in self.handler.graph else sub
                obj_lbl = self.handler.graph.nodes[obj].get("labels", [obj])[0] if obj in self.handler.graph else obj
                rel_name = data.get("relation", "relation")
                
                rule_desc = data.get("reason", "")
                rule_id = data.get("rule_id", "unknown_rule")
                confidence = data.get("confidence", 1.0)
                
                trace_chain = [
                    f"Parse: تحليل الاستعلام السببي '{part}'",
                    f"Extract: subject={sub_lbl} ({sub}), relation={rel_name}, target={obj_lbl} ({obj})",
                    f"Search Direct Facts: لم يتم العثور عليها كحقيقة مباشرة",
                    f"Apply Rules: تم تطبيق قاعدة الاستدلال '{rule_id}'",
                    f"Condition: مطابقة شروط القاعدة بنجاح",
                    f"Conclusion: استنتاج [{sub_lbl}] --({rel_name})--> [{obj_lbl}] (ثقة: {confidence})",
                    f"Result: {rule_desc}"
                ]
                
                return {
                    "type": "causal_reasoning",
                    "result": True,
                    "subject": sub,
                    "subject_label": sub_lbl,
                    "relation": rel_name,
                    "object": obj,
                    "object_label": obj_lbl,
                    "reason": rule_desc,
                    "rule_id": rule_id,
                    "trace": prag_trace + trace_chain,
                    "confidence": confidence
                }
        return None

    def _handle_classification(self, mapped_concepts, words, language, part, prag_trace):
        is_classification_query = self._is_classification_word_query(words, language)
            
        if is_classification_query and len(mapped_concepts) >= 2:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            try:
                idx1 = self._get_concept_index(c1, words, language, part)
                idx2 = self._get_concept_index(c2, words, language, part)
                if idx1 > idx2:
                    c1, c2 = c2, c1
            except Exception:
                pass
                
            is_same_type_query = False
            same_type_markers = []
            if self.handler and hasattr(self.handler, "language_rules") and self.handler.language_rules:
                lang_rules = self.handler.language_rules.get(language, {})
                same_type_markers = list(lang_rules.get("same_type_indicators", []))
                if not same_type_markers:
                    for lang in ["ar", "en", "fr"]:
                        same_type_markers.extend(self.handler.language_rules.get(lang, {}).get("same_type_indicators", []))
                        
            if not same_type_markers:
                same_type_markers = [
                    "نفس النوع", "نفس الفئة", "نفس التصنيف", "نوع واحد", "نفس فئة",
                    "same type", "same category", "same class", "same kind",
                    "même type", "meme type", "même catégorie", "meme categorie", "même classe"
                ]
            if any(marker in part.lower() for marker in same_type_markers):
                is_same_type_query = True
                
            if is_same_type_query:
                cat1 = self.handler.graph.nodes[c1].get("category") if c1 in self.handler.graph else None
                cat2 = self.handler.graph.nodes[c2].get("category") if c2 in self.handler.graph else None
                
                parents1 = set()
                parents2 = set()
                if c1 in self.handler.graph:
                    for _, to_node, data in self.handler.graph.out_edges(c1, data=True):
                        if data.get("relation") == "is_a":
                            parents1.add(to_node)
                if c2 in self.handler.graph:
                    for _, to_node, data in self.handler.graph.out_edges(c2, data=True):
                        if data.get("relation") == "is_a":
                            parents2.add(to_node)
                            
                shared_parents = parents1.intersection(parents2)
                
                is_same = False
                reason = ""
                if cat1 and cat2 and cat1 == cat2:
                    is_same = True
                    cat_label = self.handler.graph.nodes[cat1].get("labels", [cat1])[0] if cat1 in self.handler.graph else cat1
                    reason = f"كلا المفهومين ينتميان لنفس الفئة العامة [{cat_label}]"
                elif shared_parents:
                    is_same = True
                    parent_lbl = self.handler.graph.nodes[list(shared_parents)[0]].get("labels", [list(shared_parents)[0]])[0] if list(shared_parents)[0] in self.handler.graph else list(shared_parents)[0]
                    reason = f"كلا المفهومين يشتركان في التصنيف الفرعي المباشر [{parent_lbl}]"
                else:
                    reason = f"لا يوجد فئة عامة مشتركة أو سلف تصنيفي مباشر يربط بين المفهومين"
                    
                c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
                c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2
                
                return {
                    "type": "classification",
                    "result": is_same,
                    "concept1": c1,
                    "concept2": c2,
                    "is_same_type": True,
                    "trace": prag_trace + [f"التحقق من تطابق النوع لـ '{c1_lbl}' و '{c2_lbl}'", reason],
                    "confidence": 1.0
                }
            else:
                res = self.check_is_a_relationship(c1, c2)
                if res["result"]:
                    return {
                        "type": "classification",
                        "result": True,
                        "concept1": c1,
                        "concept2": c2,
                        "trace": prag_trace + res["trace"],
                        "confidence": 1.0
                    }
                
                # Check for other relationships in the active world between c1 (or ancestors) and c2 (or ancestors)
                # Find ancestors of c1
                ancestors1 = {c1}
                to_explore = [c1]
                while to_explore:
                    curr = to_explore.pop(0)
                    if self.handler.graph.has_node(curr):
                        for _, to_node, edata in self.handler.graph.out_edges(curr, data=True):
                            if edata.get("relation") == "is_a":
                                if to_node not in ancestors1:
                                    ancestors1.add(to_node)
                                    to_explore.append(to_node)
                                    
                # Find ancestors of c2
                ancestors2 = {c2}
                to_explore = [c2]
                while to_explore:
                    curr = to_explore.pop(0)
                    if self.handler.graph.has_node(curr):
                        for _, to_node, edata in self.handler.graph.out_edges(curr, data=True):
                            if edata.get("relation") == "is_a":
                                if to_node not in ancestors2:
                                    ancestors2.add(to_node)
                                    to_explore.append(to_node)
                                    
                # Check active/inferred edges
                world = self.handler.active_world
                found_relation = None
                edge_data = None
                u_source = None
                v_target = None
                
                for u in ancestors1:
                    if self.handler.graph.has_node(u):
                        for _, v_node, data in self.handler.graph.out_edges(u, data=True):
                            if v_node in ancestors2:
                                edge_world = data.get("world", "reality")
                                edge_status = data.get("status", "active")
                                if edge_world == world and edge_status == "active":
                                    found_relation = data.get("relation")
                                    edge_data = data
                                    u_source = u
                                    v_target = v_node
                                    break
                        if found_relation:
                            break
                            
                if found_relation:
                    # If the relation is "prohibited_case" or "prohibited_relation", the logical conclusion is False
                    is_prohibited = found_relation in ["prohibited_case", "prohibited_relation"]
                    result_val = not is_prohibited
                    
                    c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
                    c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2
                    u_lbl = self.handler.graph.nodes[u_source].get("labels", [u_source])[0] if u_source in self.handler.graph else u_source
                    v_lbl = self.handler.graph.nodes[v_target].get("labels", [v_target])[0] if v_target in self.handler.graph else v_target
                    
                    rel_meta = self.handler.graph.graph.get("relations_metadata", {})
                    rel_display = rel_meta.get(found_relation, {}).get("name", found_relation) if isinstance(rel_meta, dict) else found_relation
                    
                    if is_prohibited:
                        conclusion = f"العلاقة محظورة: [{u_lbl}] --({rel_display})--> [{v_lbl}]"
                    else:
                        conclusion = f"تم العثور على علاقة منطقية: [{u_lbl}] --({rel_display})--> [{v_lbl}]"
                        
                    return {
                        "type": "classification",
                        "result": result_val,
                        "concept1": c1,
                        "concept2": c2,
                        "trace": prag_trace + [
                            f"استعلام علاقة تصنيفية بين '{c1_lbl}' و '{c2_lbl}'",
                            conclusion
                        ],
                        "confidence": edge_data.get("confidence", 1.0)
                    }
                    
                return {
                    "type": "classification",
                    "result": False,
                    "concept1": c1,
                    "concept2": c2,
                    "trace": prag_trace + res["trace"] + ["لا يوجد علاقة تصنيفية أو حكم منطقي يربط بين المفهومين في قاعدة المعرفة"],
                    "confidence": 1.0
                }
        return None

    def _handle_relation_path(self, mapped_concepts, part, world, prag_trace, words):
        is_relation_query = any(w in words for w in ["علاقة", "الروابط", "رابط", "يربط", "علاقه", "العلاقة", "العلاقه", "relation", "relationship", "connect", "connection", "link", "between", "entre"]) and len(mapped_concepts) >= 2
        if is_relation_query:
            c1, c2 = mapped_concepts[0], mapped_concepts[1]
            c1_lbl = self.handler.graph.nodes[c1].get("labels", [c1])[0] if c1 in self.handler.graph else c1
            c2_lbl = self.handler.graph.nodes[c2].get("labels", [c2])[0] if c2 in self.handler.graph else c2
            
            is_deep = any(keyword in part.lower() for keyword in ["عميق", "مسار", "سلسلة", "تتبع", "مفصل", "تفصيل", "deep", "detailed", "path", "traverse", "unrestricted", "chain"])
            
            active_undirected = nx.Graph()
            for node in self.handler.graph.nodes():
                active_undirected.add_node(node)
                
            for u, v, data in self.handler.graph.edges(data=True):
                edge_type = data.get("type", "relation")
                edge_world = data.get("world", "reality")
                edge_status = data.get("status", "active")
                if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                    if edge_status == "active":
                        if not active_undirected.has_edge(u, v):
                            active_undirected.add_edge(u, v, edges=[])
                        active_undirected[u][v]['edges'].append((u, v, data))
                        
            path_steps = []
            path_found = False
            path_nodes = []
            
            if is_deep:
                try:
                    path_nodes = nx.shortest_path(active_undirected, source=c1, target=c2)
                    path_found = True
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    path_found = False
            else:
                if active_undirected.has_edge(c1, c2):
                    path_nodes = [c1, c2]
                    path_found = True
                else:
                    path_found = False
                    
            if path_found and len(path_nodes) >= 2:
                for i in range(len(path_nodes) - 1):
                    u_node = path_nodes[i]
                    v_node = path_nodes[i+1]
                    edge_list = active_undirected[u_node][v_node]['edges']
                    step_desc_list = []
                    for src, tgt, edge_data in edge_list:
                        rel_name = edge_data.get("relation", "relation")
                        rel_meta = self.handler.graph.graph.get("relations_metadata", {})
                        if isinstance(rel_meta, dict) and rel_name in rel_meta:
                            rel_display = rel_meta[rel_name].get("name", rel_name)
                        else:
                            rel_display = rel_name
                            
                        src_lbl = self.handler.graph.nodes[src].get("labels", [src])[0] if src in self.handler.graph else src
                        tgt_lbl = self.handler.graph.nodes[tgt].get("labels", [tgt])[0] if tgt in self.handler.graph else tgt
                        step_desc_list.append(f"({src_lbl}) --[{rel_display}]--> ({tgt_lbl})")
                    path_steps.append(" أو ".join(step_desc_list))
                    
                query_mode_str = "عميق" if is_deep else "محدد"
                trace_msg = [
                    f"استعلام علاقات {query_mode_str} بين '{c1_lbl}' و '{c2_lbl}'",
                    f"تم العثور على مسار يربط بين المفهومين يتكون من {len(path_nodes)} عقدة"
                ]
                
                return {
                    "type": "relation_path",
                    "result": True,
                    "concept1": c1,
                    "concept1_label": c1_lbl,
                    "concept2": c2,
                    "concept2_label": c2_lbl,
                    "is_deep": is_deep,
                    "path_found": True,
                    "path_nodes": path_nodes,
                    "path_steps": path_steps,
                    "trace": prag_trace + trace_msg,
                    "confidence": 1.0
                }
            else:
                query_mode_str = "عميق" if is_deep else "محدد"
                fail_msg = f"لا يوجد مسار علاقة {query_mode_str} يربط بين المفهومين '{c1_lbl}' و '{c2_lbl}' في قاعدة معرفة العالم '{world}'."
                if not is_deep:
                    fail_msg += " (يمكنك تجربة الاستعلام العميق بإضافة كلمة 'عميقة' أو 'مسار' لملاحظة الروابط غير المباشرة)."
                return {
                    "type": "relation_path",
                    "result": False,
                    "concept1": c1,
                    "concept1_label": c1_lbl,
                    "concept2": c2,
                    "concept2_label": c2_lbl,
                    "is_deep": is_deep,
                    "path_found": False,
                    "path_nodes": [],
                    "path_steps": [],
                    "trace": prag_trace + [f"استعلام علاقات {query_mode_str} بين '{c1_lbl}' و '{c2_lbl}'", "لم يتم العثور على روابط متصلة"],
                    "message": fail_msg,
                    "confidence": 0.8
                }
        return None

    def _handle_describe(self, mapped_concepts, words, world, prag_trace):
        is_describe_query = any(w in words for w in ["ما", "ماذا", "what", "من", "who", "هي", "هو"]) and len(mapped_concepts) >= 1
        if is_describe_query:
            concept = mapped_concepts[0]
            all_relations = []
            if self.handler.graph.has_node(concept):
                for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            to_label = self.handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in self.handler.graph else to_node
                            rel_name = data.get("relation", "unknown")
                            rel_meta = self.handler.graph.graph.get("relations_metadata", {})
                            if isinstance(rel_meta, dict) and rel_name in rel_meta:
                                rel_display = rel_meta[rel_name].get("name", rel_name)
                            else:
                                rel_display = rel_name
                            all_relations.append({
                                "relation": rel_name,
                                "relation_display": rel_display,
                                "target": to_node,
                                "target_label": to_label,
                                "confidence": data.get("confidence", 1.0)
                            })
                for from_node, _, data in self.handler.graph.in_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            from_label = self.handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in self.handler.graph else from_node
                            rel_name = data.get("relation", "unknown")
                            all_relations.append({
                                "relation": rel_name,
                                "source": from_node,
                                "source_label": from_label,
                                "direction": "incoming",
                                "confidence": data.get("confidence", 1.0)
                            })
            
            if all_relations:
                concept_label = self.handler.graph.nodes[concept].get("labels", [concept])[0] if concept in self.handler.graph else concept
                concept_category = self.handler.graph.nodes[concept].get("category", "") if concept in self.handler.graph else ""
                return {
                    "type": "describe",
                    "result": True,
                    "concept": concept,
                    "concept_label": concept_label,
                    "category": concept_category,
                    "relations": all_relations,
                    "trace": prag_trace + [f"استعلام وصفي عن المفهوم '{concept_label}' ({concept})", f"تم العثور على {len(all_relations)} علاقة مرتبطة"],
                    "confidence": 1.0
                }
        return None

    def _handle_knowledge_fallback(self, mapped_concepts, world, prag_trace):
        if len(mapped_concepts) >= 1:
            concept = mapped_concepts[0]
            all_out = []
            all_in = []
            if self.handler.graph.has_node(concept):
                for _, to_node, data in self.handler.graph.out_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            to_label = self.handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in self.handler.graph else to_node
                            all_out.append({
                                "relation": data.get("relation", "unknown"),
                                "target": to_node,
                                "target_label": to_label
                            })
                for from_node, _, data in self.handler.graph.in_edges(concept, data=True):
                    edge_type = data.get("type", "relation")
                    edge_world = data.get("world", "reality")
                    if edge_type == "relation" or (edge_type in ["fact", "inferred"] and edge_world == world):
                        if data.get("status", "active") == "active":
                            from_label = self.handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in self.handler.graph else from_node
                            all_in.append({
                                "relation": data.get("relation", "unknown"),
                                "source": from_node,
                                "source_label": from_label
                            })
            
            if all_out or all_in:
                concept_label = self.handler.graph.nodes[concept].get("labels", [concept])[0] if concept in self.handler.graph else concept
                return {
                    "type": "knowledge",
                    "result": True,
                    "concept": concept,
                    "concept_label": concept_label,
                    "outgoing": all_out,
                    "incoming": all_in,
                    "trace": prag_trace + [f"استعلام عام عن المعرفة المتوفرة حول '{concept_label}'", f"← علاقات صادرة: {len(all_out)}, علاقات واردة: {len(all_in)}"],
                    "confidence": 0.8
                }
        return None
