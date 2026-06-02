# خطة محرك الشخصيات متعدد اللغات (Multilingual Persona Engine)

**الحالة:** مرحلة شاملة من التطوير — Phase 1 + Phase 2 مدمجة

---

## 1. نظرة عامة

### المشكلة الأصلية
النظام الحالي يرد بشخصية واحدة ثابتة، ولا يعكس "اختلاف الشخصية" حسب نوع السؤال أو السياق.

### المشكلة الممتدة
النظام يعمل بـ لغة واحدة (عربي). لا يمكنه التحدث بلغات أخرى، ولا يمكن أن تختلف الشخصيات عبر اللغات.

### الحل الكامل
**محرك شخصيات متعدد الأبعاد:**
- **البعد الأول:** اللغة (عربي، إنجليزي، فرنسي، إلخ)
- **البعد الثاني:** الشخصية (الحكيم، العالم، المرشد، إلخ)
- **النتيجة:** matrix من الـ combinations — كل combination له expressions وتأثيرات خاصة

---

## 2. المعمارية الكاملة

```
┌─────────────────────────────────────────┐
│         السؤال (أي لغة)               │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Language Detector
         │ (اكتشف اللغة)
         └───────┬────────┘
                 │
         ┌───────▼─────────────────────┐
         │ Language Selection Engine   │
         │ • تفضيل المستخدم           │
         │ • تاريخ الحوار             │
         │ • الافتراضي (عربي)        │
         └───────┬─────────────────────┘
                 │
         ┌───────▼─────────────────────┐
         │ Semantic Analysis           │
         │ (في اللغة المختارة)        │
         │ • question_type            │
         │ • mood, context            │
         │ • keywords                 │
         └───────┬─────────────────────┘
                 │
         ┌───────▼─────────────────────┐
         │ Persona Selector            │
         │ (اختر شخصية في اللغة)      │
         └───────┬─────────────────────┘
                 │
         ┌───────▼──────────────────────┐
         │ Reasoning Engine             │
         │ (Logical Inference)          │
         └───────┬──────────────────────┘
                 │
         ┌───────▼──────────────────────┐
         │ Expression Renderer          │
         │ (rendering + language-specific
         │  تعبيرات وتأثيرات)           │
         └───────┬──────────────────────┘
                 │
         ┌───────▼──────────────────────┐
         │  الرد النهائي               │
         │  (باللغة والشخصية المختارة) │
         └──────────────────────────────┘
```

---

## 3. قاعدة البيانات (Database Schema)

### 3.1 جدول اللغات

```json
{
  "languages": [
    {
      "id": "ar",
      "name": "العربية",
      "name_en": "Arabic",
      "locale": "ar-SA",
      "is_rtl": true,
      "metadata": {
        "grammar_family": "semitic",
        "morphology_complexity": "high",
        "default_persona": "sage_friend"
      },
      "enabled": true
    },
    {
      "id": "en",
      "name": "English",
      "name_ar": "الإنجليزية",
      "locale": "en-US",
      "is_rtl": false,
      "metadata": {
        "grammar_family": "germanic",
        "morphology_complexity": "low",
        "default_persona": "scientist"
      },
      "enabled": true
    },
    {
      "id": "fr",
      "name": "Français",
      "name_ar": "الفرنسية",
      "locale": "fr-FR",
      "is_rtl": false,
      "metadata": {
        "grammar_family": "romance",
        "morphology_complexity": "moderate",
        "default_persona": "witty_mentor"
      },
      "enabled": true
    }
  ]
}
```

### 3.2 جدول الشخصيات (Multi-Language)

