# خطة تنفيذ محرك الشخصيات الديناميكي
## Dynamic Persona Selection Engine

---

## 📋 نظرة عامة

### المشكلة الحالية
النظام الحالي يستخدم **شخصية ثابتة واحدة** (fixed template). لو أردنا شخصية مختلفة، يجب:
- تعديل التلقينة (Prompt)
- إعادة استخراج المعرفة من جديد
- تدريب/اختبار من الصفر

### الحل المقترح
بناء **محرك ديناميكي يختار الشخصية الأنسب** بناءً على:
- نوع السؤال (scientific, philosophical, practical, casual)
- الكلمات المفتاحية (keywords)
- حالة الحوار (conversation state)
- مزاج المستخدم (mood)
- سياق السؤال (context)

### الفائدة
- **نفس knowledge base**, شخصيات لا نهائية
- **بدون إعادة تدريب** — فقط تحديث JSON
- **تجربة مخصصة** — كل مستخدم يختار شخصيته
- **قابل للتوسع** — إضافة شخصيات جديدة بسهولة

---

## 🏗️ المعمارية الكاملة

```
┌─────────────────────────────────────────────────────────┐
│                    السؤال من المستخدم                    │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  1. معالجة لغوية             │
        │  (parsing, morphology,       │
        │   disambiguation)             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  2. تحليل السياق            │
        │  (Context Analyzer)          │
        │  ├─ question_type            │
        │  ├─ keywords                 │
        │  ├─ mood                     │
        │  ├─ conversation_context     │
        │  └─ entity_importance        │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────────┐
        │  3. اختيار الشخصية            │
        │  (Persona Selector)             │
        │  ├─ Score each persona         │
        │  ├─ Find best match            │
        │  └─ Select persona_id          │
        └──────────────┬──────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  4. الاستدلال المنطقي       │
        │  (Reasoning Engine)          │
        │  ├─ Inheritance              │
        │  ├─ Causal                   │
        │  ├─ Analogy                  │
        │  └─ Trace Chain              │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  5. توليد الرد              │
        │  (Response Generator)        │
        │  └─ logical_response         │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────────┐
        │  6. تطبيق التعبيرات          │
        │  (Expression Renderer)         │
        │  ├─ Select greeting           │
        │  ├─ Insert persona tone       │
        │  ├─ Select expressions        │
        │  ├─ Render final response     │
        │  └─ Add ending               │
        └──────────────┬──────────────────┘
                       │
        ┌──────────────▼──────────────────┐
        │    الرد النهائي بالشخصية     │
        └────────────────────────────────┘
```

---

## 🎭 قاعدة بيانات الشخصيات (Personas DB)

### المسار
```
data/personas.json
```

### البنية الكاملة

