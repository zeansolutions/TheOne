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

    def translate_concept_word(self, word, language):
        if not word:
            return word
        # Try to find concept_id in Arabic lexicon
        ar_rules = self.handler.language_rules.get("ar", {})
        ar_lexicon = ar_rules.get("lexicon", {})
        
        # Clean word from prefixes for lookup
        lookup_word = word
        for pref in ["ال", "ل", "ب", "ف", "و"]:
            if lookup_word.startswith(pref) and len(lookup_word) > len(pref):
                stripped = lookup_word[len(pref):]
                if stripped in ar_lexicon:
                    lookup_word = stripped
                    break
                    
        concept_id = ar_lexicon.get(lookup_word)
        if not concept_id:
            # Check other lexicons or direct graph nodes
            for node, ndata in self.handler.graph.nodes(data=True):
                if word in ndata.get("labels", []) or node == word:
                    concept_id = node
                    break
        
        if concept_id:
            return self.get_concept_label(concept_id, language)
        return word

    def translate_rule_description_text(self, text, language):
        if not text:
            return text
            
        rule_desc_map = {
            "ar": {
                "إذا كان ?x هو تصنيف فرعي من ?y، و ?y هو تصنيف فرعي من ?z، إذن ?x هو تصنيف فرعي من ?z.": "إذا كان ?x هو تصنيف فرعي من ?y، و ?y هو تصنيف فرعي من ?z، إذن ?x هو تصنيف فرعي من ?z.",
                "يرث الكائن ?x الخاصية ?p من فئته الأعلى ?y.": "يرث الكائن ?x الخاصية ?p من فئته الأعلى ?y.",
                "إذا كان الكائن ?x يعيش في بيئة ?env تشتمل على ظرف ?cond يتطلب ?req، إذن ?x يتطلب ?req.": "إذا كان الكائن ?x يعيش في بيئة ?env تشتمل على ظرف ?cond يتطلب ?req، إذن ?x يتطلب ?req.",
                "إذا كان النجم يصدر نوراً يضيء طريقاً يؤدي إلى وجهة معينة، واتبع الشخص هذا النور، فإنه يصل إلى وجهته بأمان.": "إذا كان النجم يصدر نوراً يضيء طريقاً يؤدي إلى وجهة معينة، واتبع الشخص هذا النور، فإنه يصل إلى وجهته بأمان.",
                "مساعدة الآخرين تدخل الفرح على قلب الفاعل.": "مساعدة الآخرين تدخل الفرح على قلب الفاعل.",
                "إدراك الكائن لقيمة الخير يجعله حكيماً.": "إدراك الكائن لقيمة الخير يجعله حكيماً."
            },
            "en": {
                "إذا كان ?x هو تصنيف فرعي من ?y، و ?y هو تصنيف فرعي من ?z، إذن ?x هو تصنيف فرعي من ?z.": "If ?x is a subcategory of ?y, and ?y is a subcategory of ?z, then ?x is a subcategory of ?z.",
                "يرث الكائن ?x الخاصية ?p من فئته الأعلى ?y.": "The object ?x inherits property ?p from its superclass ?y.",
                "إذا كان الكائن ?x يعيش في بيئة ?env تشتمل على ظرف ?cond يتطلب ?req، إذن ?x يتطلب ?req.": "If object ?x lives in environment ?env which has condition ?cond requiring ?req, then ?x requires ?req.",
                "إذا كان النجم يصدر نوراً يضيء طريقاً يؤدي إلى وجهة معينة، واتبع الشخص هذا النور، فإنه يصل إلى وجهته بأمان.": "If a star emits light that illuminates a road leading to a destination, and a person follows this light, they safely reach their destination.",
                "مساعدة الآخرين تدخل الفرح على قلب الفاعل.": "Helping others brings joy to the helper's heart.",
                "إدراك الكائن لقيمة الخير يجعله حكيماً.": "Realizing the value of goodness makes an entity wise."
            },
            "fr": {
                "إذا كان ?x هو تصنيف فرعي من ?y، و ?y هو تصنيف فرعي من ?z، إذن ?x هو تصنيف فرعي من ?z.": "Si ?x est une sous-catégorie de ?y, et ?y est une sous-catégorie de ?z, alors ?x est une sous-catégorie de ?z.",
                "يرث الكائن ?x الخاصية ?p من فئته الأعلى ?y.": "L'objet ?x hérite de la propriété ?p de sa superclasse ?y.",
                "إذا كان الكائن ?x يعيش في بيئة ?env تشتمل على ظرف ?cond يتطلب ?req، إذن ?x يتطلب ?req.": "Si l'objet ?x vit dans l'environnement ?env qui a la condition ?cond nécessitant ?req, alors ?x a besoin de ?req.",
                "إذا كان النجم يصدر نوراً يضيء طريقاً يؤدي إلى وجهة معينة، واتبع الشخص هذا النور، فإنه يصل إلى وجهته بأمان.": "Si une étoile émet de la lumière qui éclaire un chemin menant à une destination, et qu'une personne suit cette lumière, elle atteint sa destination en toute sécurité.",
                "مساعدة الآخرين تدخل الفرح على قلب الفاعل.": "Aider les autres apporte de la joie au cœur de l'aidant.",
                "إدراك الكائن لقيمة الخير يجعله حكيماً.": "Réaliser la valeur du bien rend une entité sage."
            }
        }
        cleaned_text = text.strip()
        trans = rule_desc_map.get(language, {}).get(cleaned_text)
        if trans:
            return trans
        return text

    def translate_trace_step(self, step, language):
        """
        Translates a single trace step from Arabic to English or French, replacing concept IDs as well.
        """
        if language == "ar":
            return step
            
        words = re.findall(r"\w+", step)
        translated_step = step
        for w in words:
            if self.handler.graph.has_node(w) or w in ["thin_fur", "thick_fur", "savanna", "arctic", "c_sun", "c_east", "c_west", "c_underground", "feline_carnivore", "polar_bear", "animal", "carnivore"]:
                translated_lbl = self.get_concept_label(w, language)
                translated_step = re.sub(r"\b" + w + r"\b", translated_lbl, translated_step)
                
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

        # --- ADDITIONAL MULTILINGUAL TRANSLATIONS ---
        # A1) Checking type compatibility
        m = re.search(r"التحقق من تطابق النوع لـ '(.+?)' و '(.+?)'", translated_step)
        if m:
            c1 = self.translate_concept_word(m.group(1), language)
            c2 = self.translate_concept_word(m.group(2), language)
            if language == "en":
                return f"Checking type compatibility for '{c1}' and '{c2}'"
            elif language == "fr":
                return f"Vérification de la compatibilité des types pour '{c1}' et '{c2}'"

        # A2) Both belong to same category
        m = re.search(r"كلا المفهومين ينتميان لنفس الفئة العامة \[(.+?)\]", translated_step)
        if m:
            cat = self.translate_concept_word(m.group(1), language)
            if language == "en":
                return f"Both concepts belong to the same general category [{cat}]"
            elif language == "fr":
                return f"Les deux concepts appartiennent à la même catégorie générale [{cat}]"

        # A3) Both share direct subcategory
        m = re.search(r"كلا المفهومين يشتركان في التصنيف الفرعي المباشر \[(.+?)\]", translated_step)
        if m:
            parent = self.translate_concept_word(m.group(1), language)
            if language == "en":
                return f"Both concepts share the direct subcategory [{parent}]"
            elif language == "fr":
                return f"Les deux concepts partagent la sous-catégorie directe [{parent}]"

        # A4) No common ancestor
        if "لا يوجد فئة عامة مشتركة أو سلف تصنيفي مباشر يربط بين المفهومين" in translated_step:
            if language == "en":
                return "No common general category or direct taxonomic ancestor connects the two concepts"
            elif language == "fr":
                return "Aucune catégorie générale commune ou ancêtre taxonomique direct ne relie les deux concepts"

        # A5) Taxonomic relation query
        m = re.search(r"استعلام علاقة تصنيفية بين '(.+?)' و '(.+?)'", translated_step)
        if m:
            c1 = self.translate_concept_word(m.group(1), language)
            c2 = self.translate_concept_word(m.group(2), language)
            if language == "en":
                return f"Taxonomic relation query between '{c1}' and '{c2}'"
            elif language == "fr":
                return f"Requête de relation taxonomique entre '{c1}' et '{c2}'"

        # A6) Relation is prohibited
        m = re.search(r"العلاقة محظورة: \[(.+?)\] --\((.+?)\)--> \[(.+?)\]", translated_step)
        if m:
            u = self.translate_concept_word(m.group(1), language)
            rel = m.group(2)
            v = self.translate_concept_word(m.group(3), language)
            rel_trans = self.translate_concept_word(rel, language)
            if language == "en":
                return f"Relation is prohibited: [{u}] --({rel_trans})--> [{v}]"
            elif language == "fr":
                return f"Relation interdite: [{u}] --({rel_trans})--> [{v}]"

        # A7) Logical relation found
        m = re.search(r"تم العثور على علاقة منطقية: \[(.+?)\] --\((.+?)\)--> \[(.+?)\]", translated_step)
        if m:
            u = self.translate_concept_word(m.group(1), language)
            rel = m.group(2)
            v = self.translate_concept_word(m.group(3), language)
            rel_trans = self.translate_concept_word(rel, language)
            if language == "en":
                return f"Logical relation found: [{u}] --({rel_trans})--> [{v}]"
            elif language == "fr":
                return f"Relation logique trouvée: [{u}] --({rel_trans})--> [{v}]"

        # A8) No relation/rule connects
        if "لا يوجد علاقة تصنيفية أو حكم منطقي يربط بين المفهومين في قاعدة المعرفة" in translated_step:
            if language == "en":
                return "No taxonomic relation or logical rule connects the two concepts in the knowledge base"
            elif language == "fr":
                return "Aucune relation taxonomique ou règle logique ne relie les deux concepts dans la base de connaissances"

        # A9) Parse causal query
        m = re.search(r"Parse: تحليل الاستعلام السببي '(.+?)'", translated_step)
        if m:
            part = m.group(1)
            if language == "en":
                return f"Parse: Causal query analysis '{part}'"
            elif language == "fr":
                return f"Parse: Analyse de la requête causale '{part}'"

        # A10) Extract variables
        m = re.search(r"Extract: subject=(.+?) \((.+?)\), relation=(.+?), target=(.+?) \((.+?)\)", translated_step)
        if m:
            sub_lbl = self.translate_concept_word(m.group(1), language)
            sub = m.group(2)
            rel = m.group(3)
            obj_lbl = self.translate_concept_word(m.group(4), language)
            obj = m.group(5)
            rel_trans = self.translate_concept_word(rel, language)
            if language == "en":
                return f"Extract: subject={sub_lbl} ({sub}), relation={rel_trans}, target={obj_lbl} ({obj})"
            elif language == "fr":
                return f"Extract: sujet={sub_lbl} ({sub}), relation={rel_trans}, cible={obj_lbl} ({obj})"

        # A11) Search direct facts
        if "Search Direct Facts: لم يتم العثور عليها كحقيقة مباشرة" in translated_step:
            if language == "en":
                return "Search Direct Facts: Not found as a direct fact"
            elif language == "fr":
                return "Search Direct Facts: Non trouvé comme un fait direct"

        # A12) Apply rules
        m = re.search(r"Apply Rules: تم تطبيق قاعدة الاستدلال '(.+?)'", translated_step)
        if m:
            rule_id = m.group(1)
            if language == "en":
                return f"Apply Rules: Inference rule '{rule_id}' applied"
            elif language == "fr":
                return f"Apply Rules: Règle d'inférence '{rule_id}' appliquée"

        # A13) Condition matched
        if "Condition: مطابقة شروط القاعدة بنجاح" in translated_step:
            if language == "en":
                return "Condition: Rule conditions matched successfully"
            elif language == "fr":
                return "Condition: Conditions de la règle validées avec succès"

        # A14) Conclusion
        m = re.search(r"Conclusion: استنتاج \[(.+?)\] --\((.+?)\)--> \[(.+?)\] \(ثقة: (.+?)\)", translated_step)
        if m:
            sub = self.translate_concept_word(m.group(1), language)
            rel = m.group(2)
            obj = self.translate_concept_word(m.group(3), language)
            conf = m.group(4)
            rel_trans = self.translate_concept_word(rel, language)
            if language == "en":
                return f"Conclusion: Inferring [{sub}] --({rel_trans})--> [{obj}] (confidence: {conf})"
            elif language == "fr":
                return f"Conclusion: Déduction [{sub}] --({rel_trans})--> [{obj}] (confiance: {conf})"

        # A15) Result: "Result: rule_desc"
        m = re.search(r"Result: (.+)", translated_step)
        if m:
            desc = m.group(1)
            desc_trans = self.translate_rule_description_text(desc, language)
            return f"Result: {desc_trans}"

        # A16) Relation path query
        m = re.search(r"استعلام علاقات (.+?) بين '(.+?)' و '(.+?)'", translated_step)
        if m:
            mode = m.group(1)
            c1 = self.translate_concept_word(m.group(2), language)
            c2 = self.translate_concept_word(m.group(3), language)
            mode_trans = "deep" if mode == "عميق" else "specific"
            if language == "fr":
                mode_trans = "profond" if mode == "عميق" else "spécifique"
            if language == "en":
                return f"Relation path query ({mode_trans}) between '{c1}' and '{c2}'"
            elif language == "fr":
                return f"Requête de chemin de relation ({mode_trans}) entre '{c1}' et '{c2}'"

        # A17) Path found
        m = re.search(r"تم العثور على مسار يربط بين المفهومين يتكون من (\d+) عقدة", translated_step)
        if m:
            n = m.group(1)
            if language == "en":
                return f"Found a path connecting the two concepts consisting of {n} nodes"
            elif language == "fr":
                return f"Trouvé un chemin reliant les deux concepts composé de {n} nœuds"

        # A18) No path found
        if "لم يتم العثور على روابط متصلة" in translated_step:
            if language == "en":
                return "No connecting links found"
            elif language == "fr":
                return "Aucun lien de connexion trouvé"

        # A19) Describe query
        m = re.search(r"استعلام وصفي عن المفهوم '(.+?)' \((.+?)\)", translated_step)
        if m:
            lbl = self.translate_concept_word(m.group(1), language)
            concept = m.group(2)
            if language == "en":
                return f"Descriptive query for concept '{lbl}' ({concept})"
            elif language == "fr":
                return f"Requête descriptive pour le concept '{lbl}' ({concept})"

        # A20) Relations found
        m = re.search(r"تم العثور على (\d+) علاقة مرتبطة", translated_step)
        if m:
            n = m.group(1)
            if language == "en":
                return f"Found {n} related relations"
            elif language == "fr":
                return f"Trouvé {n} relations associées"

        # A21) General knowledge query
        m = re.search(r"استعلام عام عن المعرفة المتوفرة حول '(.+?)'", translated_step)
        if m:
            lbl = self.translate_concept_word(m.group(1), language)
            if language == "en":
                return f"General query about available knowledge for '{lbl}'"
            elif language == "fr":
                return f"Requête générale sur les connaissances disponibles pour '{lbl}'"

        # A22) Outgoing/incoming counts
        m = re.search(r"← علاقات صادرة: (\d+), علاقات واردة: (\d+)", translated_step)
        if m:
            out_c = m.group(1)
            in_c = m.group(2)
            if language == "en":
                return f"<- Outgoing relations: {out_c}, Incoming relations: {in_c}"
            elif language == "fr":
                return f"<- Relations sortantes: {out_c}, Relations entrantes: {in_c}"

        # A23) Sandbox entrance
        m = re.search(r"\[SANDBOX\] دخول عالم الافتراض للسيناريو: '(.+?)'", translated_step)
        if m:
            premise = m.group(1)
            if language == "en":
                return f"[SANDBOX] Entering hypothetical world for scenario: '{premise}'"
            elif language == "fr":
                return f"[SANDBOX] Entrée dans le monde hypothétique pour le scénario: '{premise}'"

        # A24) Sandbox clone graph
        if "[SANDBOX] استنساخ الرسم البياني المعرفي بأكمله بشكل آمن" in translated_step:
            if language == "en":
                return "[SANDBOX] Safely cloning the entire knowledge graph"
            elif language == "fr":
                return "[SANDBOX] Clonage sécurisé de l'ensemble du graphe de connaissances"

        # A25) Sandbox add fact
        m = re.search(r"\[SANDBOX\] إضافة حقيقة افتراضية مؤقتة: (.+)", translated_step)
        if m:
            msg = m.group(1)
            if language == "en":
                return f"[SANDBOX] Adding temporary hypothetical fact: {msg}"
            elif language == "fr":
                return f"[SANDBOX] Ajout d'un fait hypothétique temporaire: {msg}"

        # A26) Sandbox cannot teach
        m = re.search(r"\[SANDBOX\] لم نتمكن من تلقين الفرضية الافتراضية بشكل كامل: (.+)", translated_step)
        if m:
            premise = m.group(1)
            if language == "en":
                return f"[SANDBOX] Could not fully teach hypothetical premise: {premise}"
            elif language == "fr":
                return f"[SANDBOX] Impossible d'enseigner pleinement la prémisse hypothétique: {premise}"

        # A27) Sandbox run analogical reasoning
        if "[SANDBOX] تشغيل الاستدلال الاستنتاجي التناظري..." in translated_step:
            if language == "en":
                return "[SANDBOX] Running analogical deductive reasoning..."
            elif language == "fr":
                return "[SANDBOX] Exécution du raisonnement déductif analogique..."

        # A28) Sandbox exit
        if "[SANDBOX] الخروج من عالم الافتراض واستعادة الرسم البياني الأصلي بأمان" in translated_step:
            if language == "en":
                return "[SANDBOX] Exiting hypothetical world and safely restoring original graph"
            elif language == "fr":
                return "[SANDBOX] Sortie du monde hypothétique et restauration sécurisée du graphe original"

        # A29) Conflict trace
        m = re.search(r"تعارض في العوالم للمفهوم \[(.+?)\]: في عالم '(.+?)' هو \[(.+?)\],? بينما في عالم '(.+?)' هو \[(.+?)\]", translated_step)
        if m:
            concept = self.translate_concept_word(m.group(1), language)
            w1 = m.group(2)
            val1 = self.translate_concept_word(m.group(3), language)
            w2 = m.group(4)
            val2 = self.translate_concept_word(m.group(5), language)
            if language == "en":
                return f"World conflict for concept [{concept}]: in world '{w1}' it is [{val1}], while in world '{w2}' it is [{val2}]"
            elif language == "fr":
                return f"Conflit de mondes pour le concept [{concept}]: dans le monde '{w1}' il est [{val1}], alors que dans le monde '{w2}' il est [{val2}]"

        # A30) Modality
        m = re.search(r"الاستدلال الموجه بالجهة \(Modality\): الحالة المكتشفة هي '(.+?)' وثقتها (.+)", translated_step)
        if m:
            mod = m.group(1)
            conf = m.group(2)
            if language == "en":
                return f"Modality reasoning: detected mode is '{mod}' with confidence {conf}"
            elif language == "fr":
                return f"Raisonnement de modalité: le mode détecté est '{mod}' avec une confiance de {conf}"

        # A31) Quantifiers
        m = re.search(r"الاستدلال بسور القضية \(Quantifiers\): السور المكتشف هو '(.+?)'", translated_step)
        if m:
            quant = m.group(1)
            if language == "en":
                return f"Quantifier reasoning: detected quantifier is '{quant}'"
            elif language == "fr":
                return f"Raisonnement de quantificateurs: le quantificateur détecté est '{quant}'"

        # A32) Negation
        if "الاستدلال بالنفي والتقابل (Negation): تم تطبيق قاعدة نفي النفي وعكس القطبية" in translated_step:
            if language == "en":
                return "Negation reasoning: applied double negation and polarity inversion rules"
            elif language == "fr":
                return "Raisonnement de négation: application de la double négation et de l'inversion de polarité"

        # A33) Semantic Roles
        m = re.search(r"تحليل الأدوار الدلالية \(Semantic Roles\): استخلاص أدوار الفعل '(.+?)'", translated_step)
        if m:
            pred = m.group(1)
            if language == "en":
                return f"Semantic roles analysis: extracting roles for predicate '{pred}'"
            elif language == "fr":
                return f"Analyse des rôles sémantiques: extraction des rôles pour le prédicat '{pred}'"

        # A34) Causal Chain start
        m = re.search(r"الاستدلال السببي متعدد الخطوات \(Causal Chain\): بدءاً من (.+)", translated_step)
        if m:
            concept = self.translate_concept_word(m.group(1), language)
            if language == "en":
                return f"Multi-step causal reasoning (Causal Chain): starting from {concept}"
            elif language == "fr":
                return f"Raisonnement causal multi-étapes (Causal Chain): à partir de {concept}"

        # A35) Causal Chain step
        m = re.search(r"الخطوة (\d+): الحدث (.+)", translated_step)
        if m:
            step_num = m.group(1)
            event = self.translate_concept_word(m.group(2), language)
            if language == "en":
                return f"Step {step_num}: Event {event}"
            elif language == "fr":
                return f"Étape {step_num}: Événement {event}"

        # A36) Temporal check order
        m = re.search(r"الاستدلال الزمني: التحقق من الترتيب الزمني للحدث (.+)", translated_step)
        if m:
            event = self.translate_concept_word(m.group(1), language)
            if language == "en":
                return f"Temporal reasoning: verifying temporal order for event {event}"
            elif language == "fr":
                return f"Raisonnement temporel: vérification de l'ordre temporel pour l'événement {event}"

        # A37) Temporal logic fact
        m = re.search(r"الحدث (.+?) يقع (.+?) present بالتعدي الزمني", translated_step)
        if m:
            event = self.translate_concept_word(m.group(1), language)
            rel = m.group(2)
            rel_trans = "before" if rel == "قبل" else "not before"
            if language == "fr":
                rel_trans = "avant" if rel == "قبل" else "pas avant"
            if language == "en":
                return f"Event {event} occurs {rel_trans} present by temporal transitivity"
            elif language == "fr":
                return f"L'événement {event} se produit {rel_trans} present par transitivité temporelle"

        # A38) Check property
        m = re.search(r"فحص الخاصية (.+?) للـ (.+)", translated_step)
        if m:
            prop = self.translate_concept_word(m.group(1), language)
            entity = self.translate_concept_word(m.group(2), language)
            if language == "en":
                return f"Checking property {prop} for {entity}"
            elif language == "fr":
                return f"Vérification de la propriété {prop} pour {entity}"

        # A39) Compare on scale
        m = re.search(r"مقارنة الكائنات على مقياس (.+)", translated_step)
        if m:
            prop = m.group(1)
            prop_trans = self.translate_concept_word(prop, language)
            if language == "en":
                return f"Comparing entities on {prop_trans} scale"
            elif language == "fr":
                return f"Comparaison des entités sur l'échelle de {prop_trans}"

        # A40) Anomaly check exceptions
        m = re.search(r"كشف الشذوذ: البحث عن استثناءات للـ (.+)", translated_step)
        if m:
            entity = self.translate_concept_word(m.group(1), language)
            if language == "en":
                return f"Anomaly detection: searching exceptions for {entity}"
            elif language == "fr":
                return f"Détection d'anomalies: recherche d'exceptions pour {entity}"

        # A41) Anomaly exception found
        m = re.search(r"العثور على استثناء: (.+)", translated_step)
        if m:
            exc = m.group(1)
            if language == "en":
                return f"Exception found: {exc}"
            elif language == "fr":
                return f"Exception trouvée: {exc}"
                
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
            return self.translate_rule_description_text(reason, language)

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
