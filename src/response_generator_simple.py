import random

class ResponseGeneratorSimple:
    def __init__(self, graph_handler):
        self.handler = graph_handler

    def get_template(self, key, language, default):
        """Retrieves a template from language_rules or falls back to default."""
        lang_rules = self.handler.language_rules.get(language, {})
        templates = lang_rules.get("templates", {})
        return templates.get(key, default)

    def get_concept_label(self, concept_id, language="ar"):
        """Translates a concept ID into the target language label."""
        if language == "ar":
            if self.handler.graph.has_node(concept_id):
                labels = self.handler.graph.nodes[concept_id].get("labels", [])
                if labels:
                    return labels[0]
            return concept_id
        else:
            lang_rules = self.handler.language_rules.get(language, {})
            lexicon = lang_rules.get("lexicon", {})
            
            candidates = []
            for k, v in lexicon.items():
                if v == concept_id:
                    candidates.append(k)
            if candidates:
                candidates.sort(key=len)
                return candidates[0]
                
            if self.handler.graph.has_node(concept_id):
                labels = self.handler.graph.nodes[concept_id].get("labels", [])
                if labels:
                    return labels[0]
            return concept_id

    def find_lowest_common_ancestor(self, c1, c2):
        """Finds the lowest common ancestor node using is_a relations."""
        def get_ancestors(node):
            ancestors = [node]
            visited = set()
            queue = [node]
            while queue:
                curr = queue.pop(0)
                if curr in visited:
                    continue
                visited.add(curr)
                if self.handler.graph.has_node(curr):
                    for _, to_node, data in self.handler.graph.out_edges(curr, data=True):
                        if data.get("relation") == "is_a":
                            if to_node not in ancestors:
                                ancestors.append(to_node)
                                queue.append(to_node)
            return ancestors

        anc1 = get_ancestors(c1)
        anc2 = get_ancestors(c2)
        for a in anc1:
            if a in anc2:
                return a
        return None

    def generate(self, res, persona_id="persona_1", language=None):
        """Generates a natural language response from the reasoning result, applying templates and persona styling."""
        if language is None:
            language = res.get("language") or getattr(self.handler, "active_language", "ar")
        if language not in ["ar", "en", "fr"]:
            language = "ar"

        persona = self.handler.get_persona(persona_id)
        
        # Load persona rules dynamically
        particles = [""]
        fillers = [""]
        if persona:
            style = persona.get("language_style", {})
            particles = style.get("particles", [""])
            fillers = style.get("filler_words", [""])
            
        p_ref = random.choice(particles) if particles else ""
        f_ref = random.choice(fillers) if fillers else ""
        
        if language == "ar":
            prefix = f"{p_ref}، {f_ref} " if (p_ref or f_ref) else ""
        else:
            prefix = f"{p_ref}, {f_ref} " if (p_ref or f_ref) else ""
            prefix = prefix.strip(", ") + " " if prefix else ""
            
        type_ = res.get("type", "unknown")
        
        # 1. Classification Response
        if type_ == "classification":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            key = "classification_true" if res["result"] else "classification_false"
            
            default_val = {
                "classification_true": {
                    "ar": "{concept1} هو {concept2}، دي الحقيقة! الاستدلال التصنيفي أثبت العلاقة دي بالوراثة الصاعدة.",
                    "en": "{concept1} is a {concept2}, that's correct! Taxonomic deduction proves this relation via ascending inheritance.",
                    "fr": "{concept1} est un {concept2}, c'est exact! La déduction taxonomique prouve cette relation par héritage ascendant."
                },
                "classification_false": {
                    "ar": "حسب معرفتي المنطقية {concept1} ليس {concept2}.",
                    "en": "According to my logical knowledge, {concept1} is not a {concept2}.",
                    "fr": "Selon mes connaissances logiques, {concept1} n'est pas un {concept2}."
                }
            }[key].get(language, "")
            
            template = self.get_template(key, language, default_val)
            ans = template.format(concept1=c1_lbl, concept2=c2_lbl)
            return prefix + ans
                
        # 2. Location Response
        elif type_ == "location":
            c_lbl = self.get_concept_label(res["concept"], language)
            loc_lbl = self.get_concept_label(res.get("location_label", res.get("location", "")), language)
            default_val = {
                "ar": "{concept} بيعيش في {location}.",
                "en": "{concept} lives in the {location}.",
                "fr": "{concept} vit dans la {location}."
            }.get(language, "")
            template = self.get_template("location", language, default_val)
            ans = template.format(concept=c_lbl, location=loc_lbl)
            return prefix + ans
            
        # 3. Hypothetical Response (Causal + Analogy)
        elif type_ == "hypothetical":
            entity_lbl = self.get_concept_label(res["entity"], language)
            env_lbl = self.get_concept_label(res["environment"], language)
            
            if res["needs_adaptation"]:
                prop_lbl = self.get_concept_label(res["transferred_property"], language)
                cand_lbl = self.get_concept_label(res["analogy_candidate"], language)
                default_val = {
                    "ar": "لو {entity} عاش في {environment}، أكيد محتاج يتكيف! البيئة هناك تفرض متطلبات خاصة، عشان كدة هيحتاج يطور {transferred_property} بالقياس والتناظر مع {analogy_candidate} اللي بيعيش هناك بالفعل عشان يتكيف مع بيئته الجديدة.",
                    "en": "if {entity} lived in {environment}, it would definitely need to adapt! The environment there imposes specific requirements, which is why it would need to develop {transferred_property} based on analogy with {analogy_candidate} that lives there to adapt to its new environment.",
                    "fr": "si un {entity} vivait dans l'{environment}, il aurait certainement besoin de s'adapter! L'environnement y impose des exigences spécifiques, c'est pourquoi il devrait développer une {transferred_property} par analogie avec {analogy_candidate} qui y vit déjà pour s'adapter à son nouvel environnement."
                }.get(language, "")
                template = self.get_template("hypothetical_needs_adaptation", language, default_val)
                ans = template.format(entity=entity_lbl, environment=env_lbl, transferred_property=prop_lbl, analogy_candidate=cand_lbl)
            else:
                default_val = {
                    "ar": "لو {entity} عاش في {environment} مش محتاج يغير صفاته الجسدية لأنه مهيأ ليها بالفعل.",
                    "en": "if {entity} lived in {environment}, it would not need to change its physical properties because it is already suited for it.",
                    "fr": "si un {entity} vivait dans l'{environment}, il n'aurait pas besoin de modifier ses propriétés physiques car il y est déjà adapté."
                }.get(language, "")
                template = self.get_template("hypothetical_no_adaptation", language, default_val)
                ans = template.format(entity=entity_lbl, environment=env_lbl)
            return prefix + ans
                
        # 4. Comparison Response
        elif type_ == "comparison":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            
            p1_str = "، ".join([self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "has_property"])
            p2_str = ".. ".join([self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "has_property"])
            
            l1 = next((self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "lives_in"), None)
            l2 = next((self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "lives_in"), None)
            
            common = self.find_lowest_common_ancestor(res["concept1"], res["concept2"])
            
            l1_fallback = self.get_template("comparison_lives_in_fallback", language, "its environment" if language == "en" else ("son environnement" if language == "fr" else "بيئته"))
            p1_fallback = self.get_template("comparison_props_fallback_1", language, "properties optimized for its environment" if language == "en" else ("des propriétés optimisées pour son environnement" if language == "fr" else "صفات مخصصة لبيئته"))
            p2_fallback = self.get_template("comparison_props_fallback_2", language, "properties suited for the cold" if language == "en" else ("des propriétés adaptées au froid" if language == "fr" else "صفات تناسب البرودة"))
            common_fallback = self.get_template("comparison_common_fallback", language, "entities" if language == "en" else ("entités" if language == "fr" else "كائنات"))
            
            l1_str = l1 or l1_fallback
            l2_str = l2 or l2_fallback
            p1_formatted = p1_str or p1_fallback
            p2_formatted = p2_str or p2_fallback
            
            common_lbl = self.get_concept_label(common, language) if common else common_fallback
            
            default_val = {
                "ar": "الفرق واضح جداً بين {concept1} و {concept2}: أولاً، {concept1} بيعيش في {l1_str} وعنده {p1_formatted}. أما {concept2} فبيعيش في {l2_str} وعنده {p2_formatted}. لكن التشابه الجوهري أن كلاهما {common_lbl} تصنيفياً.",
                "en": "The difference is very clear between {concept1} and {concept2}: first, {concept1} lives in {l1_str} and has {p1_formatted}. On the other hand, {concept2} lives in {l2_str} and has {p2_formatted}. However, the core similarity is that both are taxonomically {common_lbl}.",
                "fr": "La différence est très claire entre {concept1} et {concept2}: premièrement, {concept1} vit dans {l1_str} et a {p1_formatted}. D'un autre côté, {concept2} vit dans {l2_str} et a {p2_formatted}. Cependant, la similitude fondamentale est que les deux sont taxonomiquement des {common_lbl}."
            }.get(language, "")
            
            template = self.get_template("comparison", language, default_val)
            ans = template.format(
                concept1=c1_lbl,
                concept2=c2_lbl,
                l1_str=l1_str,
                l2_str=l2_str,
                p1_formatted=p1_formatted,
                p2_formatted=p2_formatted,
                common_lbl=common_lbl
            )
            return prefix + ans
            
        # 6. Teaching Response
        elif type_ == "teaching":
            status = res.get("status")
            world = res.get("world", "reality")
            msg = res.get("message", "")
            
            status_keys = {
                "added": "teaching_added",
                "identical": "teaching_identical",
                "auto_replaced": "teaching_auto_replaced",
                "auto_rejected": "teaching_auto_rejected",
                "non_interactive_rejected": "teaching_non_interactive_rejected"
            }
            
            key = status_keys.get(status)
            if key:
                default_val = {
                    "added": {
                        "en": f"New fact saved successfully in world '{world}'.",
                        "fr": f"Nouveau fait enregistré avec succès dans le monde '{world}'.",
                        "ar": f"تم حفظ المعلومة بنجاح في العالم '{world}'."
                    },
                    "identical": {
                        "en": f"The fact already exists in world '{world}'.",
                        "fr": f"Le fait existe déjà dans le monde '{world}'.",
                        "ar": f"المعلومة موجودة بالفعل في العالم '{world}'."
                    },
                    "auto_replaced": {
                        "en": f"Fact automatically updated because new confidence is higher.",
                        "fr": f"Fait automatiquement mis à jour car la nouvelle confiance est plus élevée.",
                        "ar": f"تم تحديث المعلومة تلقائياً لأن الثقة الجديدة أعلى."
                    },
                    "auto_rejected": {
                        "en": f"New fact rejected because existing confidence is higher.",
                        "fr": f"Nouveau fait rejeté car la confiance existante est plus élevée.",
                        "ar": f"تم رفض المعلومة الجديدة لأن الثقة الحالية أعلى."
                    },
                    "non_interactive_rejected": {
                        "en": f"New fact ignored due to conflict.",
                        "fr": f"Nouveau fait ignoré en raison d'un conflit.",
                        "ar": f"تم تجاهل المعلومة الجديدة بسبب وجود تعارض."
                    }
                }[status][language]
                template = self.get_template(key, language, default_val)
                ans = template.format(world=world)
            else:
                default_fallback = {
                    "en": "Fact operation finished.",
                    "fr": "Opération sur le fait terminée.",
                    "ar": "تم إنهاء عملية معالجة الحقيقة."
                }.get(language, "Fact operation finished.")
                template = self.get_template("teaching_fallback", language, msg or default_fallback)
                ans = template
            return prefix + ans
            
        # 7. Anomaly Response
        elif type_ == "anomaly":
            entity_lbl = self.get_concept_label(res["entity"], language)
            default_val = {
                "en": "An anomaly detected for {entity}: condition is {anomaly_type} due to {reason} (anomaly score: {anomaly_score:.2f}).",
                "fr": "Une anomalie détectée pour {entity}: état {anomaly_type} dû à {reason} (score d'anomalie: {anomaly_score:.2f}).",
                "ar": "تم رصد استثناء وشذوذ عن القاعدة للـ {entity}: الحالة هي {anomaly_type} والسبب هو {reason} (معدل الشذوذ {anomaly_score:.2f})."
            }.get(language, "")
            template = self.get_template("anomaly", language, default_val)
            ans = template.format(entity=entity_lbl, anomaly_type=res["anomaly_type"], reason=res["reason"], anomaly_score=res["anomaly_score"])
            return prefix + ans
            
        # 8. Comparison Scale Response
        elif type_ == "comparison_scale":
            c1_lbl = self.get_concept_label(res["entity1"], language)
            c2_lbl = self.get_concept_label(res["entity2"], language)
            key = "comparison_scale_true" if res["result"] else "comparison_scale_false"
            
            default_val = {
                "comparison_scale_true": {
                    "en": "Comparing entities on scale [{property_name}]: value of {entity1} is greater than {entity2}.",
                    "fr": "Comparaison sur l'échelle [{property_name}]: valeur de {entity1} est plus grand que {entity2}.",
                    "ar": "مقارنة الكائنات على مقياس [{property_name}]: قيمة {entity1} أكبر من قيمة {entity2}."
                },
                "comparison_scale_false": {
                    "en": "Comparing entities on scale [{property_name}]: value of {entity1} is not greater than {entity2}.",
                    "fr": "Comparaison sur l'échelle [{property_name}]: valeur de {entity1} n'est pas plus grand que {entity2}.",
                    "ar": "مقارنة الكائنات على مقياس [{property_name}]: قيمة {entity1} ليست أكبر من قيمة {entity2}."
                }
            }[key].get(language, "")
            
            template = self.get_template(key, language, default_val)
            ans = template.format(entity1=c1_lbl, entity2=c2_lbl, property_name=res["property_name"])
            return prefix + ans
            
        # 9. Temporal Logic Response
        elif type_ == "temporal_logic":
            key = "temporal_logic_true" if res["result"] else "temporal_logic_false"
            default_val = {
                "temporal_logic_true": {
                    "en": "Temporal order shows that event [{event}] occurs before event [{reference}].",
                    "fr": "L'ordre temporel indique que l'événement [{event}] se produit avant l'événement [{reference}].",
                    "ar": "الترتيب الزمني يوضح أن حدث [{event}] يقع قبل الحدث [{reference}]."
                },
                "temporal_logic_false": {
                    "en": "Temporal order shows that event [{event}] occurs not before event [{reference}].",
                    "fr": "L'ordre temporel indique que l'événement [{event}] se produit pas avant l'événement [{reference}].",
                    "ar": "الترتيب الزمني يوضح أن حدث [{event}] يقع ليس قبل الحدث [{reference}]."
                }
            }[key].get(language, "")
            template = self.get_template(key, language, default_val)
            ans = template.format(event=res["event"], reference=res["reference"])
            return prefix + ans
            
        # 10. Modality Response
        elif type_ == "modality":
            key = "modality_true" if res["result"] else "modality_false"
            default_val = {
                "modality_true": {
                    "en": "Based on modal logic, this hypothesis is true and certain (modality type: {modality}, confidence: {modality_confidence:.2f}).",
                    "fr": "Selon la logique modale, cette hypothèse est vraie et certaine (type de modalité: {modality}, confiance: {modality_confidence:.2f}).",
                    "ar": "استناداً لمنطق الجهة والضرورة، فإن هذه الفرضية صحيحة ومؤكدة (نوع الجهة: {modality} وثقتها {modality_confidence:.2f})."
                },
                "modality_false": {
                    "en": "Based on modal logic, this hypothesis is uncertain or not necessary (modality type: {modality}, confidence: {modality_confidence:.2f}).",
                    "fr": "Selon la logique modale, cette hypothèse est incertaine ou pas nécessaire (type de modalité: {modality}, confiance: {modality_confidence:.2f}).",
                    "ar": "استناداً لمنطق الجهة والضرورة، فإن هذه الفرضية غير صحيحة أو غير مؤكدة (نوع الجهة: {modality} وثقتها {modality_confidence:.2f})."
                }
            }[key].get(language, "")
            template = self.get_template(key, language, default_val)
            ans = template.format(modality=res["modality"], modality_confidence=res["modality_confidence"])
            return prefix + ans
            
        # 11. Causal Chain Response
        elif type_ == "causal_chain":
            steps = res["chain"]["steps"]
            chain_str = " -> ".join([f"[{s['event']}]" for s in steps])
            default_val = {
                "en": "The multi-step causal chain starting from [{initial_state}] is: {chain_str}.",
                "fr": "La chaîne causale à plusieurs étapes à partir de [{initial_state}] est: {chain_str}.",
                "ar": "التسلسل السببي متعدد الخطوات بدءاً من [{initial_state}] هو: {chain_str}."
            }.get(language, "")
            template = self.get_template("causal_chain", language, default_val)
            ans = template.format(initial_state=res["initial_state"], chain_str=chain_str)
            return prefix + ans
            
        # 12. Quantifier Response
        elif type_ == "quantifier":
            key = "quantifier_true" if res["result"] else "quantifier_false"
            default_val = {
                "quantifier_true": {
                    "en": "Quantifier inference proves that this proposition is logically true (queried quantifier: {quantifier}).",
                    "fr": "L'inférence du quantificateur prouve que cette proposition est logiquement vraie (quantificateur interrogé: {quantifier}).",
                    "ar": "استدلال سور القضية يثبت أن هذه القضية صحيحة منطقياً (السور المستعلم عنه: {quantifier})."
                },
                "quantifier_false": {
                    "en": "Quantifier inference proves that this proposition is not logically entailed (queried quantifier: {quantifier}).",
                    "fr": "L'inférence du quantificateur prouve que cette proposition n'est pas logiquement impliquée (quantificateur interrogé: {quantifier}).",
                    "ar": "استدلال سور القضية يثبت أن هذه القضية غير مستلزمة منطقياً (السور المستعلم عنه: {quantifier})."
                }
            }[key].get(language, "")
            template = self.get_template(key, language, default_val)
            ans = template.format(quantifier=res["quantifier"])
            return prefix + ans
            
        # 13. Negation Response
        elif type_ == "negation":
            key = "negation_true" if res["result"] else "negation_false"
            default_val = {
                "negation_true": {
                    "en": "Negation and polarity inference proves that this negated proposition is true.",
                    "fr": "L'inférence de la négation et polarité prouve que cette proposition niée est vraie.",
                    "ar": "استدلال النفي وعكس القطبية يثبت أن هذه القضية المنفية صحيحة."
                },
                "negation_false": {
                    "en": "Negation and polarity inference proves that this negated proposition is false.",
                    "fr": "L'inférence de la négation et polarité prouve que cette proposition niée est fausse.",
                    "ar": "استدلال النفي وعكس القطبية يثبت أن هذه القضية المنفية خاطئة."
                }
            }[key].get(language, "")
            template = self.get_template(key, language, default_val)
            ans = template
            return prefix + ans
            
        # 14. Causal Reasoning Response (Why query / Inference Rules)
        elif type_ == "causal_reasoning":
            return prefix + res.get("reason", "")

        # 15. Semantic Roles Response
        elif type_ == "semantic_roles":
            roles_list = []
            for r_type, val in res["roles"].items():
                val_lbl = self.get_concept_label(val, language)
                roles_list.append(f"{r_type}: {val_lbl}")
            sep = self.get_template("semantic_roles_separator", language, "، " if language == "ar" else ", ")
            roles_str = sep.join(roles_list)
            
            default_val = {
                "en": "Semantic roles for predicate [{predicate}] are: {roles_str}.",
                "fr": "Les rôles sémantiques pour le prédicat [{predicate}] sont: {roles_str}.",
                "ar": "الأدوار الدلالية للفعل [{predicate}] هي: {roles_str}."
            }.get(language, "")
            template = self.get_template("semantic_roles", language, default_val)
            ans = template.format(predicate=res["predicate"], roles_str=roles_str)
            return prefix + ans

        # 15.5. Relation Path Response
        elif type_ == "relation_path":
            c1_lbl = res.get("concept1_label", "")
            c2_lbl = res.get("concept2_label", "")
            is_deep = res.get("is_deep", False)
            path_steps = res.get("path_steps", [])
            
            if res.get("path_found") and path_steps:
                steps_str = ("، ثم " if language == "ar" else ", then ").join(path_steps)
                if is_deep:
                    ans = {
                        "en": f"Indirect relation path found between [{c1_lbl}] and [{c2_lbl}]: {steps_str}.",
                        "fr": f"Chemin de relation indirecte trouvé entre [{c1_lbl}] et [{c2_lbl}]: {steps_str}.",
                        "ar": f"تم العثور على مسار علاقة غير مباشر (عميق) بين [{c1_lbl}] و [{c2_lbl}]: {steps_str}."
                    }.get(language, f"Indirect relation path: {steps_str}")
                else:
                    ans = {
                        "en": f"Direct relation found between [{c1_lbl}] and [{c2_lbl}]: {steps_str}.",
                        "fr": f"Relation directe trouvée entre [{c1_lbl}] et [{c2_lbl}]: {steps_str}.",
                        "ar": f"توجد علاقة مباشرة بين [{c1_lbl}] و [{c2_lbl}]: {steps_str}."
                    }.get(language, f"Direct relation found: {steps_str}")
            else:
                ans = {
                    "en": "No relation path found between the two concepts in the knowledge base.",
                    "fr": "Aucun chemin de relation trouvé entre les deux concepts dans la base de connaissances.",
                    "ar": "لا توجد علاقة بين المفهومين في قاعدة المعرفة."
                }.get(language, "No relation path found.")
            return prefix + ans

        # 16. Describe Response
        elif type_ == "describe":
            concept_label = res.get("concept_label", self.get_concept_label(res.get("concept", ""), language))
            category = res.get("category", "")
            relations = res.get("relations", [])
            
            parts = []
            if category:
                default_cat = {
                    "en": "{concept_label} is a concept of type ({category})",
                    "fr": "{concept_label} est un concept de type ({category})",
                    "ar": "{concept_label} هو مفهوم من نوع ({category})"
                }.get(language, "")
                template_cat = self.get_template("describe_category", language, default_cat)
                parts.append(template_cat.format(concept_label=concept_label, category=category))
            else:
                parts.append(concept_label)
            
            # De-duplicate outgoing relations
            seen_out = set()
            unique_outgoing = []
            for r in relations:
                if "target_label" in r:
                    key = (r.get("relation"), r.get("target"))
                    if key not in seen_out:
                        seen_out.add(key)
                        unique_outgoing.append(r)
            
            # De-duplicate incoming relations
            seen_in = set()
            unique_incoming = []
            for r in relations:
                if "source_label" in r:
                    key = (r.get("source"), r.get("relation"))
                    if key not in seen_in:
                        seen_in.add(key)
                        unique_incoming.append(r)
            
            default_rel_map = {
                "ar": {"is_a": "هو", "lives_in": "يعيش في", "has_property": "لديه صفة", "part_of": "جزء من", "rises_from": "يشرق من"},
                "en": {"is_a": "is a", "lives_in": "lives in", "has_property": "has property", "part_of": "part of", "rises_from": "rises from"},
                "fr": {"is_a": "est un", "lives_in": "vit dans", "has_property": "a la propriété", "part_of": "fait partie de", "rises_from": "se lève à"}
            }.get(language, {})
            mapped_rel_map = self.get_template("describe_rel_map", language, default_rel_map)
            
            for r in unique_outgoing[:5]:
                rel_display = mapped_rel_map.get(r.get("relation"), r.get("relation_display", r.get("relation", "")))
                parts.append(f"{rel_display} {r['target_label']}")
            
            for r in unique_incoming[:3]:
                rel_display = mapped_rel_map.get(r.get("relation"), r.get("relation", ""))
                parts.append(f"{r['source_label']} {rel_display} {concept_label}")
            
            sep = self.get_template("describe_separator", language, "، و" if language == "ar" else ", and ")
            body = sep.join(parts)
            return prefix + body + "."

        # 17. Knowledge Response
        elif type_ == "knowledge":
            concept_label = res.get("concept_label", self.get_concept_label(res.get("concept", ""), language))
            outgoing = res.get("outgoing", [])
            incoming = res.get("incoming", [])
            
            default_header = {
                "en": "Knowledge available about {concept_label}:",
                "fr": "Connaissances disponibles sur {concept_label}:",
                "ar": "المعرفة المتوفرة حول {concept_label}:"
            }.get(language, "")
            template_header = self.get_template("knowledge_header", language, default_header)
            parts = [template_header.format(concept_label=concept_label)]
            
            # De-duplicate outgoing
            seen_out = set()
            unique_outgoing = []
            for r in outgoing:
                key = (r.get("relation"), r.get("target"))
                if key not in seen_out:
                    seen_out.add(key)
                    unique_outgoing.append(r)
            
            # De-duplicate incoming
            seen_in = set()
            unique_incoming = []
            for r in incoming:
                key = (r.get("source"), r.get("relation"))
                if key not in seen_in:
                    seen_in.add(key)
                    unique_incoming.append(r)
            
            for r in unique_outgoing[:5]:
                parts.append(f"{concept_label} {r.get('relation', '')} {r.get('target_label', r.get('target', ''))}")
            
            for r in unique_incoming[:3]:
                parts.append(f"{r.get('source_label', r.get('source', ''))} {r.get('relation', '')} {concept_label}")
            
            sep = self.get_template("knowledge_separator", language, "، " if language == "ar" else ", ")
            body = sep.join(parts)
            return prefix + body + "."
            
        # 18. Honest Fail-safe
        else:
            default_val = {
                "ar": "بص بقى، معنديش أي معلومة أو حقيقة منطقية تسند السؤال ده في قاعدة البيانات حالياً، وأنا بفضل أقول معرفش على إني أهلس!",
                "en": "honestly, I do not possess any logical information or facts in the database to support this question, and I prefer to say I don't know rather than make things up!",
                "fr": "honnêtement, je ne dispose d'aucune information ou fait logique dans la base de données pour appuyer cette question, et je préfère dire que je ne sais pas plutôt que d'inventer!"
            }.get(language, "")
            template = self.get_template("unknown", language, default_val)
            return prefix + template