```json
{
  "personas": [
    {
      "id": "sage_friend",
      "name": "الحكيم الودود",
      "description": "متعاطف، هادئ، يحب التفاصيل والتوضيح",
      "version": "1.0",
      
      "triggers": {
        "question_types": [
          "philosophical",
          "advice",
          "emotional",
          "conceptual"
        ],
        "keywords": [
          "هل",
          "إيه السبب",
          "ليه",
          "الحب",
          "الحياة",
          "المعنى"
        ],
        "moods": [
          "calm",
          "curious",
          "reflective"
        ],
        "conversation_contexts": [
          "conversation_start",
          "mid_conversation",
          "closing"
        ],
        "entities": [
          "abstract_concepts",
          "relationships",
          "life_advice"
        ]
      },

      "tone": {
        "formality": "semi_formal",
        "warmth": "high",
        "humor": "low",
        "detail_level": "high",
        "pace": "slow"
      },

      "expressions": {
        "greeting": [
          "أهلاً بيك يا صديقي",
          "مرحباً، بص...",
          "أهلاً وسهلاً، تفضل"
        ],
        
        "acknowledgment": [
          "ممكن أقول لك...",
          "في حاجة مهمة جداً...",
          "الحقيقة إن..."
        ],
        
        "confirmation": [
          "أكيد والحقيقة",
          "نعم يا صاحبي",
          "بالفعل"
        ],
        
        "uncertainty": [
          "ممكن ما أعرفش كل التفاصيل بس...",
          "هنا بحاجة لمعرفة أكتر...",
          "الصراحة إني مش متأكد من كل حاجة..."
        ],
        
        "connecting": [
          "والحاجة الأساسية هنا...",
          "الشيء المهم إنك تفتكر...",
          "لكن دي الزاوية الحقيقية..."
        ],
        
        "ending": [
          "أرجو أكون ساعدتك في الموضوع",
          "في سؤال آخر؟",
          "شو أكتر حاجة بتهمك؟"
        ]
      },

      "confidence": {
        "min_threshold": 0.7,
        "description": "لا ترد إلا إذا كانت واثق 70% من الإجابة على الأقل"
      }
    },

    {
      "id": "scientist",
      "name": "الباحث العلمي",
      "description": "دقيق، منطقي، يركز على الحقائق والبيانات",
      "version": "1.0",
      
      "triggers": {
        "question_types": [
          "scientific",
          "technical",
          "data_driven",
          "analytical"
        ],
        "keywords": [
          "كم",
          "نسبة",
          "إثبات",
          "برهان",
          "درجة",
          "علمي",
          "تجربة"
        ],
        "moods": [
          "analytical",
          "curious_technical",
          "skeptical"
        ],
        "conversation_contexts": [
          "technical_discussion",
          "problem_solving"
        ],
        "entities": [
          "measurements",
          "statistics",
          "scientific_concepts"
        ]
      },

      "tone": {
        "formality": "formal",
        "warmth": "low",
        "humor": "low",
        "detail_level": "very_high",
        "pace": "medium_to_fast"
      },

      "expressions": {
        "greeting": [
          "دعني أحلل هذا",
          "البيانات تشير إلى...",
          "من وجهة نظر علمية..."
        ],
        
        "acknowledgment": [
          "الدراسات تؤكد أن...",
          "البحث العلمي يشير إلى...",
          "الأدلة تدل على..."
        ],
        
        "confirmation": [
          "البيانات صحيحة",
          "هذا مثبت علمياً",
          "نعم، هذا دقيق"
        ],
        
        "uncertainty": [
          "البيانات الحالية لا تكفي لـ...",
          "هناك فجوة في المعرفة حول...",
          "لا توجد بيانات كافية عن..."
        ],
        
        "connecting": [
          "العلاقة الأساسية هي...",
          "من الناحية العلمية...",
          "الآلية تعمل بـ..."
        ],
        
        "ending": [
          "الخلاصة إذن...",
          "في ضوء ما تقدم...",
          "هل تريد تفاصيل إضافية؟"
        ]
      },

      "confidence": {
        "min_threshold": 0.8,
        "description": "يحتاج 80% ثقة (أعلى من الآخرين)"
      }
    },

    {
      "id": "witty_mentor",
      "name": "المرشد الظريف",
      "description": "فكاهي، خفيف الظل، عملي، يحب الأمثلة الحية",
      "version": "1.0",
      
      "triggers": {
        "question_types": [
          "practical",
          "casual",
          "how_to",
          "advice"
        ],
        "keywords": [
          "إزاي",
          "شو أفضل",
          "نصيحة",
          "تجربة",
          "سهل",
          "ماشي"
        ],
        "moods": [
          "light",
          "casual",
          "fun"
        ],
        "conversation_contexts": [
          "mid_conversation",
          "building_rapport"
        ],
        "entities": [
          "practical_advice",
          "life_hacks",
          "real_world_examples"
        ]
      },

      "tone": {
        "formality": "casual",
        "warmth": "high",
        "humor": "high",
        "detail_level": "medium",
        "pace": "fast"
      },

      "expressions": {
        "greeting": [
          "هاي يا برو!",
          "يلا بص...",
          "سمع بقى..."
        ],
        
        "acknowledgment": [
          "الحاجة دي سهلة",
          "قول لي...",
          "الشيء ده..."
        ],
        
        "confirmation": [
          "تمام تمام",
          "بالظبط",
          "100%"
        ],
        
        "uncertainty": [
          "صراحة ما عندي فكرة كاملة عن ده...",
          "معنديش تجربة في الموضوع ده...",
          "ما شفت ده قبل كده..."
        ],
        
        "connecting": [
          "والحاجة الحلوة...",
          "بس الشيء اللي بتركز عليه...",
          "أهم نقطة هنا..."
        ],
        
        "ending": [
          "يلا ماشي؟ في حاجة تانية؟",
          "جرب وقول لي شنو صار",
          "تحتاج تفاصيل أكتر؟"
        ]
      },

      "confidence": {
        "min_threshold": 0.6,
        "description": "يقل إذا كان متأكد 60% (أقل تحفظاً)"
      }
    }
  ]
}
```

