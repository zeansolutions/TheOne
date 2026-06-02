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
            
    def get_concept_label(self, concept_id, language):
        """
        Translates a concept ID into the target language label.
        """
        if language == "ar":
            if self.handler.graph.has_node(concept_id):
                labels = self.handler.graph.nodes[concept_id].get("labels", [])
                if labels:
                    return labels[0]
            return concept_id
            
        # Fallbacks for common concepts (check first to guarantee best translation)
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
            }
        }
        
        fallback_map = fallbacks.get(language, {})
        if concept_id in fallback_map:
            return fallback_map[concept_id]
            
        # Get language rules lexicon
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
            
        return concept_id

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
            if language == "ar":
                return f"{c1_lbl} هو {c2_lbl}، دي الحقيقة! الاستدلال التصنيفي أثبت العلاقة دي بالوراثة الصاعدة." if res["result"] else f"حسب معرفتي المنطقية {c1_lbl} ليس {c2_lbl}."
            elif language == "en":
                return f"{c1_lbl} is a {c2_lbl}, that's correct! Taxonomic deduction proves this relation via ascending inheritance." if res["result"] else f"According to my logical knowledge, {c1_lbl} is not a {c2_lbl}."
            elif language == "fr":
                return f"{c1_lbl} est un {c2_lbl}, c'est exact! La déduction taxonomique prouve cette relation par héritage ascendant." if res["result"] else f"Selon mes connaissances logiques, {c1_lbl} n'est pas un {c2_lbl}."

        # 2. Location
        elif type_ == "location":
            c_lbl = self.get_concept_label(res["concept"], language)
            loc_lbl = self.get_concept_label(res["location"], language)
            if language == "ar":
                return f"{c_lbl} بيعيش في {loc_lbl}."
            elif language == "en":
                return f"{c_lbl} lives in the {loc_lbl}."
            elif language == "fr":
                return f"{c_lbl} vit dans la {loc_lbl}."

        # 3. Hypothetical
        elif type_ == "hypothetical":
            entity_lbl = self.get_concept_label(res["entity"], language)
            env_lbl = self.get_concept_label(res["environment"], language)
            
            if res["needs_adaptation"]:
                prop_lbl = self.get_concept_label(res["transferred_property"], language)
                cand_lbl = self.get_concept_label(res["analogy_candidate"], language)
                
                if language == "ar":
                    return (
                        f"لو {entity_lbl} عاش في {env_lbl}، "
                        f"أكيد محتاج يتكيف! البيئة هناك برد شديد ومحتاجة عزل حراري قوي، "
                        f"عشان كدة هيحتاج يطور {prop_lbl} زي {cand_lbl} بالظبط اللي بيعيش هناك. "
                        f"وبالنسبة للغذاء، هيتخلى عن طرائده المعتادة ويتغذى على فرائس قطبية متوفرة زي الفقمات والأسماك. "
                        f"يعني تكيف كامل مبني على التناظر المنطقي."
                    )
                elif language == "en":
                    return (
                        f"if a {entity_lbl} lived in the {env_lbl}, "
                        f"it would definitely need to adapt! The environment there is extremely cold and requires strong thermal insulation, "
                        f"which is why it would need to develop {prop_lbl} just like a {cand_lbl} that lives there. "
                        f"As for food, it would abandon its usual prey and feed on available polar prey like seals and fish. "
                        f"This represents a complete adaptation based on logical analogy."
                    )
                elif language == "fr":
                    return (
                        f"si un {entity_lbl} vivait dans l'{env_lbl}, "
                        f"il aurait certainement besoin de s'adapter! L'environnement y est extrêmement froid et nécessite une forte isolation thermique, "
                        f"c'est pourquoi il devrait développer une {prop_lbl} tout comme un {cand_lbl} qui y vit. "
                        f"Pour la nourriture, il abandonnerait ses proies habituelles et se nourrirait de proies polaires disponibles comme les phoques et les poissons. "
                        f"Cela représente une adaptation complète basée sur l'analogie logique."
                    )
            else:
                if language == "ar":
                    return f"لو {entity_lbl} عاش في {env_lbl} مش محتاج يغير صفاته الجسدية لأنه مهيأ ليها بالفعل."
                elif language == "en":
                    return f"if a {entity_lbl} lived in the {env_lbl}, it would not need to change its physical properties because it is already suited for it."
                elif language == "fr":
                    return f"si un {entity_lbl} vivait dans l'{env_lbl}, il n'aurait pas besoin de modifier ses propriétés physiques car il y est déjà adapté."

        # 4. Comparison
        elif type_ == "comparison":
            c1_lbl = self.get_concept_label(res["concept1"], language)
            c2_lbl = self.get_concept_label(res["concept2"], language)
            
            p1_str = " & ".join([self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "has_property"])
            p2_str = " & ".join([self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "has_property"])
            
            l1 = next((self.get_concept_label(p["property"], language) for p in res["props1"] if p["relation"] == "lives_in"), None)
            l2 = next((self.get_concept_label(p["property"], language) for p in res["props2"] if p["relation"] == "lives_in"), None)
            
            if language == "ar":
                l1_str = l1 or "بيئته"
                l2_str = l2 or "بيئته"
                p1_formatted = p1_str or "صفات مخصصة لبيئته"
                p2_formatted = p2_str or "صفات تناسب البرودة"
                return (
                    f"الفرق واضح جداً بين {c1_lbl} و {c2_lbl}: "
                    f"أولاً، {c1_lbl} بيعيش في {l1_str} وعنده {p1_formatted}. "
                    f"أما {c2_lbl} فبيعيش في {l2_str} وعنده {p2_formatted}. "
                    f"لكن التشابه الجوهري أن كلاهما ثدييات مفترسة تصنيفياً."
                )
            elif language == "en":
                l1_str = l1 or "its environment"
                l2_str = l2 or "its environment"
                p1_formatted = p1_str or "properties optimized for its environment"
                p2_formatted = p2_str or "properties suited for the cold"
                return (
                    f"The difference is very clear between {c1_lbl} and {c2_lbl}: "
                    f"first, {c1_lbl} lives in {l1_str} and has {p1_formatted}. "
                    f"On the other hand, {c2_lbl} lives in {l2_str} and has {p2_formatted}. "
                    f"However, the core similarity is that both are taxonomically predatory mammals."
                )
            elif language == "fr":
                l1_str = l1 or "son environnement"
                l2_str = l2 or "son environnement"
                p1_formatted = p1_str or "des propriétés optimisées pour son environnement"
                p2_formatted = p2_str or "des propriétés adaptées au froid"
                return (
                    f"La différence est très claire entre {c1_lbl} et {c2_lbl}: "
                    f"premièrement, {c1_lbl} vit dans {l1_str} et a {p1_formatted}. "
                    f"D'un autre côté, {c2_lbl} vit dans {l2_str} et a {p2_formatted}. "
                    f"Cependant, la similitude fondamentale est que les deux sont taxonomiquement des mammifères prédateurs."
                )

        # 5. Teaching
        elif type_ == "teaching":
            msg = res.get("message", "")
            if language == "ar":
                return msg
                
            status = res.get("status")
            world = res.get("world", "reality")
            # Translate message based on status
            if language == "en":
                if status == "added":
                    return f"New fact saved successfully in world '{world}'."
                elif status == "identical":
                    return f"The fact already exists in world '{world}'."
                elif status == "auto_replaced":
                    return f"Fact automatically updated because new confidence is higher."
                elif status == "auto_rejected":
                    return f"New fact rejected because existing confidence is higher."
                elif status == "non_interactive_rejected":
                    return f"New fact ignored due to conflict."
                else:
                    return msg or "Fact operation finished."
            elif language == "fr":
                if status == "added":
                    return f"Nouveau fait enregistré avec succès dans le monde '{world}'."
                elif status == "identical":
                    return f"Le fait existe déjà dans le monde '{world}'."
                elif status == "auto_replaced":
                    return f"Fait automatiquement mis à jour car la nouvelle confiance est plus élevée."
                elif status == "auto_rejected":
                    return f"Nouveau fait rejeté car la confiance existante est plus élevée."
                elif status == "non_interactive_rejected":
                    return f"Nouveau fait ignoré en raison d'un conflit."
                else:
                    return msg or "Opération sur le fait terminée."

        # 6. Unknown fail-safe
        else:
            if language == "ar":
                return "بص بقى، معنديش أي معلومة أو حقيقة منطقية تسند السؤال ده في قاعدة البيانات حالياً، وأنا بفضل أقول معرفش على إني أهلس!"
            elif language == "en":
                return "honestly, I do not possess any logical information or facts in the database to support this question, and I prefer to say I don't know rather than make things up!"
            elif language == "fr":
                return "honnêtement, je ne dispose d'aucune information ou fait logique dans la base de données pour appuyer cette question, et je préfère dire que je ne sais pas plutôt que d'inventer!"
                
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
        if variant.get("use_reasoning_chain") or logical_response.get("type") in ["classification", "hypothetical", "location", "comparison"]:
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
