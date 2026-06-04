import re
import json
import random

class MultilingualExpressionRenderer:
    """
    Translates logical reasoning outputs into natural responses in the selected language,
    applying the selected persona's expressions and stylistic markers.
    Also translates the reasoning trace to match the target language.
    """
    
    def __init__(self, personas_data, graph_handler):
        self.handler = graph_handler
        # personas_data can be a parsed list from config/personas_multilingual.json or a path
        if isinstance(personas_data, str):
            with open(personas_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.personas = {p["id"]: p for p in data.get("personas", [])}
        else:
            self.personas = {p["id"]: p for p in personas_data}

        # Load fallback templates from JSON
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        fallback_path = os.path.join(base_dir, "data", "fallback_templates.json")
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                self.fallback_db = json.load(f)
        except Exception:
            self.fallback_db = {"concept_labels": {}, "templates": {}}
            
    def get_template(self, key, language, default):
        """
        Retrieves a sentence/phrase template from the language rules database.
        Falls back to a default if not found in the database.
        """
        lang_rules = self.handler.language_rules.get(language, {})
        templates = lang_rules.get("templates", {})
        return templates.get(key, default)

    def get_fallback_template(self, key, language):
        """
        Retrieves a baseline fallback template from the default_templates configuration database.
        """
        return self.fallback_db.get("templates", {}).get(language, {}).get(key, "")

    def get_concept_label(self, concept_id, language):
        """
        Translates a concept ID into the target language label.
        """
        # 1. Try fallbacks for common concepts first (to guarantee correct baseline translation)
        fallback_map = self.fallback_db.get("concept_labels", {}).get(language, {})
        if concept_id in fallback_map:
            return fallback_map[concept_id]

        # 2. Try to get from language rules lexicon (dynamic database lookup)
        lang_rules = self.handler.language_rules.get(language, {})
        lexicon = lang_rules.get("lexicon", {})
        
        # Invert lexicon
        candidates = []
        for k, v in lexicon.items():
            if v == concept_id:
                candidates.append(k)
                
        if candidates:
            # Sort by length and take the shortest/simplest candidate
            candidates.sort(key=len)
            return candidates[0]
            
        # 3. Fallback to node labels in graph
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

    def select_expression(self, expressions_list, context):
        """
        Selects a random expression from the list.
        """
        if not expressions_list:
            return ""
        return random.choice(expressions_list)

    def translate_trace_step(self, step, language):
        """
        Translates a single trace step from Arabic to English or French, replacing concept IDs as well.
        """
        if language == "ar":
            return step
            
        # 1. Translate concept IDs or Arabic labels embedded in trace to the target language
        # We can extract words and replace if they are concepts
        words = re.findall(r"\w+", step)
        translated_step = step
        for w in words:
            if self.handler.graph.has_node(w) or w in ["thin_fur", "thick_fur", "savanna", "arctic", "c_sun", "c_east", "c_west", "c_underground", "feline_carnivore", "polar_bear", "animal", "carnivore"]:
                translated_lbl = self.get_concept_label(w, language)
                translated_step = re.sub(r"\b" + w + r"\b", translated_lbl, translated_step)
                
        # 2. Check for matching Arabic patterns and map to target language
        # 1) Classification is_a
        m = re.search(r"(.+?) هو تصنيف فرعي من (.+?) \(علاقة is_a\)", translated_step)
        if m:
            c1, c2 = m.group(1), m.group(2)
            if language == "en":
                return f"{c1} is a subcategory of {c2} (is_a relation)"
            elif language == "fr":
                return f"{c1} est une sous-catégorie de {c2} (relation is_a)"
                
        # 2) Direct property
        m = re.search(r"(.+?) لديه الخاصية (.+?) بشكل مباشر", translated_step)
        if m:
            c1, c2 = m.group(1), m.group(2)
            if language == "en":
                return f"{c1} has property {c2} directly"
            elif language == "fr":
                return f"{c1} a la propriété {c2} directement"
                
        # 3) Inheritance chain
        m = re.search(r"تتبع الوراثة تصاعدياً: (.+?) يرث من (.+?)", translated_step)
        if m:
            c1, c2 = m.group(1), m.group(2)
            if language == "en":
                return f"Taxonomic inheritance tracing: {c1} inherits from {c2}"
            elif language == "fr":
                return f"Suivi de l'héritage taxonomique: {c1} hérite de {c2}"
                
        # 4) Inheritance deduction
        m = re.search(r"وجدنا أن (.+?) لديه الخاصية (.+?)، وبالتالي يرثها (.+?) بالتبعية", translated_step)
        if m:
            parent, prop, entity = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Found that {parent} has property {prop}, thus {entity} inherits it"
            elif language == "fr":
                return f"Trouvé que {parent} a la propriété {prop}, donc {entity} l'hérite par conséquent"
                
        # 5) Causal reasoning start
        m = re.search(r"بدء الاستدلال السببي للـ (.+?) في البيئة (.+?)", translated_step)
        if m:
            entity, env = m.group(1), m.group(2)
            if language == "en":
                return f"Starting causal reasoning for {entity} in environment {env}"
            elif language == "fr":
                return f"Début du raisonnement causal pour {entity} dans l'environnement {env}"
                
        # 6) Environment no requirements
        m = re.search(r"البيئة (.+?) لا تفرض أي متطلبات خاصة مسجلة في قاعدة المعرفة", translated_step)
        if m:
            env = m.group(1)
            if language == "en":
                return f"Environment {env} does not impose any special requirements registered in the knowledge base"
            elif language == "fr":
                return f"L'environnement {env} n'impose aucune exigence particulière enregistrée dans la base de connaissances"
                
        # 7) Environment requirement
        m = re.search(r"البيئة (.+?) بها (.+?) مما يستدعي متطلب: (.+?)", translated_step)
        if m:
            env, cond, req = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Environment {env} has condition {cond} which imposes requirement: {req}"
            elif language == "fr":
                return f"L'environnement {env} présente la condition {cond} ce qui impose l'exigence: {req}"
                
        # 8) Physical/morphological check
        m = re.search(r"الفحص الصرفي/الفيزيائي للـ (.+?): يمتلك (.+?)", translated_step)
        if m:
            entity, fur = m.group(1), m.group(2)
            if language == "en":
                return f"Physical check for {entity}: possesses {fur}"
            elif language == "fr":
                return f"Examen physique pour {entity}: possède {fur}"
                
        # 9) Requirement met
        m = re.search(r"الخاصية (.+?) تلبي المتطلب (.+?) بنجاح", translated_step)
        if m:
            fur, req = m.group(1), m.group(2)
            if language == "en":
                return f"Property {fur} successfully satisfies requirement {req}"
            elif language == "fr":
                return f"La propriété {fur} satisfait avec succès l'exigence {req}"
                
        # 10) Requirement not met
        m = re.search(r"الخاصية الحالية للـ (.+?) \((.+?)\) لا توفر العزل المطلوب \((.+?)\)", translated_step)
        if m:
            entity, fur, req = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Current property of {entity} ({fur}) does not provide required insulation ({req})"
            elif language == "fr":
                return f"La propriété actuelle de {entity} ({fur}) ne fournit pas l'isolation requise ({req})"
                
        # 11) Adaptation needed
        m = re.search(r"← النتيجة: (.+?) بحاجة إلى عزل حراري \((.+?)\) في (.+?)", translated_step)
        if m:
            entity, req, env = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Result: {entity} needs thermal insulation ({req}) in {env}"
            elif language == "fr":
                return f"Résultat: {entity} a besoin d'isolation thermique ({req}) dans {env}"
                
        # 12) Analogy reasoning start
        m = re.search(r"بدء استدلال التناظر والقياس للـ (.+?) في البيئة (.+?)", translated_step)
        if m:
            entity, env = m.group(1), m.group(2)
            if language == "en":
                return f"Starting analogical transfer for {entity} in environment {env}"
            elif language == "fr":
                return f"Début de l'analogie et du transfert pour {entity} dans l'environnement {env}"
                
        # 13) Candidates
        m = re.search(r"الكائنات البديلة التي تعيش في (.+?): \[(.+?)\]", translated_step)
        if m:
            env, cand_list = m.group(1), m.group(2)
            if language == "en":
                return f"Alternative candidates living in {env}: [{cand_list}]"
            elif language == "fr":
                return f"Candidats alternatifs vivant à/en {env}: [{cand_list}]"
                
        # 14) Jaccard similarity
        m = re.search(r"مقياس التشابه الجاكاردي \(Ancestry Similarity\) بين (.+?) و (.+?) هو (.+?)", translated_step)
        if m:
            e1, e2, sim = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Jaccard similarity index (Ancestry Similarity) between {e1} and {e2} is {sim}"
            elif language == "fr":
                return f"Indice de similitude de Jaccard (Ancestry Similarity) entre {e1} et {e2} est {sim}"
                
        # 15) Best candidate
        m = re.search(r"المرشح الأنسب للقياس هو: (.+?) \(معدل تشابه: (.+?)\)", translated_step)
        if m:
            cand, sim = m.group(1), m.group(2)
            if language == "en":
                return f"Best candidate for analogy is: {cand} (similarity: {sim})"
            elif language == "fr":
                return f"Le meilleur candidat pour l'analogie est: {cand} (similitude: {sim})"
                
        # 16) Transfer action
        m = re.search(r"نقوم بنقل الخاصية (.+?) من (.+?) إلى (.+?) لحل مشكلة البيئة", translated_step)
        if m:
            prop, cand, entity = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Transferring property {prop} from {cand} to {entity} to solve environmental requirement"
            elif language == "fr":
                return f"Transfert de la propriété {prop} depuis {cand} vers {entity} pour résoudre l'exigence environnementale"
                
        # 17) No candidate fallback
        if "لم نجد أي كائن مماثل" in step:
            if language == "en":
                return "Could not find any similar entity living in that environment with the required property for analogical transfer"
            elif language == "fr":
                return "Impossible de trouver un être similaire vivant dans cet environnement avec la propriété requise pour l'analogie"
                
        # 18) Teaching fact
        m = re.search(r"تحليل الجملة الخبرية وإدخالها في العالم النشط '(.+?)'", translated_step)
        if m:
            world = m.group(1)
            if language == "en":
                return f"Parsing declarative sentence and inserting fact into active world '{world}'"
            elif language == "fr":
                return f"Analyse de la phrase déclarative et insertion du fait dans le monde actif '{world}'"
                
        # 19) Sun query
        m = re.search(r"الاستعلام عن شروق الشمس في العالم النشط '(.+?)'", translated_step)
        if m:
            world = m.group(1)
            if language == "en":
                return f"Querying sun rise in active world '{world}'"
            elif language == "fr":
                return f"Requête sur le lever du soleil dans le monde actif '{world}'"
                
        # 20) Sun rises
        m = re.search(r"الشمس تشرق من (.+?) في هذا العالم", translated_step)
        if m:
            target = m.group(1)
            if language == "en":
                return f"The sun rises from {target} in this world"
            elif language == "fr":
                return f"Le soleil se lève à/en {target} dans ce monde"
                
        # 21) Location query
        m = re.search(r"البحث عن موطن (.+?) في العالم '(.+?)'", translated_step)
        if m:
            concept, world = m.group(1), m.group(2)
            if language == "en":
                return f"Searching for habitat of {concept} in world '{world}'"
            elif language == "fr":
                return f"Recherche de l'habitat de {concept} dans le monde '{world}'"
                
        # 22) Location found
        m = re.search(r"← وجدنا أن (.+?) يعيش في (.+?)", translated_step)
        if m:
            concept, location = m.group(1), m.group(2)
            if language == "en":
                return f"Found that {concept} lives in {location}"
            elif language == "fr":
                return f"Trouvé que {concept} vit à/en {location}"
                
        # 23) Comparison trace
        m = re.search(r"مقارنة الخصائص للـ (.+?) والـ (.+?) في العالم النشط '(.+?)'", translated_step)
        if m:
            c1, c2, world = m.group(1), m.group(2), m.group(3)
            if language == "en":
                return f"Comparing properties of {c1} and {c2} in active world '{world}'"
            elif language == "fr":
                return f"Comparaison des propriétés de {c1} et {c2} dans le monde actif '{world}'"
                
        # 24) Unknown query fallback
        if "لم نجد مسار استدلالي" in step:
            if language == "en":
                return "Could not find a clear taxonomic or logical reasoning path matching input words in the knowledge base"
            elif language == "fr":
                return "Aucun chemin de raisonnement taxonomique ou logique clair trouvé dans la base de connaissances pour ces mots"
                
        return translated_step

    def format_trace(self, trace, language):
        """
        Formats reasoning trace in the selected language.
        """
        if not trace:
            return ""
            
        translated_steps = [self.translate_trace_step(step, language) for step in trace]
        
        if language == "ar":
            trace_text = "\n📋 مسار الاستدلال المنطقي والتتبع:\n"
            for idx, step in enumerate(translated_steps):
                trace_text += f"  [{idx + 1}] {step}\n"
        elif language == "en":
            trace_text = "\n📋 Logical Reasoning Trace:\n"
            for idx, step in enumerate(translated_steps):
                trace_text += f"  [{idx + 1}] {step}\n"
        elif language == "fr":
            trace_text = "\n📋 Trace de Raisonnement Logique:\n"
            for idx, step in enumerate(translated_steps):
                trace_text += f"  [{idx + 1}] {step}\n"
        else:
            trace_text = "\n📋 Trace:\n"
            for idx, step in enumerate(translated_steps):
                trace_text += f"  [{idx + 1}] {step}\n"
                
        return trace_text.rstrip()

    def generate_logical_answer(self, res, language):
        """
        Generates core raw answer in target language without persona wrapping.
        """
        type_ = res.get("type", "unknown")
        
        # 1. Classification
        if type_ == "classification":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            
            key = "classification_true" if res["result"] else "classification_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            return template.format(concept1=c1_lbl, concept2=c2_lbl)

        # 2. Location
        elif type_ == "location":
            c_lbl = self.get_concept_label(res["concept"], language)
            loc_lbl = self.get_concept_label(res["location"], language)
            
            template = self.get_template("location", language, self.get_fallback_template("location", language))
            return template.format(concept=c_lbl, location=loc_lbl)

        # 3. Hypothetical
        elif type_ == "hypothetical":
            entity_lbl = self.get_concept_label(res["entity"], language)
            env_lbl = self.get_concept_label(res["environment"], language)
            
            if res["needs_adaptation"]:
                prop_lbl = self.get_concept_label(res["transferred_property"], language)
                cand_lbl = self.get_concept_label(res["analogy_candidate"], language)
                
                template = self.get_template("hypothetical_needs_adaptation", language, self.get_fallback_template("hypothetical_needs_adaptation", language))
                return template.format(
                    entity=entity_lbl,
                    environment=env_lbl,
                    transferred_property=prop_lbl,
                    analogy_candidate=cand_lbl
                )
            else:
                template = self.get_template("hypothetical_no_adaptation", language, self.get_fallback_template("hypothetical_no_adaptation", language))
                return template.format(
                    entity=entity_lbl,
                    environment=env_lbl
                )

        # 4. Comparison
        elif type_ == "comparison":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            
            p1_str = " & ".join([self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "has_property"])
            p2_str = " & ".join([self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "has_property"])
            
            l1 = next((self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "lives_in"), None)
            l2 = next((self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "lives_in"), None)
            
            common = self.find_lowest_common_ancestor(res["concept1"], res["concept2"])
            
            l1_fallback = self.get_template("comparison_lives_in_fallback", language, self.get_fallback_template("comparison_lives_in_fallback", language))
            p1_fallback = self.get_template("comparison_props_fallback_1", language, self.get_fallback_template("comparison_props_fallback_1", language))
            p2_fallback = self.get_template("comparison_props_fallback_2", language, self.get_fallback_template("comparison_props_fallback_2", language))
            common_fallback = self.get_template("comparison_common_fallback", language, self.get_fallback_template("comparison_common_fallback", language))
            
            l1_str = l1 or l1_fallback
            l2_str = l2 or l1_fallback
            p1_formatted = p1_str or p1_fallback
            p2_formatted = p2_str or p2_fallback
            
            common_lbl = self.get_concept_label(common, language) if common else common_fallback
            
            template = self.get_template("comparison", language, self.get_fallback_template("comparison", language))
            return template.format(
                concept1=c1_lbl,
                concept2=c2_lbl,
                l1_str=l1_str,
                l2_str=l2_str,
                p1_formatted=p1_formatted,
                p2_formatted=p2_formatted,
                common_lbl=common_lbl
            )

        # 5. Teaching
        elif type_ == "teaching":
            msg = res.get("message", "")
            status = res.get("status")
            world = res.get("world", "reality")
            
            if language == "ar" and not status:
                return msg
                
            status_keys = {
                "added": "teaching_added",
                "identical": "teaching_identical",
                "auto_replaced": "teaching_auto_replaced",
                "auto_rejected": "teaching_auto_rejected",
                "non_interactive_rejected": "teaching_non_interactive_rejected"
            }
            
            key = status_keys.get(status)
            if key:
                template = self.get_template(key, language, self.get_fallback_template(key, language))
                return template.format(world=world)
            else:
                template = self.get_template("teaching_fallback", language, msg or self.get_fallback_template("teaching_fallback", language))
                return template

        # 6. Anomaly & Exception
        elif type_ == "anomaly":
            entity_lbl = self.get_concept_label(res["entity"], language)
            anomaly_type = res["anomaly_type"]
            reason = res["reason"]
            score = res["anomaly_score"]
            
            template = self.get_template("anomaly", language, self.get_fallback_template("anomaly", language))
            return template.format(
                entity=entity_lbl,
                anomaly_type=anomaly_type,
                reason=reason,
                anomaly_score=score
            )

        # 7. Comparison Scale
        elif type_ == "comparison_scale":
            c1_lbl = self.get_concept_label(res["entity1"], language)
            c2_lbl = self.get_concept_label(res["entity2"], language)
            prop = res["property_name"]
            
            key = "comparison_scale_true" if res["result"] else "comparison_scale_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            return template.format(
                entity1=c1_lbl,
                entity2=c2_lbl,
                property_name=prop
            )

        # 8. Temporal Logic
        elif type_ == "temporal_logic":
            ev = res["event"]
            ref = res["reference"]
            
            key = "temporal_logic_true" if res["result"] else "temporal_logic_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            return template.format(
                event=ev,
                reference=ref
            )

        # 9. Modality
        elif type_ == "modality":
            mod = res["modality"]
            conf = res["modality_confidence"]
            
            key = "modality_true" if res["result"] else "modality_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            return template.format(
                modality=mod,
                modality_confidence=conf
            )

        # 10. Causal Chain
        elif type_ == "causal_chain":
            steps = res["chain"]["steps"]
            chain_str = " -> ".join([f"[{s['event']}]" for s in steps])
            init = res["initial_state"]
            
            template = self.get_template("causal_chain", language, self.get_fallback_template("causal_chain", language))
            return template.format(
                initial_state=init,
                chain_str=chain_str
            )

        # 11. Quantifier
        elif type_ == "quantifier":
            quant = res["quantifier"]
            
            key = "quantifier_true" if res["result"] else "quantifier_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            return template.format(
                quantifier=quant
            )

        # 12. Negation
        elif type_ == "negation":
            key = "negation_true" if res["result"] else "negation_false"
            template = self.get_template(key, language, self.get_fallback_template(key, language))
            return template

        # 13. Semantic Roles
        elif type_ == "semantic_roles":
            pred = res["predicate"]
            roles_list = []
            for r_type, val in res["roles"].items():
                val_lbl = self.get_concept_label(val, language)
                roles_list.append(f"{r_type}: {val_lbl}")
            
            sep = self.get_template("semantic_roles_separator", language, self.get_fallback_template("semantic_roles_separator", language))
            roles_str = sep.join(roles_list)
            
            template = self.get_template("semantic_roles", language, self.get_fallback_template("semantic_roles", language))
            return template.format(
                predicate=pred,
                roles_str=roles_str
            )

        # 14. Describe
        elif type_ == "describe":
            concept_label = res.get("concept_label", self.get_concept_label(res.get("concept", ""), language))
            category = res.get("category", "")
            relations = res.get("relations", [])
            
            parts = []
            if category:
                template_cat = self.get_template("describe_category", language, self.get_fallback_template("describe_category", language))
                parts.append(template_cat.format(concept_label=concept_label, category=category))
            else:
                parts.append(concept_label)
            
            outgoing = [r for r in relations if "target" in r]
            incoming = [r for r in relations if "source" in r]
            
            # De-duplicate relations to prevent repetitive output
            seen_out = set()
            unique_outgoing = []
            for r in outgoing:
                pair = (r.get("relation", ""), r.get("target", ""))
                if pair not in seen_out:
                    seen_out.add(pair)
                    unique_outgoing.append(r)
                    
            seen_in = set()
            unique_incoming = []
            for r in incoming:
                pair = (r.get("relation", ""), r.get("source", ""))
                if pair not in seen_in:
                    seen_in.add(pair)
                    unique_incoming.append(r)
            
            # Map basic relations to display text
            mapped_rel_map = self.get_template("describe_rel_map", language, self.get_fallback_template("describe_rel_map", language))
            if not isinstance(mapped_rel_map, dict):
                mapped_rel_map = {}
            
            for r in unique_outgoing[:5]:
                rel = r.get("relation", "")
                target_lbl = self.get_concept_label(r.get("target", ""), language)
                rel_display = mapped_rel_map.get(rel, rel)
                parts.append(f"{rel_display} {target_lbl}")
                
            for r in unique_incoming[:3]:
                rel = r.get("relation", "")
                src_lbl = self.get_concept_label(r.get("source", ""), language)
                rel_display = mapped_rel_map.get(rel, rel)
                parts.append(f"{src_lbl} {rel_display} {concept_label}")
                
            sep = self.get_template("describe_separator", language, self.get_fallback_template("describe_separator", language))
            body = sep.join(parts)
            return body

        # 15. Knowledge
        elif type_ == "knowledge":
            concept_label = res.get("concept_label", self.get_concept_label(res.get("concept", ""), language))
            outgoing = res.get("outgoing", [])
            incoming = res.get("incoming", [])
            
            # De-deduplicate
            seen_out = set()
            unique_outgoing = []
            for r in outgoing:
                pair = (r.get("relation", ""), r.get("target", ""))
                if pair not in seen_out:
                    seen_out.add(pair)
                    unique_outgoing.append(r)
                    
            seen_in = set()
            unique_incoming = []
            for r in incoming:
                pair = (r.get("relation", ""), r.get("source", ""))
                if pair not in seen_in:
                    seen_in.add(pair)
                    unique_incoming.append(r)
            
            template_header = self.get_template("knowledge_header", language, self.get_fallback_template("knowledge_header", language))
            parts = [template_header.format(concept_label=concept_label)]
                
            for r in unique_outgoing[:5]:
                target_lbl = self.get_concept_label(r.get("target", ""), language)
                parts.append(f"{concept_label} {r.get('relation', '')} {target_lbl}")
            for r in unique_incoming[:3]:
                src_lbl = self.get_concept_label(r.get("source", ""), language)
                parts.append(f"{src_lbl} {r.get('relation', '')} {concept_label}")
                
            sep = self.get_template("knowledge_separator", language, self.get_fallback_template("knowledge_separator", language))
            body = sep.join(parts)
            return body

        # 15.5. Causal Reasoning
        elif type_ == "causal_reasoning":
            reason = res.get("reason", "")
            return reason

        # 16. Unknown fail-safe
        else:
            template = self.get_template("unknown", language, self.get_fallback_template("unknown", language))
            return template
            
        return ""



    def render_response(self, logical_response, persona_id, language, context):
        """
        Renders the final response with the selected persona and language rules.
        """
        persona = self.personas.get(persona_id)
        if not persona:
            # Fallback to simple formatting if persona not found
            answer = self.generate_logical_answer(logical_response, language)
            details = self.format_trace(logical_response.get("trace", []), language)
            if details:
                return f"{answer}\n{details}"
            return answer
            
        variant = persona["versions"].get(language)
        if not variant:
            # Fallback to default language if selected language not supported
            variant = persona["versions"].get("ar")
            language = "ar"
            
        # 1. Select greeting
        greeting = self.select_expression(variant["expressions"]["greeting"], context)
        
        # 2. Select introduction based on confidence
        confidence = logical_response.get("confidence", 1.0)
        if confidence > 0.8:
            intro = self.select_expression(variant["expressions"]["explanation_intro"], context)
        else:
            intro = self.select_expression(variant["expressions"]["uncertainty"], context)
            
        # 3. Generate raw logical answer
        answer = self.generate_logical_answer(logical_response, language)
        
        # 4. Format tracing details
        if variant.get("use_reasoning_chain") or logical_response.get("type") in ["classification", "hypothetical", "location", "comparison", "causal_reasoning"]:
            details = self.format_trace(logical_response.get("trace", []), language)
        else:
            details = ""
            
        # 5. Select ending
        ending = self.select_expression(variant["expressions"]["ending"], context)
        
        # 6. Style markers (e.g. style fillers)
        p_ref = random.choice(variant.get("style_markers", [""])) if variant.get("style_markers") else ""
        
        # Assemble based on type
        resp_type = logical_response.get("type", "unknown")
        
        if resp_type == "teaching":
            # For system teaching feedback, make it short but styled by the persona marker
            if p_ref:
                if language == "ar":
                    full_response = f"{p_ref}، {answer}"
                else:
                    full_response = f"{p_ref.capitalize()}, {answer}"
            else:
                full_response = answer
        elif resp_type == "unknown":
            # For unknown, use uncertainty intro
            if language == "ar":
                full_response = f"{greeting}\n{intro}\n{ending}"
            else:
                full_response = f"{greeting},\n{intro}\n{ending}"
        else:
            # Standard answer
            if language == "ar":
                full_response = f"{greeting}\n\n{intro} {answer}\n{details}\n\n{ending}"
            else:
                full_response = f"{greeting},\n\n{intro} {answer}\n{details}\n\n{ending}"
                
        # Clean up double linebreaks or spacing issues
        full_response = re.sub(r'\n{3,}', '\n\n', full_response)
        return full_response.strip()