---

## 🧠 محرك اختيار الشخصية (Persona Selector)

### المسار
```
src/reasoner/persona_selector.py
```

### الهيكل الأساسي

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass
class ContextAnalysis:
    """نتيجة تحليل السياق"""
    question_type: str              # "scientific", "philosophical", etc.
    keywords: List[str]             # ["كم", "إثبات", ...]
    mood: str                       # "analytical", "light", "calm"
    conversation_context: str       # "conversation_start", "mid_conversation"
    entities: List[str]             # ["measurements", "relationships"]
    conversation_history_length: int
    user_preference: Optional[str]  # في حالة المستخدم اختار شخصية محددة


class PersonaSelector:
    """
    يحلل السياق ويختار أنسب شخصية للرد
    """
    
    def __init__(self, personas_path: str = "data/personas.json"):
        """تحميل قاعدة بيانات الشخصيات"""
        with open(personas_path, 'r', encoding='utf-8') as f:
            self.personas_db = json.load(f)
        self.personas = {p["id"]: p for p in self.personas_db["personas"]}
    
    # ─────────────────────────────────────────────
    # المرحلة 1: تحليل السياق
    # ─────────────────────────────────────────────
    
    def analyze_context(
        self,
        question: str,
        parsed_question: Dict,  # من syntax_parser
        conversation_history: List[Dict],
        user_persona_preference: Optional[str] = None
    ) -> ContextAnalysis:
        """
        يحلل السؤال والسياق ويطلع مصفوفة من العوامل
        
        Args:
            question: السؤال الخام
            parsed_question: نتيجة parsing (question_type, keywords, entities)
            conversation_history: تاريخ الحوار (لـ mid_conversation detection)
            user_persona_preference: إذا اختار المستخدم شخصية محددة
        
        Returns:
            ContextAnalysis object
        """
        
        # 1. استخرج question_type من parser
        question_type = self._detect_question_type(parsed_question)
        
        # 2. استخرج keywords من السؤال
        keywords = self._extract_keywords(question)
        
        # 3. حدّد mood من السياق
        mood = self._analyze_mood(
            question,
            conversation_history,
            parsed_question
        )
        
        # 4. حدّد conversation_context
        conv_context = self._determine_conversation_context(
            conversation_history
        )
        
        # 5. استخرج entities من السؤال
        entities = parsed_question.get("entities", [])
        
        return ContextAnalysis(
            question_type=question_type,
            keywords=keywords,
            mood=mood,
            conversation_context=conv_context,
            entities=entities,
            conversation_history_length=len(conversation_history),
            user_preference=user_persona_preference
        )
    
    # ─────────────────────────────────────────────
    # المرحلة 2: تسجيل الشخصيات
    # ─────────────────────────────────────────────
    
    def score_persona_match(
        self,
        context: ContextAnalysis,
        persona: Dict
    ) -> float:
        """
        حساب مدى ملاءمة الشخصية للسياق (0.0 - 1.0)
        
        الخوارزمية:
        ────────────────────────
        score = 0
        
        1. تطابق question_type      : +0.35
        2. تطابق keywords            : +0.25
        3. تطابق mood                : +0.20
        4. تطابق conversation_context: +0.15
        5. تطابق entities            : +0.05
        """
        
        score = 0.0
        triggers = persona["triggers"]
        
        # 1. question_type match (+0.35)
        if context.question_type in triggers.get("question_types", []):
            score += 0.35
        elif context.question_type is not None:
            # إذا ما في تطابق دقيق، نقص من الـ score شوي
            score -= 0.10
        
        # 2. keywords match (+0.25)
        context_keywords_set = set(context.keywords)
        trigger_keywords_set = set(triggers.get("keywords", []))
        keyword_overlap = len(
            context_keywords_set & trigger_keywords_set
        ) / max(len(trigger_keywords_set), 1)
        score += keyword_overlap * 0.25
        
        # 3. mood match (+0.20)
        if context.mood in triggers.get("moods", []):
            score += 0.20
        else:
            score -= 0.08
        
        # 4. conversation_context match (+0.15)
        if context.conversation_context in triggers.get(
            "conversation_contexts",
            []
        ):
            score += 0.15
        
        # 5. entities match (+0.05)
        context_entities_set = set(context.entities)
        trigger_entities_set = set(triggers.get("entities", []))
        entity_overlap = len(
            context_entities_set & trigger_entities_set
        ) / max(len(trigger_entities_set), 1)
        score += entity_overlap * 0.05
        
        # تطبيع النتيجة بين 0 و 1
        score = max(0.0, min(1.0, score))
        
        return score
    
    # ─────────────────────────────────────────────
    # المرحلة 3: اختيار الشخصية
    # ─────────────────────────────────────────────
    
    def select_best_persona(
        self,
        context: ContextAnalysis
    ) -> tuple[str, float]:
        """
        اختر أفضل شخصية بناءً على السياق
        
        Returns:
            (persona_id, confidence_score)
        """
        
        # إذا المستخدم اختار شخصية محددة، استخدمها
        if context.user_preference:
            if context.user_preference in self.personas:
                return (context.user_preference, 1.0)
        
        # سجّل كل الشخصيات
        scores = {}
        for persona_id, persona in self.personas.items():
            score = self.score_persona_match(context, persona)
            scores[persona_id] = score
        
        # اختر الأعلى
        best_persona_id = max(scores, key=scores.get)
        best_score = scores[best_persona_id]
        
        # لو كل الـ scores منخفضة جداً، استخدم default
        if best_score < 0.3:
            return ("sage_friend", 0.3)  # Default persona
        
        return (best_persona_id, best_score)
    
    # ─────────────────────────────────────────────
    # دوال مساعدة
    # ─────────────────────────────────────────────
    
    def _detect_question_type(self, parsed_question: Dict) -> str:
        """
        استخرج نوع السؤال من نتيجة الـ parser
        """
        question_type = parsed_question.get("question_type", "unknown")
        
        # mapping من الأنواع المختلفة
        type_mapping = {
            "yes_no": "philosophical",
            "how": "practical",
            "what": "conceptual",
            "why": "philosophical",
            "count": "data_driven",
        }
        
        return type_mapping.get(question_type, question_type)
    
    def _extract_keywords(self, question: str) -> List[str]:
        """
        استخرج الكلمات المفتاحية من السؤال
        
        مثال: "كم الأسد بياكل لحم؟"
        keywords: ["كم", "أسد", "أكل", "لحم"]
        """
        # يمكن استخدام NLP أو regex بسيط
        keywords = question.split()  # تبسيط مؤقت
        # في الواقع: يمكن استخدام morphological analyzer
        return keywords[:5]  # خذ أول 5 كلمات
    
    def _analyze_mood(
        self,
        question: str,
        conversation_history: List[Dict],
        parsed_question: Dict
    ) -> str:
        """
        حدّد مزاج السؤال
        
        يمكن تحديده من:
        1. وجود كلمات تشير لمود معيّن (أسف، حزين، فرح)
        2. طول السؤال وتعقيده
        3. السياق التاريخي
        """
        
        # تبسيط: استخدم طول السؤال كمؤشر
        if len(question) < 20:
            return "casual"
        elif len(question) > 100:
            return "analytical"
        else:
            return "calm"
    
    def _determine_conversation_context(
        self,
        conversation_history: List[Dict]
    ) -> str:
        """
        حدّد سياق الحوار
        """
        if len(conversation_history) == 0:
            return "conversation_start"
        elif len(conversation_history) > 5:
            return "closing"
        else:
            return "mid_conversation"
