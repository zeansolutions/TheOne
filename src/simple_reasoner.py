import os
import json
import re
import networkx as nx
from src.world_manager import WorldManager
from src.conflict_resolver import ConflictResolver
from src.conversation_manager import ConversationManager
from src.entity_resolver import EntityResolver
from src.manager.language_selection_engine import LanguageSelectionEngine
from src.reasoner.pattern_matcher import GenericPatternMatcher
from src.reasoner.learning_engine import InteractiveBootstrapper
from src.utils.logger import logger
from src.utils.profiler import profile_function

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

# Import modular delegators
from src.reasoner.entity_extractors import EntityExtractor
from src.reasoner.intent_handlers import IntentHandlers
from src.reasoner.response_builders import ResponseBuilder

class SimpleReasoner:
    def __init__(self, graph_handler):
        self.handler = graph_handler
        self.conversation_manager = ConversationManager()
        self.entity_resolver = EntityResolver(self.conversation_manager, self.handler)
        self.world_manager = WorldManager(self.handler)
        self.conflict_resolver = ConflictResolver(self.handler)
        
        # Modular components delegation
        self.entity_extractor = EntityExtractor(self)
        self.intent_handlers = IntentHandlers(self)
        self.response_builder = ResponseBuilder(self)
        
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
            
        # Instantiate Pattern Matcher and Learning Engine
        rules_path = getattr(self.handler, "language_rules_path", "data/language_rules.json")
        self.pattern_matcher = GenericPatternMatcher(rules_path)
        self.learning_engine = InteractiveBootstrapper(self.handler, rules_path)

    def _resolve_extracted_entity(self, val, language, context_concepts):
        return self.entity_extractor.resolve_extracted_entity(val, language, context_concepts)

    def _resolve_concept(self, val, language, context_concepts, trace=None):
        return self.entity_extractor.resolve_concept(val, language, context_concepts, trace=trace)

    def _get_concept_index(self, c, words, language, part=None):
        return self.entity_extractor.get_concept_index(c, words, language, part=part)

    def check_is_a_relationship(self, concept_id, target_category_id):
        """Checks if concept_id is a target_category_id directly or via transitive inheritance."""
        self.handler.infer_facts(self.handler.active_world)
        trace = []
        path = [concept_id, target_category_id]
        
        # Check direct or inferred edge
        for _, to_node, data in self.handler.graph.out_edges(concept_id, data=True):
            if data.get("relation") == "is_a" and to_node == target_category_id:
                reason = data.get("reason")
                sub_lbl = self.handler.graph.nodes[concept_id].get("labels", [concept_id])[0]
                obj_lbl = self.handler.graph.nodes[target_category_id].get("labels", [target_category_id])[0]
                logical_step = f"{sub_lbl} هو تصنيف فرعي من {obj_lbl} (علاقة is_a)"
                if reason:
                    if "استنتاج بالتعدي" in reason or "هو" in reason:
                        trace.append(reason)
                    else:
                        trace.append(f"{logical_step} [مصدر: {reason}]")
                else:
                    trace.append(logical_step)
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

    @profile_function
    def process_query(self, query, interactive=False, language=None, is_deep=None):
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
                res = self._process_query_internal(query, interactive, language, is_deep=is_deep)
                
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
            return self._process_query_internal(query, interactive, language, is_deep=is_deep)

    def _process_query_internal(self, query, interactive=False, language=None, is_deep=None):
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
                matched_by_pattern = False
                match_res = self.pattern_matcher.match(part)
                

                
                if match_res:
                    logger.info(f"Pattern matched successfully! Intent: {match_res.intent}, entities: {match_res.extracted_entities}")
                    extracted_concepts = []
                    expected_roles = [role for role in ["concept1", "concept2", "concept", "entity", "environment", "object"]
                                     if role in match_res.extracted_entities]
                    for role in expected_roles:
                        val = match_res.extracted_entities.get(role)
                        if val:
                            c = self._resolve_concept(val, language, context_concepts, trace=prag_trace)
                            if c and c not in extracted_concepts:
                                extracted_concepts.append(c)
                    if len(extracted_concepts) >= len(expected_roles) and len(extracted_concepts) > 0:
                        mapped_concepts = extracted_concepts
                        matched_by_pattern = True
                    else:
                        match_res = None

                if not matched_by_pattern:
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
                res = self._route_logical_reasoning(mapped_concepts, words, language, world, part, prag_trace, match_res, is_deep=is_deep)
                
                # Check for interactive/clarification fallback if result is unknown, it was a question, and no pattern matched
                if res.get("type") == "unknown" and is_question and not match_res:
                    proposal = self.learning_engine.propose_pattern(part)
                    if proposal:
                        if interactive:
                            print(f"\n💡 {proposal['suggested_question']}")
                            ans = input("هل هذا صحيح؟ (نعم/لا): ").strip()
                            if ans in ["نعم", "yes", "y", "صح", "بالظبط", "بالضبط"]:
                                success = self.learning_engine.save_new_pattern(proposal)
                                if success:
                                    print("✅ تم تعلم النمط الدلالي الجديد وحفظه بنجاح!")
                                    self.pattern_matcher.load_patterns()
                                    new_match_res = self.pattern_matcher.match(part)
                                    if new_match_res:
                                        res = self._route_logical_reasoning(mapped_concepts, words, language, world, part, prag_trace, new_match_res, is_deep=is_deep)
                            else:
                                print("❌ تم إلغاء عملية التعلم.")
                        else:
                            res = {
                                "type": "clarification_needed",
                                "result": False,
                                "suggested_question": proposal["suggested_question"],
                                "proposal": proposal,
                                "trace": prag_trace + [f"اكتشاف نمط دلالي جديد بحاجة لتوضيح: '{proposal['suggested_question']}'"],
                                "confidence": 0.5
                            }
                last_result = res
                
        return self.response_builder.build_answer(last_result, language=language)

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

    def _route_logical_reasoning(self, mapped_concepts, words, language, world, part, prag_trace, match_res=None, is_deep=None):
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

        # If matched by pattern, route to that specific intent first
        if match_res:
            intent = match_res.intent
            if intent == "classification":
                res = self._handle_classification(mapped_concepts, words, language, part, prag_trace, match_res)
                if res: return res
            elif intent == "location":
                res = self._handle_location(mapped_concepts, words, world, prag_trace, match_res)
                if res: return res
            elif intent == "hypothetical":
                res = self._handle_hypothetical(mapped_concepts, words, prag_trace, match_res)
                if res: return res
            elif intent == "comparison":
                res = self._handle_comparison_diff(mapped_concepts, words, world, prag_trace, match_res)
                if res: return res
            elif intent == "relation_path":
                res = self._handle_relation_path(mapped_concepts, part, world, prag_trace, words, match_res, is_deep=is_deep)
                if res: return res
            elif intent == "celestial":
                res = self._handle_celestial(mapped_concepts, words, language, world, prag_trace, match_res)
                if res: return res
            elif intent == "describe":
                res = self._handle_describe(mapped_concepts, words, world, prag_trace, match_res=match_res)
                if res: return res
            elif intent == "knowledge":
                res = self._handle_knowledge_fallback(mapped_concepts, world, prag_trace)
                if res: return res
        
        # 8. Semantic Roles (Level 1)
        res = self._handle_semantic_roles(words, language, prag_trace)
        if res: return res
        
        # 9. Celestial
        res = self._handle_celestial(mapped_concepts, words, language, world, prag_trace, match_res)
        if res: return res
        
        # 10. Comparison
        res = self._handle_comparison_diff(mapped_concepts, words, world, prag_trace, match_res)
        if res: return res
        
        # 11. Hypothetical
        res = self._handle_hypothetical(mapped_concepts, words, prag_trace, match_res)
        if res: return res
        
        # 12. Location
        res = self._handle_location(mapped_concepts, words, world, prag_trace, match_res)
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
        res = self._handle_classification(mapped_concepts, words, language, part, prag_trace, match_res)
        if res: return res
        
        # 15. Relation Path / Connection Search
        res = self._handle_relation_path(mapped_concepts, part, world, prag_trace, words, match_res, is_deep=is_deep)
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

    def _handle_anomaly(self, *args, **kwargs):
        return self.intent_handlers.handle_anomaly(*args, **kwargs)

    def _handle_comparison_scale(self, *args, **kwargs):
        return self.intent_handlers.handle_comparison_scale(*args, **kwargs)

    def _handle_temporal_logic(self, *args, **kwargs):
        return self.intent_handlers.handle_temporal_logic(*args, **kwargs)

    def _handle_modality(self, *args, **kwargs):
        return self.intent_handlers.handle_modality(*args, **kwargs)

    def _handle_causal_chain(self, *args, **kwargs):
        return self.intent_handlers.handle_causal_chain(*args, **kwargs)

    def _handle_quantifiers(self, *args, **kwargs):
        return self.intent_handlers.handle_quantifiers(*args, **kwargs)

    def _handle_negation(self, *args, **kwargs):
        return self.intent_handlers.handle_negation(*args, **kwargs)

    def _handle_semantic_roles(self, *args, **kwargs):
        return self.intent_handlers.handle_semantic_roles(*args, **kwargs)

    def _handle_celestial(self, *args, **kwargs):
        return self.intent_handlers.handle_celestial(*args, **kwargs)

    def _handle_comparison_diff(self, *args, **kwargs):
        return self.intent_handlers.handle_comparison_diff(*args, **kwargs)

    def _handle_hypothetical(self, *args, **kwargs):
        return self.intent_handlers.handle_hypothetical(*args, **kwargs)

    def _handle_location(self, *args, **kwargs):
        return self.intent_handlers.handle_location(*args, **kwargs)

    def _handle_causal_why(self, *args, **kwargs):
        return self.intent_handlers.handle_causal_why(*args, **kwargs)

    def _handle_classification(self, *args, **kwargs):
        return self.intent_handlers.handle_classification(*args, **kwargs)

    def _handle_relation_path(self, *args, **kwargs):
        return self.intent_handlers.handle_relation_path(*args, **kwargs)

    def _handle_describe(self, *args, **kwargs):
        return self.intent_handlers.handle_describe(*args, **kwargs)

    def _handle_knowledge_fallback(self, *args, **kwargs):
        return self.intent_handlers.handle_knowledge_fallback(*args, **kwargs)