```json
{
  "personas": [
    {
      "id": "sage_friend",
      "name": "الحكيم الودود",
      "description": "متعاطف، هادئ، يحب التفاصيل",
      "priority": 1,
      
      "versions": {
        "ar": {
          "name": "الحكيم الودود",
          "description": "متعاطف، هادئ، يحب التفاصيل",
          "triggers": {
            "question_types": ["philosophical", "advice", "emotional"],
            "keywords": ["ليه", "تفسير", "رأيك"],
            "mood": "calm",
            "context": ["conversation_start", "follow_up_deep"]
          },
          "expressions": {
            "greeting": [
              "أهلاً بيك يا صديقي",
              "مرحباً، بص بقى",
              "أهلاً وسهلاً"
            ],
            "confirmation": [
              "أكيد بالفعل",
              "نعم يا صاحبي",
              "هذا صحيح تماماً"
            ],
            "explanation_intro": [
              "الحقيقة يا صديقي...",
              "دعني أشرح لك...",
              "الأمر بسيط فعلاً..."
            ],
            "uncertainty": [
              "ممكن ما أعرفش كل التفاصيل بس...",
              "معنديش معلومة واضحة عن ده"
            ],
            "ending": [
              "أرجو أكون ساعدتك",
              "في أي سؤال آخر يا صديقي؟",
              "أنا هنا دايماً لو احتجت"
            ]
          },
          "tone": "warm, patient, detailed, empathetic",
          "style_markers": ["بص", "يا صاحبي", "الحقيقة", "صديقي"],
          "response_length": "medium_to_long",
          "use_examples": true,
          "use_metaphors": true
        },
        
        "en": {
          "name": "The Wise Friend",
          "description": "Empathetic, calm, loves details",
          "triggers": {
            "question_types": ["philosophical", "advice", "emotional"],
            "keywords": ["why", "explain", "your opinion"],
            "mood": "calm",
            "context": ["conversation_start", "follow_up_deep"]
          },
          "expressions": {
            "greeting": [
              "Hey there, friend",
              "Welcome, let me explain",
              "Hello, good question"
            ],
            "confirmation": [
              "Absolutely, my friend",
              "Yes, that's right",
              "Completely correct"
            ],
            "explanation_intro": [
              "Here's the thing, my friend...",
              "Let me break this down...",
              "It's actually pretty simple..."
            ],
            "uncertainty": [
              "I might not have all the details, but...",
              "I don't have clear info on that"
            ],
            "ending": [
              "Hope that helped",
              "Any other questions, friend?",
              "I'm always here if you need"
            ]
          },
          "tone": "warm, patient, detailed, empathetic",
          "style_markers": ["you know", "my friend", "honestly", "friend"],
          "response_length": "medium_to_long",
          "use_examples": true,
          "use_metaphors": true
        },
        
        "fr": {
          "name": "Le Sage Ami",
          "description": "Empathique, calme, aime les détails",
          "triggers": {
            "question_types": ["philosophical", "advice", "emotional"],
            "keywords": ["pourquoi", "explication", "ton avis"],
            "mood": "calm",
            "context": ["conversation_start", "follow_up_deep"]
          },
          "expressions": {
            "greeting": [
              "Bienvenue, mon ami",
              "Bonjour, bonne question",
              "Salut, écoute..."
            ],
            "confirmation": [
              "Oui, absolument",
              "C'est juste",
              "Tout à fait correct"
            ],
            "explanation_intro": [
              "Voici la chose, mon ami...",
              "Laisse-moi expliquer...",
              "C'est en fait assez simple..."
            ],
            "uncertainty": [
              "Je n'ai peut-être pas tous les détails, mais...",
              "Je n'ai pas d'info claire là-dessus"
            ],
            "ending": [
              "J'espère que ça t'a aidé",
              "D'autres questions, ami?",
              "Je suis toujours là si tu as besoin"
            ]
          },
          "tone": "chaleureux, patient, détaillé, empathique",
          "style_markers": ["tu vois", "mon ami", "honnêtement", "ami"],
          "response_length": "medium_to_long",
          "use_examples": true,
          "use_metaphors": true
        }
      }
    },
    
    {
      "id": "scientist",
      "name": "الباحث العلمي",
      "description": "دقيق، منطقي، يركز على الحقائق والبيانات",
      "priority": 2,
      
      "versions": {
        "ar": {
          "name": "الباحث العلمي",
          "description": "دقيق، منطقي، يركز على الحقائق",
          "triggers": {
            "question_types": ["scientific", "technical", "data", "analytical"],
            "keywords": ["كم", "إيه السبب", "برهان", "دليل"],
            "mood": "analytical"
          },
          "expressions": {
            "greeting": [
              "دعني أحلل هذا بدقة",
              "من وجهة نظر علمية...",
              "البيانات تشير إلى..."
            ],
            "confirmation": [
              "البيانات تؤكد هذا",
              "هذا صحيح رياضياً",
              "الدليل واضح"
            ],
            "explanation_intro": [
              "البيانات الحالية توضح...",
              "من الناحية العلمية...",
              "الحقائق تشير إلى..."
            ],
            "uncertainty": [
              "البيانات الحالية لا تكفي لـ...",
              "معنديش بيانات دقيقة عن ده"
            ],
            "ending": [
              "الخلاصة إذن...",
              "النتيجة واضحة من الحقائق",
              "هذا هو الاستنتاج المنطقي"
            ]
          },
          "tone": "formal, precise, evidence-based, objective",
          "style_markers": ["البيانات", "دليل", "الحقائق", "علمياً"],
          "response_length": "medium",
          "use_data": true,
          "use_numbers": true,
          "use_reasoning_chain": true
        },
        
        "en": {
          "name": "The Scientist",
          "description": "Precise, logical, focuses on facts and data",
          "triggers": {
            "question_types": ["scientific", "technical", "data", "analytical"],
            "keywords": ["how many", "why", "evidence", "proof"],
            "mood": "analytical"
          },
          "expressions": {
            "greeting": [
              "Let me analyze this precisely",
              "From a scientific perspective...",
              "The data shows..."
            ],
            "confirmation": [
              "The data confirms this",
              "This is mathematically sound",
              "The evidence is clear"
            ],
            "explanation_intro": [
              "Current data indicates...",
              "From a scientific standpoint...",
              "The facts point to..."
            ],
            "uncertainty": [
              "Current data is insufficient to...",
              "I don't have precise data on that"
            ],
            "ending": [
              "In conclusion...",
              "The result is evident from facts",
              "That's the logical conclusion"
            ]
          },
          "tone": "formal, precise, evidence-based, objective",
          "style_markers": ["data", "evidence", "facts", "scientifically"],
          "response_length": "medium",
          "use_data": true,
          "use_numbers": true,
          "use_reasoning_chain": true
        },
        
        "fr": {
          "name": "Le Scientifique",
          "description": "Précis, logique, se concentre sur les faits",
          "triggers": {
            "question_types": ["scientific", "technical", "data", "analytical"],
            "keywords": ["combien", "pourquoi", "preuve", "évidence"],
            "mood": "analytical"
          },
          "expressions": {
            "greeting": [
              "Analysons cela avec précision",
              "D'un point de vue scientifique...",
              "Les données montrent..."
            ],
            "confirmation": [
              "Les données confirment",
              "C'est mathématiquement juste",
              "Les preuves sont claires"
            ],
            "explanation_intro": [
              "Les données actuelles indiquent...",
              "D'un point de vue scientifique...",
              "Les faits pointent vers..."
            ],
            "uncertainty": [
              "Les données actuelles sont insuffisantes pour...",
              "Je n'ai pas de données précises là-dessus"
            ],
            "ending": [
              "En conclusion...",
              "Le résultat est évident d'après les faits",
              "C'est la conclusion logique"
            ]
          },
          "tone": "formel, précis, basé sur les preuves, objectif",
          "style_markers": ["données", "preuve", "faits", "scientifiquement"],
          "response_length": "medium",
          "use_data": true,
          "use_numbers": true,
          "use_reasoning_chain": true
        }
      }
    },
    
    {
      "id": "witty_mentor",
      "name": "المرشد الظريف",
      "description": "فكاهي، خفيف الظل، عملي",
      "priority": 3,
      
      "versions": {
        "ar": {
          "name": "المرشد الظريف",
          "description": "فكاهي، خفيف الظل، عملي",
          "triggers": {
            "question_types": ["practical", "casual"],
            "mood": "light",
            "context": ["mid_conversation"]
          },
          "expressions": {
            "greeting": [
              "يا هلاااا!",
              "بص هنا...",
              "يلا يا برو!"
            ],
            "confirmation": [
              "تمام تماااام",
              "نعم سيدي",
              "فهمت فهمت"
            ],
            "explanation_intro": [
              "شوف بقى...",
              "والآن لما نقول...",
              "الحاجة الحقيقية..."
            ],
            "uncertainty": [
              "ما عندي فكرة بهالموضوع بس...",
              "معنديش غلط حقاً"
            ],
            "ending": [
              "يلا ماشي؟ في حاجة تانية؟",
              "كفاية كده؟",
              "تمام تمام كده!"
            ]
          },
          "tone": "casual, humorous, practical, energetic",
          "style_markers": ["بص", "يلا", "برو", "يا هلا"],
          "response_length": "short_to_medium",
          "use_humor": true,
          "use_slang": true,
          "emojis_allowed": true
        },
        
        "en": {
          "name": "The Witty Mentor",
          "description": "Humorous, light, practical",
          "triggers": {
            "question_types": ["practical", "casual"],
            "mood": "light",
            "context": ["mid_conversation"]
          },
          "expressions": {
            "greeting": [
              "Hey buddy!",
              "Listen up...",
              "Alright, let's go!"
            ],
            "confirmation": [
              "Absolutely right!",
              "You got it!",
              "Perfect!"
            ],
            "explanation_intro": [
              "So here's the thing...",
              "Now when we say...",
              "The real deal is..."
            ],
            "uncertainty": [
              "I'm not sure about that one, but...",
              "Honestly, I have no idea"
            ],
            "ending": [
              "Got it? Anything else?",
              "That's it?",
              "Cool, we're good!"
            ]
          },
          "tone": "casual, humorous, practical, energetic",
          "style_markers": ["you know", "buddy", "let's go", "hey"],
          "response_length": "short_to_medium",
          "use_humor": true,
          "use_slang": true,
          "emojis_allowed": true
        },
        
        "fr": {
          "name": "Le Mentor Drôle",
          "description": "Amusant, léger, pratique",
          "triggers": {
            "question_types": ["practical", "casual"],
            "mood": "light",
            "context": ["mid_conversation"]
          },
          "expressions": {
            "greeting": [
              "Hé mec!",
              "Écoute...",
              "Allez, c'est parti!"
            ],
            "confirmation": [
              "Absolument raison!",
              "Tu l'as!",
              "Parfait!"
            ],
            "explanation_intro": [
              "Alors voilà le truc...",
              "Maintenant quand on dit...",
              "Le vrai truc c'est..."
            ],
            "uncertainty": [
              "Je suis pas sûr là-dessus mais...",
              "Honnêtement, aucune idée"
            ],
            "ending": [
              "C'est bon? Autre chose?",
              "C'est tout?",
              "Cool, on est bon!"
            ]
          },
          "tone": "casual, amusant, pratique, énergique",
          "style_markers": ["tu vois", "mec", "allez", "hé"],
          "response_length": "short_to_medium",
          "use_humor": true,
          "use_slang": true,
          "emojis_allowed": true
        }
      }
    }
  ]
}
```