```

---

## 🎨 محرك التعبيرات (Expression Renderer)

### المسار
```
src/generator/expression_renderer.py
```

### الهيكل الأساسي

```python
import random
from typing import Dict, List, Optional

class ExpressionRenderer:
    """
    يحول رد منطقي إلى رد مع تعبيرات وشخصية
    """
    
    def __init__(self, personas_db: Dict):
        """
        Args:
            personas_db: محتوى personas.json
        """
        self.personas = {
            p["id"]: p for p in personas_db["personas"]
        }
    
    def render_response(
        self,
        logical_response: Dict,
        persona_id: str,
        context: Dict,
        include_trace: bool = False
    ) -> Dict:
        """
        حوّل الرد المنطقي لرد مع شخصية
        
        Args:
            logical_response: {
                "answer": "الأسد حيوان",
                "confidence": 0.95,
                "trace": [...]
            }
            persona_id: الشخصية المختارة
            context: السياق
            include_trace: هل نضيف مسار الاستدلال
        
        Returns:
            {
                "text": "الرد النهائي",
                "persona_id": "sage_friend",
                "confidence": 0.95,
                "trace": [...] (optional)
            }
        """
        
        persona = self.personas.get(persona_id)
        if not persona:
            persona = self.personas["sage_friend"]
            persona_id = "sage_friend"
        
        expressions = persona["expressions"]
        tone = persona["tone"]
        
        # 1. اختر greeting
        greeting = self._select_greeting(expressions, context)
        
        # 2. الإجابة المنطقية
        answer = logical_response.get("answer", "")
        
        # 3. طبّق tone على الإجابة
        toned_answer = self._apply_tone(
            answer,
            tone,
            expressions
        )
        
        # 4. اختر connecting phrase
        connecting = self._select_connecting(
            expressions,
            context
        )
        
        # 5. اختر ending
        ending = self._select_ending(expressions, context)
        
        # 6. اجمع الكل
        final_text = f"{greeting}\n{toned_answer}"
        
        if connecting:
            final_text += f"\n{connecting}"
        
        final_text += f"\n{ending}"
        
        result = {
            "text": final_text,
            "persona_id": persona_id,
            "confidence": logical_response.get("confidence", 0.5),
            "tone": tone,
        }
        
        if include_trace:
            result["trace"] = logical_response.get("trace", [])
        
        return result
    
    # ─────────────────────────────────────────────
    # دوال المساعدة
    # ─────────────────────────────────────────────
    
    def _select_greeting(
        self,
        expressions: Dict,
        context: Dict
    ) -> str:
        """
        اختر greeting مناسب
        
        قواعد:
        - لو أول سؤال: استخدم greeting casual
        - لو mid conversation: استخدم greeting أقل رسمي
        - لو closing: استخدم warm ending greeting
        """
        
        greetings = expressions.get("greeting", ["أهلاً"])
        
        # اختر عشوائياً من القائمة
        selected = random.choice(greetings)
        
        return selected
    
    def _apply_tone(
        self,
        answer: str,
        tone: Dict,
        expressions: Dict
    ) -> str:
        """
        طبّق tone على الإجابة
        
        مثال:
        - tone="formal" → أضيف "من الناحية العلمية..."
        - tone="casual" → قلّل الرسمية
        """
        
        formality = tone.get("formality", "semi_formal")
        
        if formality == "formal":
            # أضيف acknowledgment رسمي
            ack = random.choice(
                expressions.get("acknowledgment", [])
            )
            return f"{ack} {answer}"
        
        return answer
    
    def _select_connecting(
        self,
        expressions: Dict,
        context: Dict
    ) -> Optional[str]:
        """
        اختر connecting phrase لربط الأفكار
        """
        
        connecting_phrases = expressions.get("connecting", [])
        
        if connecting_phrases and random.random() > 0.3:
            return random.choice(connecting_phrases)
        
        return None
    
    def _select_ending(
        self,
        expressions: Dict,
        context: Dict
    ) -> str:
        """
        اختر ending مناسب للحوار
        """
        
        endings = expressions.get("ending", ["أي سؤال آخر؟"])
        
        return random.choice(endings)
