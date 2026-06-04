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
            
    def get_template(self, key, language, default):
        """
        Retrieves a sentence/phrase template from the language rules database.
        Falls back to a default if not found in the database.
        """
        lang_rules = self.handler.language_rules.get(language, {})
        templates = lang_rules.get("templates", {})
        return templates.get(key, default)

    def get_concept_label(self, concept_id, language):
        """
        Translates a concept ID into the target language label.
        """
        # 1. Try fallbacks for common concepts first (to guarantee correct baseline translation)
        fallbacks = {
            "en": {
                "feline_carnivore": "lion",
                "polar_bear": "polar bear",
                "animal": "animal",
                "carnivore": "predator",
                "savanna": "savanna",
                "arctic": "arctic",
                "thin_fur": "thin fur",
                "thick_fur": "thick fur",
                "meat": "meat",
                "c_sun": "sun",
                "c_east": "east",
                "c_west": "west",
                "c_underground": "underground"
            },
            "fr": {
                "feline_carnivore": "lion",
                "polar_bear": "ours polaire",
                "animal": "animal",
                "carnivore": "prédateur",
                "savanna": "savane",
                "arctic": "arctique",
                "thin_fur": "fourrure légère",
                "thick_fur": "fourrure épaisse",
                "meat": "viande",
                "c_sun": "soleil",
                "c_east": "est",
                "c_west": "ouest",
                "c_underground": "sous-sol"
            },
            "ar": {
                "feline_carnivore": "أسد",
                "polar_bear": "دب قطبي",
                "animal": "حيوان",
                "carnivore": "مفترس",
                "savanna": "سافانا",
                "arctic": "قطب",
                "thin_fur": "فراء خفيف",
                "thick_fur": "فراء سميك",
                "meat": "لحم",
                "c_sun": "الشمس",
                "c_east": "الشرق",
                "c_west": "الغرب",
                "c_underground": "تحت الأرض"
            }
        }
        
        fallback_map = fallbacks.get(language, {})
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
            return template.format(concept1=c1_lbl, concept2=c2_lbl)

        # 2. Location
        elif type_ == "location":
            c_lbl = self.get_concept_label(res["concept"], language)
            loc_lbl = self.get_concept_label(res["location"], language)
            
            default_val = {
                "ar": "{concept} بيعيش في {location}.",
                "en": "{concept} lives in the {location}.",
                "fr": "{concept} vit dans la {location}."
            }.get(language, "")
            
            template = self.get_template("location", language, default_val)
            return template.format(concept=c_lbl, location=loc_lbl)

        # 3. Hypothetical
        elif type_ == "hypothetical":
            entity_lbl = self.get_concept_label(res["entity"], language)
            env_lbl = self.get_concept_label(res["environment"], language)
            
            if res["needs_adaptation"]:
                prop_lbl = self.get_concept_label(res["transferred_property"], language)
                cand_lbl = self.get_concept_label(res["analogy_candidate"], language)
                
                default_val = {
                    "ar": (
                        "لو {entity} عاش في {environment}، "
                        "أكيد محتاج يتكيف! البيئة هناك تفرض متطلبات خاصة، "
                        "عشان كدة هيحتاج يطور {transferred_property} بالقياس والتناظر مع {analogy_candidate} "
                        "اللي بيعيش هناك بالفعل عشان يتكيف مع بيئته الجديدة."
                    ),
                    "en": (
                        "if a {entity} lived in the {environment}, "
                        "it would definitely need to adapt! The environment there imposes specific requirements, "
                        "which is why it would need to develop {transferred_property} based on analogy with {analogy_candidate} "
                        "that lives there to adapt to its new environment."
                    ),
                    "fr": (
                        "si un {entity} vivait dans l'{environment}, "
                        "il aurait certainement besoin de s'adapter! L'environnement y impose des exigences spécifiques, "
                        "c'est pourquoi il devrait développer une {transferred_property} par analogie avec {analogy_candidate} "
                        "qui y vit déjà pour s'adapter à son nouvel environnement."
                    )
                }.get(language, "")
                
                template = self.get_template("hypothetical_needs_adaptation", language, default_val)
                return template.format(
                    entity=entity_lbl,
                    environment=env_lbl,
                    transferred_property=prop_lbl,
                    analogy_candidate=cand_lbl
                )
            else:
                default_val = {
                    "ar": "لو {entity} عاش في {environment} مش محتاج يغير صفاته الجسدية لأنه مهيأ ليها بالفعل.",
                    "en": "if a {entity} lived in the {environment}, it would not need to change its physical properties because it is already suited for it.",
                    "fr": "si un {entity} vivait dans l'{environment}, il n'aurait pas besoin de modifier ses propriétés physiques car il y est déjà adapté."
                }.get(language, "")
                
                template = self.get_template("hypothetical_no_adaptation", language, default_val)
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
            
            l1_fallback = self.get_template("comparison_lives_in_fallback", language, "its environment" if language == "en" else ("son environnement" if language == "fr" else "بيئته"))
            p1_fallback = self.get_template("comparison_props_fallback_1", language, "properties optimized for its environment" if language == "en" else ("des propriétés optimisées pour son environnement" if language == "fr" else "صفات مخصصة لبيئته"))
            p2_fallback = self.get_template("comparison_props_fallback_2", language, "properties suited for the cold" if language == "en" else ("des propriétés adaptées au froid" if language == "fr" else "صفات تناسب البرودة"))
            common_fallback = self.get_template("comparison_common_fallback", language, "entities" if language == "en" else ("entités" if language == "fr" else "كائنات"))
            
            l1_str = l1 or l1_fallback
            l2_str = l2 or l1_fallback
            p1_formatted = p1_str or p1_fallback
            p2_formatted = p2_str or p2_fallback
            
            common_lbl = self.get_concept_label(common, language) if common else common_fallback
            
            default_val = {
                "ar": (
                    "الفرق واضح جداً بين {concept1} و {concept2}: "
                    "أولاً، {concept1} بيعيش في {l1_str} وعنده {p1_formatted}. "
                    "أما {concept2} فبيعيش في {l2_str} وعنده {p2_formatted}. "
                    "لكن التشابه الجوهري أن كلاهما {common_lbl} تصنيفياً."
                ),
                "en": (
                    "The difference is very clear between {concept1} and {concept2}: "
                    "first, {concept1} lives in {l1_str} and has {p1_formatted}. "
                    "On the other hand, {concept2} lives in {l2_str} and has {p2_formatted}. "
                    "However, the core similarity is that both are taxonomically {common_lbl}."
                ),
                "fr": (
                    "La différence est très claire entre {concept1} et {concept2}: "
                    "premièrement, {concept1} vit dans {l1_str} et a {p1_formatted}. "
                    "D'un autre côté, {concept2} vit dans {l2_str} et a {p2_formatted}. "
                    "Cependant, la similitude fondamentale est que les deux sont taxonomiquement des {common_lbl}."
                )
            }.get(language, "")
            
            template = self.get_template("comparison", language, default_val)
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
                return template.format(world=world)
            else:
                default_fallback = {
                    "en": "Fact operation finished.",
                    "fr": "Opération sur le fait terminée.",
                    "ar": "تم إنهاء عملية معالجة الحقيقة."
                }.get(language, "Fact operation finished.")
                
                template = self.get_template("teaching_fallback", language, msg or default_fallback)
                return template

        # 6. Anomaly & Exception
        elif type_ == "anomaly":
            entity_lbl = self.get_concept_label(res["entity"], language)
            anomaly_type = res["anomaly_type"]
            reason = res["reason"]
            score = res["anomaly_score"]
            
            default_val = {
                "en": "An anomaly detected for {entity}: condition is {anomaly_type} due to {reason} (anomaly score: {anomaly_score:.2f}).",
                "fr": "Une anomalie détectée pour {entity}: état {anomaly_type} dû à {reason} (score d'anomalie: {anomaly_score:.2f}).",
                "ar": "تم رصد استثناء وشذوذ عن القاعدة للـ {entity}: الحالة هي {anomaly_type} والسبب هو {reason} (معدل الشذوذ {anomaly_score:.2f})."
            }.get(language, "")
            
            template = self.get_template("anomaly", language, default_val)
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
            return template.format(
                event=ev,
                reference=ref
            )

        # 9. Modality
        elif type_ == "modality":
            mod = res["modality"]
            conf = res["modality_confidence"]
            
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
            return template.format(
                modality=mod,
                modality_confidence=conf
            )

        # 10. Causal Chain
        elif type_ == "causal_chain":
            steps = res["chain"]["steps"]
            chain_str = " -> ".join([f"[{s['event']}]" for s in steps])
            init = res["initial_state"]
            
            default_val = {
                "en": "The multi-step causal chain starting from [{initial_state}] is: {chain_str}.",
                "fr": "La chaîne causale à plusieurs étapes à partir de [{initial_state}] est: {chain_str}.",
                "ar": "التسلسل السببي متعدد الخطوات بدءاً من [{initial_state}] هو: {chain_str}."
            }.get(language, "")
            
            template = self.get_template("causal_chain", language, default_val)
            return template.format(
                initial_state=init,
                chain_str=chain_str
            )

        # 11. Quantifier
        elif type_ == "quantifier":
            quant = res["quantifier"]
            
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
            return template.format(
                quantifier=quant
            )

        # 12. Negation
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
            return template

        # 13. Semantic Roles
        elif type_ == "semantic_roles":
            pred = res["predicate"]
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
                default_cat = {
                    "en": "{concept_label} is a concept of type ({category})",
                    "fr": "{concept_label} est un concept de type ({category})",
                    "ar": "{concept_label} هو مفهوم من نوع ({category})"
                }.get(language, "")
                template_cat = self.get_template("describe_category", language, default_cat)
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
            default_rel_map = {
                "ar": {"is_a": "هو", "lives_in": "يعيش في", "has_property": "لديه صفة", "part_of": "جزء من", "rises_from": "يشرق من"},
                "en": {"is_a": "is a", "lives_in": "lives in", "has_property": "has property", "part_of": "part of", "rises_from": "rises from"},
                "fr": {"is_a": "est un", "lives_in": "vit dans", "has_property": "a la propriété", "part_of": "fait partie de", "rises_from": "se lève à"}
            }.get(language, {})
            
            mapped_rel_map = self.get_template("describe_rel_map", language, default_rel_map)
            
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
                
            sep = self.get_template("describe_separator", language, "، و" if language == "ar" else ", and ")
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
            
            default_header = {
                "en": "Knowledge available about {concept_label}:",
                "fr": "Connaissances disponibles sur {concept_label}:",
                "ar": "المعرفة المتوفرة حول {concept_label}:"
            }.get(language, "")
            
            template_header = self.get_template("knowledge_header", language, default_header)
            parts = [template_header.format(concept_label=concept_label)]
                
            for r in unique_outgoing[:5]:
                target_lbl = self.get_concept_label(r.get("target", ""), language)
                parts.append(f"{concept_label} {r.get('relation', '')} {target_lbl}")
            for r in unique_incoming[:3]:
                src_lbl = self.get_concept_label(r.get("source", ""), language)
                parts.append(f"{src_lbl} {r.get('relation', '')} {concept_label}")
                
            sep = self.get_template("knowledge_separator", language, "، " if language == "ar" else ", ")
            body = sep.join(parts)
            return body

        # 15.5. Causal Reasoning
        elif type_ == "causal_reasoning":
            reason = res.get("reason", "")
            return reason

        # 16. Unknown fail-safe
        else:
            default_val = {
                "ar": "بص بقى، معنديش أي معلومة أو حقيقة منطقية تسند السؤال ده في قاعدة البيانات حالياً، وأنا بفضل أقول معرفش على إني أهلس!",
                "en": "honestly, I do not possess any logical information or facts in the database to support this question, and I prefer to say I don't know rather than make things up!",
                "fr": "honnêtement, je ne dispose d'aucune information ou fait logique dans la base de données pour appuyer cette question, et je préfère dire que je ne sais pas plutôt que d'inventer!"
            }.get(language, "")
            
            template = self.get_template("unknown", language, default_val)
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