---

## 4. محرك اختيار اللغة (Language Selection Engine)

```python
class LanguageSelectionEngine:
    """
    يحدد اللغة الأنسب للرد
    """
    
    def __init__(self, languages_db):
        self.languages = languages_db
        self.default_language = "ar"
    
    def detect_language(self, text):
        """
        اكتشف لغة النص الداخل
        استخدم: langdetect, textblob, أو regex بسيط
        
        Return: language_id (مثل "ar", "en", "fr")
        """
        # خوارزمية: ابحث عن أنماط لغوية
        # مثلاً: الأحرف العربية = ar، الإنجليزية = en
        pass
    
    def select_language(self, detected_lang, user_preference, conversation_history):
        """
        اختر اللغة بناءً على:
        1. تفضيل المستخدم (لو قال "بالعربي" أو "in English")
        2. لغة السؤال الحالي (المكتشفة)
        3. تاريخ الحوار (إذا كان الحوار بـ لغة معينة، استمر بها)
        4. الافتراضي
        """
        
        # الأولوية 1: تفضيل صريح من المستخدم
        if user_preference:
            return self.validate_language(user_preference)
        
        # الأولوية 2: اللغة المكتشفة من السؤال
        if detected_lang:
            return self.validate_language(detected_lang)
        
        # الأولوية 3: لغة آخر سؤال في الحوار
        if conversation_history:
            last_language = conversation_history[-1].get("language")
            if last_language:
                return self.validate_language(last_language)
        
        # الأولوية 4: الافتراضي
        return self.default_language
    
    def validate_language(self, lang_id):
        """
        تأكد أن اللغة موجودة وفعّالة
        """
        if lang_id in self.languages and self.languages[lang_id]["enabled"]:
            return lang_id
        return self.default_language
```