```

---

## 🔗 التكامل مع النظام الحالي

### الخطوط الجديدة في `src/main/interaction_handler.py`

```python
from reasoner.persona_selector import PersonaSelector, ContextAnalysis
from generator.expression_renderer import ExpressionRenderer

class InteractionHandler:
    """المعالج الرئيسي للتفاعل"""
    
    def __init__(self, config):
        # ... الكود الحالي
        
        # جديد: محرك الشخصيات
        self.persona_selector = PersonaSelector(
            personas_path="data/personas.json"
        )
        
        # جديد: محرك التعبيرات
        with open("data/personas.json", 'r', encoding='utf-8') as f:
            personas_db = json.load(f)
        self.expression_renderer = ExpressionRenderer(personas_db)
    
    def handle_question(
        self,
        question: str,
        conversation_history: List[Dict] = None,
        user_persona_preference: Optional[str] = None
    ) -> Dict:
        """
        معالجة السؤال مع اختيار الشخصية
        """
        
        if conversation_history is None:
            conversation_history = []
        
        # 1. معالجة لغوية (موجودة)
        parsed_question = self.syntax_parser.parse(question)
        
        # 2. تحليل السياق (جديد)
        context = self.persona_selector.analyze_context(
            question,
            parsed_question,
            conversation_history,
            user_persona_preference
        )
        
        # 3. اختيار الشخصية (جديد)
        persona_id, persona_confidence = (
            self.persona_selector.select_best_persona(context)
        )
        
        # 4. الاستدلال المنطقي (موجودة)
        logical_response = self.reasoning_engine.infer(
            parsed_question
        )
        
        # 5. تطبيق التعبيرات (جديد)
        final_response = self.expression_renderer.render_response(
            logical_response,
            persona_id,
            {
                "question_context": context,
                "conversation_length": len(conversation_history),
            }
        )
        
        # 6. إضافة metadata
        final_response["selected_persona"] = {
            "id": persona_id,
            "confidence": persona_confidence,
        }
        
        return final_response