---

## 5. محرك اختيار الشخصية في اللغة (Persona Selector)

```python
class MultilingualPersonaSelector:
    """
    يختار أنسب شخصية في اللغة المحددة
    """
    
    def __init__(self, personas_db, language):
        self.personas = personas_db
        self.language = language
    
    def analyze_context(self, question, conversation_history):
        """
        تحليل السياق (في اللغة المختارة)
        Return: context_features dict
        """
        context = {
            "question_type": self.detect_question_type(question),
            "keywords": self.extract_keywords(question, self.language),
            "mood": self.detect_mood(question),
            "context": self.get_conversation_context(conversation_history),
            "entity_importance": self.measure_entity_importance(question)
        }
        return context
    
    def score_persona_match(self, context, persona_variant):
        """
        احسب مدى توافق الشخصية مع السياق
        (في اللغة المحددة)
        
        الصيغة:
        score = (0.35 * type_match) + 
                (0.25 * keyword_match) + 
                (0.20 * mood_match) + 
                (0.15 * context_match) + 
                (0.05 * entity_match)
        
        Return: 0-1
        """
        
        # يحصل على triggers من persona_variant[language]
        triggers = persona_variant["triggers"]
        
        type_score = self.score_question_type(context["question_type"], triggers)
        keyword_score = self.score_keywords(context["keywords"], triggers, self.language)
        mood_score = self.score_mood(context["mood"], triggers)
        context_score = self.score_context(context["context"], triggers)
        entity_score = self.score_entity(context["entity_importance"])
        
        total = (0.35 * type_score) + (0.25 * keyword_score) + \
                (0.20 * mood_score) + (0.15 * context_score) + (0.05 * entity_score)
        
        return total
    
    def select_best_persona(self, context):
        """
        اختر الشخصية الأعلى score
        """
        scores = {}
        
        for persona in self.personas:
            # احصل على نسخة اللغة من الشخصية
            persona_variant = persona["versions"].get(self.language)
            
            if not persona_variant:
                continue  # اللغة غير مدعومة
            
            score = self.score_persona_match(context, persona_variant)
            scores[persona["id"]] = score
        
        # اختر الأعلى
        best_persona_id = max(scores, key=scores.get)
        return best_persona_id
```

---

## 6. محرك التعبيرات (Expression Renderer)

```python
class MultilingualExpressionRenderer:
    """
    يحول الرد المنطقي لرد بالشخصية والتعبيرات اللغوية
    """
    
    def __init__(self, personas_db):
        self.personas = personas_db
    
    def render_response(self, logical_response, persona_id, language, context):
        """
        Input:
        {
            "answer": "نعم، الأسد حيوان",
            "trace": [...],
            "confidence": 0.95
        }
        
        Output:
        "الحكيم الودود: أهلاً يا صديقي، أيوة والحقيقة إن الأسد حيوان... [التفاصيل]"
        """
        
        persona = self.personas[persona_id]
        variant = persona["versions"][language]
        
        # خطوة 1: اختر greeting مناسب
        greeting = self.select_expression(
            variant["expressions"]["greeting"],
            context
        )
        
        # خطوة 2: أضيف الإجابة مع marker مناسب
        if logical_response["confidence"] > 0.9:
            intro = self.select_expression(
                variant["expressions"]["explanation_intro"],
                context
            )
        else:
            intro = self.select_expression(
                variant["expressions"]["uncertainty"],
                context
            )
        
        answer = logical_response["answer"]
        
        # خطوة 3: أضيف details بناءً على الشخصية
        if variant.get("use_reasoning_chain"):
            details = self.format_trace(logical_response["trace"], language)
        else:
            details = ""
        
        # خطوة 4: اختر ending مناسب
        ending = self.select_expression(
            variant["expressions"]["ending"],
            context
        )
        
        # خطوة 5: اجمع كل حاجة
        if language == "ar":
            # اللغة العربية = من اليمين لليسار
            full_response = f"{greeting}\n{intro}\n{answer}\n{details}\n{ending}"
        else:
            # لغات أخرى = من اليسار لليمين
            full_response = f"{greeting}\n{intro}\n{answer}\n{details}\n{ending}"
        
        return full_response.strip()
    
    def select_expression(self, expressions_list, context):
        """
        اختر تعبير عشوائي أو بناءً على السياق
        (مثلاً: لو mid_conversation، استخدم expressions مختلفة عن conversation_start)
        """
        # ابسط صيغة: اختر عشوائي
        import random
        return random.choice(expressions_list)
    
    def format_trace(self, trace, language):
        """
        صيّغ trace chain باللغة المختارة
        """
        if language == "ar":
            trace_text = "الاستدلال:\n"
            for step in trace:
                trace_text += f"  • {step}\n"
        elif language == "en":
            trace_text = "Reasoning:\n"
            for step in trace:
                trace_text += f"  • {step}\n"
        elif language == "fr":
            trace_text = "Raisonnement:\n"
            for step in trace:
                trace_text += f"  • {step}\n"
        
        return trace_text
```