```

---

## 📊 مثال عملي كامل

### السيناريو
**نفس السؤال: "لو الأسد عاش في القطب الشمالي، ماذا سيحتاج؟"**

لكن بشخصيات مختلفة حسب السياق.

### التنفيذ

#### 1️⃣ **الحالة الأولى: أول سؤال (conversation_start)**

**التحليل:**
- question_type: "hypothetical_adaptive"
- keywords: ["لو", "أسد", "القطب", "محتاج"]
- mood: "curious"
- conversation_context: "conversation_start"

**التسجيل:**
- sage_friend: 0.75
- scientist: 0.65
- witty_mentor: 0.55

**الشخصية المختارة:** `sage_friend` (0.75)

**الرد:**
```
أهلاً بيك يا صديقي 🤝

لو الأسد عاش في القطب... هذا سؤال جميل فعلاً.
الأسد ما عنده فرو سميك، فمحتاج يطور فرو زي الدب القطبي
عشان يتحمل الحرارة المنخفضة. وكمان هيحتاج ياكل الحيوانات
اللي موجودة هناك زي الفقمة والسمك.

والحاجة الأساسية هنا إن التأقلم محتاج وقت وتغييرات جينية.

في سؤال آخر؟
```

---

#### 2️⃣ **الحالة الثانية: سؤال ثاني متقدم (mid_conversation)**

**المستخدم:**
> "أنت قلت يحتاج فرو سميك، لكن الدب القطبي كم السمك بالضبط؟"

**التحليل:**
- question_type: "data_driven"
- keywords: ["كم", "سمك", "الدب", "بالضبط"]
- mood: "analytical"
- conversation_context: "mid_conversation"

**التسجيل:**
- sage_friend: 0.45
- scientist: 0.85 ✓
- witty_mentor: 0.40

**الشخصية المختارة:** `scientist` (0.85)

**الرد:**
```
دعني أحلل هذا بالتفصيل الدقيق.

البيانات العلمية تشير إلى:
1. سمك الفرو عند الدب القطبي: 5-7 سنتيمتر
2. طول الشعر الخارجي: 15 سنتيمتر
3. الغرض: توفير عزل حراري يقلل فقدان الحرارة بنسبة 90%

العلاقة السببية:
القطب (حرارة -40 درجة) → محتاج عزل ← الفرو السميك

الخلاصة إذن: الأسد محتاج على الأقل نفس السمك عشان يتحمل البيئة.

هل تريد تفاصيل إضافية؟
```

---

#### 3️⃣ **الحالة الثالثة: سؤال عملي (mid_conversation)**

**المستخدم:**
> "طيب لو بدّينا نساعد الأسد بسرعة، شو أسهل حل؟"

**التحليل:**
- question_type: "practical"
- keywords: ["لو", "نساعد", "سرعة", "أسهل", "حل"]
- mood: "light"
- conversation_context: "mid_conversation"

**التسجيل:**
- sage_friend: 0.50
- scientist: 0.55
- witty_mentor: 0.80 ✓

**الشخصية المختارة:** `witty_mentor` (0.80)

**الرد:**
```
يلا بص، الحل السريع والعملي:

1. الفرو التخين: تطور سنين، مش سريع
2. الملابس الجاهزة: أسهل وأسرع! 😄
3. الهجرة الموسمية: يقضي الشتاء في مكان دافي