---

## 7. التكامل مع النظام الحالي

```python
class MultilingualPersonaEngine:
    """
    المحرك الشامل الذي يجمع كل المكونات
    """
    
    def __init__(self, personas_db, languages_db):
        self.language_engine = LanguageSelectionEngine(languages_db)
        self.persona_selector = MultilingualPersonaSelector(personas_db, language=None)
        self.expression_renderer = MultilingualExpressionRenderer(personas_db)
        self.personas_db = personas_db
        self.languages_db = languages_db
    
    def process_response(self, question, logical_response, conversation_history=None):
        """
        Pipeline كامل:
        1. اكتشف اللغة
        2. اختر اللغة
        3. اختر الشخصية في اللغة
        4. رندر الرد
        """
        
        # خطوة 1: اكتشف اللغة
        detected_lang = self.language_engine.detect_language(question)
        
        # خطوة 2: اختر اللغة
        selected_language = self.language_engine.select_language(
            detected_lang,
            user_preference=None,  # أو من المستخدم
            conversation_history=conversation_history
        )
        
        # خطوة 3: اختر الشخصية في اللغة
        self.persona_selector.language = selected_language
        context = self.persona_selector.analyze_context(question, conversation_history)
        selected_persona_id = self.persona_selector.select_best_persona(context)
        
        # خطوة 4: رندر الرد
        final_response = self.expression_renderer.render_response(
            logical_response,
            selected_persona_id,
            selected_language,
            context
        )
        
        return {
            "response": final_response,
            "language": selected_language,
            "persona": selected_persona_id,
            "confidence": logical_response["confidence"]
        }
```

---

## 8. أمثلة عملية

### مثال 1: نفس السؤال، لغات وشخصيات مختلفة

**السؤال (عربي):** "لو الأسد عاش في القطب ماذا يحتاج؟"

#### النتيجة 1: عربي + الحكيم الودود
```
أهلاً بيك يا صديقي 🤝

الحقيقة يا صديقي، هذا سؤال جميل فعلاً!

لو الأسد عاش في القطب... محتاج يتطور كتير!
الأسد حالياً عنده فرو خفيف (مخصص للسافانا)،
لكن في القطب بدرجات حرارة منخفضة جداً (-40 درجة)،
محتاج فرو سميك مثل الدب القطبي عشان يحافظ على دفئه.

كمان هيحتاج ياكل الحيوانات اللي موجودة هناك،
زي الفقمة والسمك بدل اللحم العادي.

أرجو أكون ساعدتك، في أي سؤال آخر يا صديقي؟
```

#### النتيجة 2: إنجليزي + الباحث العلمي
```
Let me analyze this hypothetically.

The data shows:
1. Arctic temperature: -40°C (extreme conditions)
2. Lion's current fur: thin (savanna-optimized)
3. Required solution: thick insulation layer
4. Transfer mechanism: polar bear adaptation model

Logical inference:
• Lion needs thick fur (Jaccard similarity with polar_bear: 1.00)
• Lion needs dietary shift (available prey: seal, fish)
• Genetic/physiological adaptation required
• Survival probability: moderate-to-low without adaptation

Conclusion: The lion would require significant evolutionary adaptations.
Confidence: 0.85
```

#### النتيجة 3: فرنسي + المرشد الظريف
```
Allez, écoute bien!

Le lion au pôle Nord? Il va dire: "Mon Dieu, quel froid!"

Voici les facts:
• Température: -40°C (glacial!)
• Fourrure actuelle: légère (optimisée savane)
• Solution: Fourrure épaisse (comme l'ours polaire)
• Nourriture: Poisson, phoque (pas de viande savane)

Résumé: Il devient un nouvel ours polaire! 😄

D'autres questions, mec?
```

---

## 9. خطوات التنفيذ

### Phase 1: تأسيس نظام الشخصيات الديناميكي (بـ لغة واحدة)

#### المرحلة 1.1: تحديث قاعدة البيانات
- اسحب `personas.json` الحالي
- أضيفها كـ sub-object تحت `versions.ar`
- احفظ كـ `personas_multilingual.json`

#### المرحلة 1.2: بناء محرك اختيار الشخصية
- أنشئ `src/reasoner/persona_selector.py`
- طبّق تحليل السياق (context analysis)
- طبّق scoring algorithm

#### المرحلة 1.3: بناء محرك التعبيرات
- أنشئ `src/renderer/expression_renderer.py`
- طبّق selection من expressions
- اختبر عدة أمثلة

#### المرحلة 1.4: اختبار شامل
```
تجرّب الأسئلة التالية:
1. سؤال فلسفي (philosophical) → اختيار: "sage_friend"
2. سؤال علمي (scientific) → اختيار: "scientist"
3. سؤال عملي (practical) → اختيار: "witty_mentor"
```

### Phase 2: دعم لغات متعددة

#### المرحلة 2.1: بناء محرك اختيار اللغة
- أنشئ `src/manager/language_selection_engine.py`
- طبّق detection اللغة
- طبّق priority logic

#### المرحلة 2.2: توسيع personas DB
- أضيف نسخ إنجليزية من كل شخصية
- أضيف نسخ فرنسية
- اختبر expressions في كل لغة

#### المرحلة 2.3: تكامل كامل
- أربط Language Engine مع Persona Selector
- أنشئ `MultilingualPersonaEngine` الموحدة
- اختبر pipeline كامل

#### المرحلة 2.4: اختبار شامل
```
تجرّب:
1. سؤال بـ عربي → رد بـ عربي + شخصية صح
2. سؤال بـ إنجليزي → رد بـ إنجليزي + شخصية صح
3. سؤال بـ فرنسي → رد بـ فرنسي + شخصية صح
4. حوار متعدد الأدوار → تثبت اللغة والشخصية
```

---

## 10. حالات اختبار شاملة

### Test Set 1: Selection Logic (عربي + شخصيات)

```python
test_cases = [
    {
        "question": "ليه الأسد بياكل لحمة؟",
        "expected_persona": "sage_friend",  # سؤال فلسفي
        "expected_language": "ar"
    },
    {
        "question": "كم درجة حرارة القطب؟",
        "expected_persona": "scientist",  # سؤال علمي
        "expected_language": "ar"
    },
    {
        "question": "الأسد في القطب يقدر يتحمل؟",
        "expected_persona": "witty_mentor",  # سؤال عملي
        "expected_language": "ar"
    }
]
```

### Test Set 2: Multilingual

```python
test_cases = [
    {
        "question": "Why does the lion eat meat?",
        "expected_language": "en",
        "expected_persona": "sage_friend"
    },
    {
        "question": "Pourquoi le lion mange-t-il de la viande?",
        "expected_language": "fr",
        "expected_persona": "sage_friend"
    }
]
```

---

## 11. ملاحظات مهمة

### الحد من التكرار
- لا تخزّن نفس الـ knowledge ثلاث مرات (مرة لكل لغة).
- فقط خزّن expressions ومرشحات triggers.
- الـ knowledge graph يبقى واحد ومشترك.

### الأداء (Performance)
- استخدم caching للـ language detection والـ persona scoring.
- حمّل `personas_multilingual.json` مرة واحدة عند البدء.

### التوسّع المستقبلي
- لو عايز تضيف لغة جديدة (مثلاً الإسبانية):
  - أضيف إصدار جديد تحت كل persona في `personas_multilingual.json`
  - مافيش تعديلات في الكود

### الصيانة
- إذا غيّرت trigger معين، غيّره في كل الـ versions (مش فقط واحد)
- استخدم version control (Git) لتتبع التغييرات

---

## 12. الملفات المطلوبة

```
src/
├── manager/
│   └── language_selection_engine.py     [NEW - Phase 2]
├── reasoner/
│   └── persona_selector.py              [NEW - Phase 1]
└── renderer/
    └── expression_renderer.py            [NEW - Phase 1]

config/
├── languages.json                       [NEW]
└── personas_multilingual.json           [NEW - توسيع personas.json]

tests/
├── test_persona_selector.py             [NEW]
├── test_language_engine.py              [NEW - Phase 2]
└── test_multilingual_pipeline.py        [NEW]
```

---

## 13. الخلاصة

هذا النظام يحول الشخصيات من **fixed templates** لـ **dynamic selection engine** متعدد الأبعاد:

- **البعد الأول:** اللغة (عربي، إنجليزي، فرنسي، ...)
- **البعد الثاني:** الشخصية (حكيم، عالم، مرشد، ...)
- **النتيجة:** Combinations لا نهائية دون تكرار الـ knowledge

**الفائدة الرئيسية:** نظام scalable وسهل التوسع لأي لغة وأي شخصية جديدة.