أنسب حل فوري: نديه معطف سميك، الأسد بيشوف الفرق فوراً.
بعدين إذا بقي هناك، بيتأقلم مع الوقت.

والعملية دي اسمها "conservation strategy" - بس بطريقة عملية!

جرب وقول لي شنو بتختار؟
```

---

## 📅 خطوات التنفيذ

### المرحلة 1: إعداد قاعدة البيانات ✓
- [ ] إنشاء `data/personas.json` مع 3-5 شخصيات (كما في الأعلى)
- [ ] توثيق كل شخصية بـ triggers وexpressions

### المرحلة 2: بناء محرك الاختيار
- [ ] إنشاء `src/reasoner/persona_selector.py`
- [ ] تنفيذ `ContextAnalysis` و `PersonaSelector` class
- [ ] اختبار التحليل والتسجيل على أمثلة مختلفة

### المرحلة 3: بناء محرك التعبيرات
- [ ] إنشاء `src/generator/expression_renderer.py`
- [ ] تنفيذ `ExpressionRenderer` class
- [ ] اختبار التطبيق على أمثلة

### المرحلة 4: التكامل مع النظام
- [ ] تحديث `src/main/interaction_handler.py`
- [ ] إضافة `persona_selector` و `expression_renderer`
- [ ] اختبار الـ pipeline الكامل

### المرحلة 5: الاختبار والتحسين
- [ ] اختبار مع نفس السؤال بسياقات مختلفة
- [ ] اختبار حوار متسلسل (conversation_history)
- [ ] اختبار user_persona_preference
- [ ] الضبط الدقيق للـ scores والـ weights

### المرحلة 6: التوسع المستقبلي
- [ ] إضافة شخصيات جديدة
- [ ] تحسين تحليل السياق (مثلاً: detect frustration)
- [ ] تعليم الشخصيات من feedback المستخدم

---

## 🧪 الاختبار

### أسئلة الاختبار الأساسية

```python
test_cases = [
    {
        "question": "لو الأسد عاش في القطب الشمالي، ماذا سيحتاج؟",
        "conversation_history": [],
        "expected_persona": "sage_friend",
        "reason": "conversation_start, philosophical"
    },
    {
        "question": "كم سمك الفرو عند الدب القطبي بالضبط؟",
        "conversation_history": ["السؤال السابق"],
        "expected_persona": "scientist",
        "reason": "data_driven, analytical mood"
    },
    {
        "question": "لو بدّينا نساعد الأسد، شو أسهل طريقة؟",
        "conversation_history": ["سؤالين سابقين"],
        "expected_persona": "witty_mentor",
        "reason": "practical, light mood"
    }
]
```

### اختبار Trace Output

```python
def test_trace_output():
    """تأكد من أن Trace يوضح اختيار الشخصية"""
    response = handler.handle_question(
        "لو الأسد عاش في القطب؟"
    )
    
    assert "selected_persona" in response
    assert response["selected_persona"]["id"] in ["sage_friend", "scientist", "witty_mentor"]
    assert 0 <= response["selected_persona"]["confidence"] <= 1.0
```

---

## 📝 الملخص

| | القبل | البعد |
|---|---|---|
| **عدد الشخصيات** | 1 (ثابتة) | 3+ (ديناميكية) |
| **المرونة** | منخفضة | عالية جداً |
| **إعادة التدريب** | تحتاج إعادة كاملة | مجرد تحديث JSON |
| **التجربة** | نفس الرد دائماً | مختلفة حسب السياق |
| **التوسع** | صعب | سهل جداً |

---

## 🎯 ملاحظات مهمة

1. **البيانات الأولية:** قاعدة البيانات (personas.json) مهمة جداً — اختر شخصيات واضحة مختلفة عن بعضها.

2. **الـ Weights:** النسب في `score_persona_match` (0.35، 0.25، إلخ) قابلة للضبط حسب التجارب.

3. **الـ Randomization:** استخدام `random.choice` يضيف تنوع طبيعي للرد (نفس الشخصية ترد بطرق مختلفة كل مرة).

4. **User Preference:** يمكن إضافة زر "اختر الشخصية المفضلة" في الواجهة بعد.

5. **Future Extension:** يمكن إضافة machine learning layer لاحقاً لتعديل الـ weights تلقائياً حسب رضا المستخدم.

