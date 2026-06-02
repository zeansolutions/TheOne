# خطة التنفيذ الشاملة لنظام Neuro-Symbolic AI
## نظام منطقي صادق قابل للتعليم المستمر

---

## 📋 جدول المحتويات
1. نظرة عامة على النظام
2. المعمارية الكاملة
3. قواعد البيانات الأربعة
4. محرك الاستدلال
5. خطوات معالجة السؤال
6. بنية ملف JSON
7. الـ Prompt الكامل للـ LLM
8. مثال عملي كامل (عالم الحيوانات)
9. خارطة الطريق
10. البرنامج الأول (MVP)

---

## 1️⃣ نظرة عامة على النظام

### الفكرة الأساسية
بناء بديل لـ LLMs بدون إحصاء أثناء التشغيل — نظام **منطقي محايد** يفهم الأسئلة ويرد برمنطق واستدلال شفّاف وقابل للتتبّع.

### الفلسفة الحاكمة
- ✅ **Zero Hallucination**: لو مايعرفش، يقول "مش عندي معلومة"
- ✅ **Transparent Reasoning**: كل رد مرفقه بسلسلة استدلال كاملة
- ✅ **Continuous Learning**: النظام قابل للتعليم أثناء التشغيل
- ✅ **Symbolic + Causal**: اجمع بين التصنيف والعلاقات السببية والتمثيل
- ✅ **No Inference Hallucination**: استدلال يقيني فقط + تمثيل موجّه بالسبب
- ✅ **Bounded Domain**: كل عالم له حدود معرّفة واضحة

### دور الـ LLM
الـ LLM يلعب **دور واحد فقط**: مُستخرِج المعرفة من النصوص (extraction time، مش runtime).
- المستخدم بيديه قصة/نص
- الـ LLM بيستخرج منها معلومات منسّقة في JSON
- التطبيق بينظّم الـ JSON في قواعد البيانات
- **من هنا فصاعداً: لا لـ LLM، كل شيء منطق بحت.**

---

## 2️⃣ المعمارية الكاملة

```
┌─────────────────────────────────────────────────────────┐
│           المستخدم / واجهة الحوار                      │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │  Input Processor        │
      │ (تحليل نحوي وصرفي)     │
      └────────────┬────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐  ┌───────────┐  ┌──────────┐
│ Parser │  │Morphology │  │Lexicon   │
│(نحو)   │  │Analyzer   │  │Database  │
└────┬───┘  └─────┬─────┘  └────┬─────┘
     │            │             │
     └────────────┼─────────────┘
                  │
          ┌───────▼────────┐
          │ Disambiguation │
          │ (Spreading     │
          │  Activation)   │
          └───────┬────────┘
                  │
       ┌──────────▼──────────┐
       │ Question Analyzer   │
       │ (ما نوع السؤال؟)   │
       └──────────┬──────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
 ┌────────┐  ┌────────┐  ┌──────────┐
 │Fact    │  │Graph   │  │World     │
 │DB      │  │Handler │  │Manager   │
 │(عالم) │  │(استنتاج)│  │(تعارضات) │
 └────┬───┘  └────┬───┘  └─────┬────┘
      │           │            │
      └───────────┼────────────┘
                  │
         ┌────────▼─────────┐
         │ Reasoning Engine │
         │ ┌───────────────┐│
         │ │Inheritance    ││
         │ │Deduction      ││
         │ │Causal         ││
         │ │Analogy        ││
         │ └───────────────┘│
         └────────┬─────────┘
                  │
         ┌────────▼─────────┐
         │ Response         │
         │ Generator        │
         │ ┌───────────────┐│
         │ │Template       ││
         │ │Selection      ││
         │ │Persona        ││
         │ │Application    ││
         │ └───────────────┘│
         └────────┬─────────┘
                  │
         ┌────────▼─────────┐
         │ Conversation     │
         │ Manager          │
         │(تخزين السياق)    │
         └────────┬─────────┘
                  │
      ┌───────────▼───────────┐
      │ Final Output          │
      │ - الرد بالعربية      │
      │ - سلسلة الاستدلال   │
      │ - معامل الثقة        │
      └───────────────────────┘
```

---

## 3️⃣ قواعد البيانات الأربعة

### أولاً: قاعدة البيانات الأساسية (Language Rules DB)
**الملف**: `data/language_rules.json`

```json
{
  "morphology": {
    "roots": [
      { "id": "كتب", "patterns": ["كتاب", "كتب", "مكتب", "يكتب"] },
      { "id": "أكل", "patterns": ["أكل", "طعام", "يأكل"] }
    ],
    "particles": [
      { "form": "ال", "type": "definite_article" },
      { "form": "و", "type": "conjunction" },
      { "form": "في", "type": "preposition" }
    ]
  },
  "grammar": {
    "sentence_types": [
      { "id": "declarative", "pattern": "noun + verb + object", "description": "جملة خبرية" },
      { "id": "interrogative", "pattern": "interrogative_particle + ...", "description": "جملة استفهامية" },
      { "id": "conditional", "pattern": "if + condition + then", "description": "جملة شرطية" }
    ],
    "question_particles": ["هل", "ما", "كيف", "كم", "ماذا", "أين", "متى", "لماذا"]
  }
}
```

---

### ثانياً: قاعدة المفاهيم والعلاقات (Knowledge Graph DB)
**الملف**: `data/ontology.json`

```json
{
  "concepts": [
    {
      "id": "animal",
      "labels": ["حيوان", "كائن حي"],
      "description": "كائن حي متحرك يتغذى على الكائنات الأخرى"
    },
    {
      "id": "feline_carnivore",
      "labels": ["أسد", "ليث"],
      "description": "حيوان مفترس"
    }
  ],
  "relations": [
    {
      "from": "feline_carnivore",
      "relation": "is_a",
      "to": "carnivore",
      "type": "classification"
    },
    {
      "from": "feline_carnivore",
      "relation": "has_property",
      "to": "thin_fur",
      "causal_purpose": "adaptation_to_warm_climates"
    },
    {
      "from": "thin_fur",
      "relation": "purpose",
      "to": "thermal_regulation",
      "value": "poor_insulation"
    },
    {
      "from": "thick_fur",
      "relation": "purpose",
      "to": "thermal_regulation",
      "value": "good_insulation"
    },
    {
      "from": "arctic",
      "relation": "has_environment",
      "to": "extreme_cold"
    },
    {
      "from": "extreme_cold",
      "relation": "requires",
      "to": "good_insulation"
    }
  ],
  "inference_rules": [
    {
      "id": "rule_1",
      "name": "Inheritance through is_a",
      "pattern": "X is_a Y, Y is_a Z => X is_a Z",
      "logic": "transitive"
    },
    {
      "id": "rule_2",
      "name": "Causal Adaptation",
      "pattern": "Environment E requires Property P, Animal A in E, A lacks P => A needs to adapt P",
      "logic": "causal_reasoning"
    },
    {
      "id": "rule_3",
      "name": "Analogy Transfer",
      "pattern": "A1 is_similar_to A2, A2 has_property P, P solves_problem Prob => A1 can_have P",
      "logic": "analogical_reasoning"
    }
  ]
}
```

---

### ثالثاً: قاعدة الحقائق (Facts DB)
**الملف**: `data/facts.json`

```json
{
  "facts": [
    {
      "id": "fact_1",
      "world": "reality",
      "subject": "sun",
      "predicate": "rises_from",
      "object": "east",
      "confidence": 1.0,
      "source": "astronomy"
    },
    {
      "id": "fact_2",
      "world": "arctic",
      "subject": "polar_bear",
      "predicate": "lives_in",
      "object": "arctic",
      "confidence": 1.0
    },
    {
      "id": "fact_3",
      "world": "arctic",
      "subject": "polar_bear",
      "predicate": "has_property",
      "object": "thick_fur",
      "confidence": 1.0,
      "reason": "arctic is extreme_cold, extreme_cold requires good_insulation, thick_fur provides good_insulation"
    }
  ]
}
```

---

### رابعاً: قاعدة الشخصية والسياق (Persona + Context DB)
**الملف**: `data/personas.json`

```json
{
  "personas": [
    {
      "id": "persona_1",
      "name": "الخبير المرح",
      "language_style": {
        "tone": "friendly_expert",
        "particles": ["يا صاحبي", "بص بقى", "دي الحقيقة"],
        "filler_words": ["طبعاً", "أكيد"]
      },
      "knowledge_preferences": {
        "detailed": true,
        "examples": true,
        "analogies": true
      },
      "personality_traits": {
        "humorous": 0.7,
        "formal": 0.3,
        "patient": 0.9
      }
    }
  ]
}
```

---

## 4️⃣ محرك الاستدلال (Reasoning Engine)

### المستويات الأربعة للاستدلال

#### 1. **Inheritance Deduction** (الوراثة والتصنيف)
```python
def inheritance_deduction(entity, property_type):
    """
    إذا كان: 
      - X من نوع Y
      - Y يملك خاصية P
    إذن: X يملك خاصية P
    """
    current = entity
    while current:
        # ابحث عن علاقات is_a
        parent = graph.get_parent(current, "is_a")
        if parent and graph.has_property(parent, property_type):
            return True
        current = parent
    return False
```

#### 2. **Causal Reasoning** (الاستدلال السببي)
```python
def causal_reasoning(entity, environment, target_property):
    """
    إذا كان:
      - البيئة تحتاج خاصية P
      - الكائن لا يملك P
    إذن: الكائن في هذه البيئة يحتاج P
    """
    # ابحث عن ما تحتاجه البيئة
    env_needs = graph.get_requirements(environment)
    
    # هل الكائن عنده ده؟
    entity_has = graph.has_property(entity, target_property)
    
    if target_property in env_needs and not entity_has:
        return {
            "conclusion": f"{entity} needs {target_property}",
            "trace": [
                f"{environment} has requirement: {target_property}",
                f"{entity} does not have: {target_property}",
                f"→ {entity} must adapt"
            ]
        }
```

#### 3. **Analogical Reasoning** (التمثيل)
```python
def analogical_reasoning(source_entity, target_entity, target_env):
    """
    إذا كان:
      - A و B متشابهان (نفس العائلة، بنفس الـ category)
      - B يعيش في بيئة E وعنده خاصية P
      - E ملها نفس المتطلبات المتطلبة لـ A
    إذن: A يمكنه امتلاك P
    """
    similarity_score = graph.calculate_similarity(source_entity, target_entity)
    
    if similarity_score > 0.6:  # عتبة التشابه
        # خذ خصائص target_entity
        properties = graph.get_properties(target_entity)
        return {
            "conclusion": f"{source_entity} can potentially have properties like {target_entity}",
            "adapted_properties": properties,
            "confidence": similarity_score
        }
```

#### 4. **Conflict Resolution** (حل التعارضات)
```python
def resolve_world_conflict(fact1, fact2):
    """
    إذا تعارضت حقيقتان من عالمين مختلفين:
    - استخدم ترجيح العالم
    - أو حفظ كلا النسختين مع الإشارة إلى العالم
    """
    if fact1['world'] == fact2['world']:
        # تعارض داخل نفس العالم → خطأ
        return {"error": "contradiction_in_same_world"}
    else:
        # تعارض بين عالمين → طبيعي، احفظ الاثنين
        return {
            "fact1": fact1,
            "fact2": fact2,
            "note": f"Different facts in different worlds: {fact1['world']} vs {fact2['world']}"
        }
```

---

## 5️⃣ خطوات معالجة السؤال (الـ Pipeline)

### الخطوة 1: Input Preprocessing
```
المستخدم: "لو الأسد عاش في القطب، ماذا يحتاج عشان يتحمل الحرارة؟"

↓

الخطوة الأولى: تقسيم وتنظيف
- إزالة الفراغات الزائدة
- تحديد اللغة (عربي)
- تقسيم لجمل فرعية إن لزم
```

### الخطوة 2: Morphological Analysis
```
"الأسد" → 
  - الجذر: "أسد"
  - النوع: noun
  - التعريف: definite (ال)

"يحتاج" →
  - الجذر: "حتج"
  - الفعل: present tense
  - النوع: verb
```

### الخطوة 3: Syntactic Parsing
```
الجملة الرئيسية:
- نوع: conditional (شرط)
- الشرط: "الأسد عاش في القطب"
- السؤال: "ماذا يحتاج"

تحليل الشرط:
- الموضوع: الأسد (entity)
- الفعل: عاش (live)
- المكان: القطب (environment)

تحليل السؤال:
- الاستفهام: ماذا (what)
- الموضوع: يحتاج (needs)
- المقصود: ما الذي يحتاجه
```

### الخطوة 4: Lexicon Lookup + Disambiguation
```
"أسد" → concept_id: "feline_carnivore"
"القطب" → concept_id: "arctic"
"يحتاج" → relation: "requires"

السياق:
- Environment (arctic) ← يشير إلى "extreme_cold"
- Action (يحتاج) ← causal reasoning مطلوب
```

### الخطوة 5: World Selection
```
المستخدم ذكر شرط افتراضي ("لو...")
→ اختر "hypothetical_world" أو "alternate_arctic_scenario"
→ لكن تطبّق قواعس arctic الأساسية
```

### الخطوة 6: Reasoning Engine Execution
```
الاستدلال:
1. Arctic has environment: extreme_cold
2. Extreme_cold requires: good_insulation
3. Feline_carnivore currently has: thin_fur
4. Thin_fur provides: poor_insulation
5. → CONCLUSION: Feline_carnivore in arctic needs to adapt fur

البحث عن حل:
- ابحث عن "good_insulation" في graph
- لقيت "thick_fur" توفّره
- لقيت "polar_bear" لديها "thick_fur"
- → Analogy: كما يفعل polar_bear

البحث عن غذاء:
- Arctic animals that carnivore can eat?
- تشابه قائم: carnivore + cold environment
- → lemmings, seals, fish
```

### الخطوة 7: Response Generation
```
الحقائق المستخرجة:
- الأسد يحتاج فرو تخين
- الأسد يمكنه أن يأكل الفقمات والأسماك

القالب (Template):
"بما أن [البيئة] تتطلب [الخاصية]، و[الكائن] لا يملكها،
فإن [الكائن] بحاجة إلى [التكيف]."

الرد النهائي (مع الشخصية):
"يا صاحبي، لو الأسد عاش في القطب، محتاج يغيّر فروه التخين
عشان يتحمل البرد الشديد — زي الدب القطبي بالظبط.
وبعدين يقدر يتغذى على الفقمات والسمك اللي في هناك."
```

### الخطوة 8: Trace Chain Compilation
```
سلسلة الاستدلال الكاملة:

السؤال: "لو الأسد عاش في القطب؟"

الخطوات:
1. تحديد الموضوع: الأسد (feline_carnivore)
2. تحديد البيئة: القطب (arctic, extreme_cold)
3. البحث عن متطلبات البيئة: extreme_cold requires good_insulation
4. تقييم خصائص الأسد الحالية: feline_carnivore has thin_fur
5. مقارنة: thin_fur → poor_insulation (غير كافي)
6. البحث عن حل: good_insulation ← provided by thick_fur
7. البحث عن نظير: polar_bear has thick_fur and lives in arctic
8. التمثيل (Analogy): feline_carnivore (similar to polar_bear) needs thick_fur
9. البحث عن غذاء: arctic_predators can eat seals, fish, lemmings
10. الاستنتاج: يحتاج فرو + قائمة طعام جديدة

معامل الثقة (Confidence): 0.95
(عالي لأن كل الخطوات مستندة على تصنيفات واضحة)
```

---

## 6️⃣ بنية ملف JSON النهائية

### Input JSON (ما يعطيه المستخدم للـ LLM)
```json
{
  "text": "الأسد حيوان مفترس يعيش في السافانا. الدب القطبي يعيش في الأرض المتجمدة وعنده فرو سميك عشان يتحمل البرد. الفقمة كمان عندها دهون تحت الجلد للعزل.",
  "extraction_target": "ontology",
  "format_version": "1.0"
}
```

### Output JSON (اللي الـ LLM بترجعه)
```json
{
  "metadata": {
    "extraction_date": "2024-01-15",
    "source_text": "الأسد حيوان مفترس...",
    "language": "ar",
    "confidence_score": 0.92
  },
  "language_rules": [
    {
      "type": "morphological_pattern",
      "root": "أسد",
      "variations": ["الأسد", "أسود", "أسد"],
      "pos": "noun"
    }
  ],
  "concepts": [
    {
      "id": "feline_carnivore",
      "labels": ["الأسد", "ليث", "أسد"],
      "description": "حيوان مفترس يعيش في السافانا",
      "category": "animal"
    },
    {
      "id": "arctic_environment",
      "labels": ["الأرض المتجمدة", "القطب", "البيئة المتجمدة"],
      "description": "بيئة باردة جداً",
      "category": "environment"
    }
  ],
  "relations": [
    {
      "from": "feline_carnivore",
      "relation": "is_a",
      "to": "carnivore",
      "type": "classification"
    },
    {
      "from": "feline_carnivore",
      "relation": "lives_in",
      "to": "savanna",
      "type": "location"
    },
    {
      "from": "feline_carnivore",
      "relation": "has_property",
      "to": "thin_fur",
      "type": "physical_attribute",
      "causal_purpose": "adaptation_to_warm_climates"
    },
    {
      "from": "arctic_environment",
      "relation": "requires",
      "to": "thick_fur",
      "type": "environmental_requirement"
    },
    {
      "from": "arctic_environment",
      "relation": "has_property",
      "to": "extreme_cold",
      "type": "environmental_condition"
    },
    {
      "from": "thick_fur",
      "relation": "provides",
      "to": "thermal_insulation",
      "type": "functional",
      "value": "high"
    }
  ],
  "facts": [
    {
      "id": "fact_lion_savanna",
      "world": "reality",
      "subject": "feline_carnivore",
      "predicate": "lives_in",
      "object": "savanna",
      "confidence": 1.0
    },
    {
      "id": "fact_bear_arctic",
      "world": "arctic",
      "subject": "polar_bear",
      "predicate": "lives_in",
      "object": "arctic_environment",
      "confidence": 1.0
    },
    {
      "id": "fact_bear_fur",
      "world": "arctic",
      "subject": "polar_bear",
      "predicate": "has_property",
      "object": "thick_fur",
      "confidence": 1.0,
      "reason": "arctic_environment requires thick_fur for survival"
    }
  ],
  "inference_rules": [
    {
      "rule_id": "transitive_classification",
      "name": "Transitive is_a",
      "pattern": "X is_a Y AND Y is_a Z → X is_a Z",
      "priority": "high"
    },
    {
      "rule_id": "causal_adaptation",
      "name": "Environmental Adaptation",
      "pattern": "Environment E requires Property P AND Animal A lacks P AND A in E → A needs P",
      "priority": "high"
    }
  ]
}
```

---

## 7️⃣ الـ Prompt الكامل للـ LLM

### تلقينة الاستخراج (Extraction Prompt)

```
أنت مختص في استخراج المعرفة من النصوص العربية وتحويلها إلى بنية بيانات منظمة.

مهمتك: قراءة النص التالي واستخراج:
1. القواعد اللغوية (جذور، أنماط صرفية)
2. المفاهيم الرئيسية (concepts) والعلاقات بينها (relations)
3. الحقائق المذكورة صراحة أو ضمنياً
4. القواعس الاستدلالية المستخدمة

القيود المهمة:
- استخرج فقط ما هو موجود في النص أو مستنتج منه بوضوح
- لا تخترع مفاهيم جديدة خارج السياق
- ركز على العلاقات السببية والغرضية ("لماذا؟"، "عشان إيه؟")
- حدد reliability كل مفهوم (معلومة مباشرة = 1.0، مستنتجة = 0.7-0.8)
- استخدم معرّفات concept قياسية (مثلاً: "feline_carnivore" بدلاً من "أسد")

الفورمات المطلوب:
أرجع JSON بالتركيب التالي بالضبط:

{
  "metadata": { /* تفاصيل الاستخراج */ },
  "language_rules": [ /* القواعد اللغوية */ ],
  "concepts": [ /* المفاهيم */ ],
  "relations": [ /* العلاقات بين المفاهيم */ ],
  "facts": [ /* الحقائق */ ],
  "inference_rules": [ /* القواعس الاستدلالية */ ]
}

مثال من الاستخراج:

النص: "الأسد حيوان مفترس وعنده فرو خفيف عشان يتحمل حرارة السافانا."

الاستخراج:
```json
{
  "concepts": [
    { "id": "feline_carnivore", "labels": ["أسد"], "category": "animal" },
    { "id": "thin_fur", "labels": ["فرو خفيف"], "category": "physical_attribute" },
    { "id": "warm_climate", "labels": ["حرارة السافانا"], "category": "environment" }
  ],
  "relations": [
    {
      "from": "feline_carnivore",
      "relation": "is_a",
      "to": "carnivore",
      "type": "classification"
    },
    {
      "from": "feline_carnivore",
      "relation": "has_property",
      "to": "thin_fur",
      "type": "physical_attribute",
      "causal_purpose": "adaptation_to_warm_climates"
    }
  ]
}
```

الآن، استخرج من النص التالي:

[النص هنا]
```

---

## 8️⃣ مثال عملي كامل: عالم الحيوانات

### البيانات الأساسية للنموذج

#### 1. Knowledge Graph (animals_ontology.json)
```json
{
  "concepts": [
    {"id": "animal", "labels": ["حيوان", "كائن حي"]},
    {"id": "carnivore", "labels": ["مفترس"]},
    {"id": "feline_carnivore", "labels": ["أسد", "ليث"]},
    {"id": "polar_bear", "labels": ["دب قطبي"]},
    {"id": "thin_fur", "labels": ["فرو خفيف"]},
    {"id": "thick_fur", "labels": ["فرو سميك"]},
    {"id": "thermal_regulation", "labels": ["تنظيم حرارة"]},
    {"id": "arctic", "labels": ["القطب", "الأرض المتجمدة"]},
    {"id": "savanna", "labels": ["السافانا"]},
    {"id": "extreme_cold", "labels": ["برد شديد"]},
    {"id": "warm_climate", "labels": ["مناخ دافئ"]}
  ],
  "relations": [
    {
      "from": "feline_carnivore",
      "relation": "is_a",
      "to": "carnivore"
    },
    {
      "from": "carnivore",
      "relation": "is_a",
      "to": "animal"
    },
    {
      "from": "feline_carnivore",
      "relation": "lives_in",
      "to": "savanna"
    },
    {
      "from": "feline_carnivore",
      "relation": "has_property",
      "to": "thin_fur",
      "causal_purpose": "thermal_regulation_warm"
    },
    {
      "from": "thin_fur",
      "relation": "provides",
      "to": "poor_insulation"
    },
    {
      "from": "polar_bear",
      "relation": "lives_in",
      "to": "arctic"
    },
    {
      "from": "polar_bear",
      "relation": "has_property",
      "to": "thick_fur",
      "causal_purpose": "thermal_regulation_cold"
    },
    {
      "from": "thick_fur",
      "relation": "provides",
      "to": "good_insulation"
    },
    {
      "from": "arctic",
      "relation": "has_environment",
      "to": "extreme_cold"
    },
    {
      "from": "extreme_cold",
      "relation": "requires",
      "to": "good_insulation"
    }
  ]
}
```

#### 2. السؤال
```
"لو الأسد عاش في القطب، ماذا يحتاج عشان يتحمل البرد؟"
```

#### 3. خطوات المعالجة

**الخطوة 1: Parsing**
- نوع السؤال: conditional + what
- الشرط: "الأسد عاش في القطب"
- الاستفهام: "ماذا يحتاج"

**الخطوة 2: Lexicon Mapping**
- "الأسد" → feline_carnivore
- "القطب" → arctic
- "يحتاج" → requires (relation)

**الخطوة 3: Causal Reasoning**
```
1. arctic has extreme_cold
2. extreme_cold requires good_insulation
3. feline_carnivore currently has thin_fur
4. thin_fur provides poor_insulation
5. NEED: good_insulation
→ SOLUTION: thick_fur (provides good_insulation)
```

**الخطوة 4: Analogy**
```
1. Find who else needs good_insulation in arctic
2. polar_bear has good_insulation via thick_fur
3. feline_carnivore and polar_bear are both: mammals, carnivores
4. → feline_carnivore can potentially adapt like polar_bear
```

**الخطوة 5: Food Chain**
```
1. Arctic inhabitants that are carnivore prey
2. seal, fish, lemming are in arctic
3. feline_carnivore (carnivore) can eat them
→ Alternative food sources available
```

#### 4. الرد
```
سلسلة الاستدلال:
1. تعريف البيئة: القطب → بيئة باردة جداً (extreme_cold)
2. متطلبات البيئة: البرد الشديد → يحتاج عزل حراري جيد
3. خصائص الأسد الحالية: فرو خفيف → عزل حراري ضعيف
4. الفجوة: يحتاج الأسد إلى عزل حراري أفضل
5. البحث عن حل: من يستخدم عزل حراري جيد؟ → الدب القطبي
6. مقارنة: الأسد والدب القطبي ثدييات مفترسة (متشابهة)
7. الحل: يحتاج الأسد إلى فرو سميك مثل الدب القطبي
8. غذاء جديد: في القطب يقدر يأكل الفقمات والأسماك

الرد (بشخصية "الخبير المرح"):
"يا صاحبي، لو الأسد عاش في القطب، أول حاجة محتاج يغيّر فروه!
الفرو الخفيف بتاعه مش هيتحمل البرد الشديد هناك.
الحل؟ فرو سميك زي الدب القطبي اللي بيعيش هناك — ده هيديه عزل حراري قوي.
وبعدين، يبقى عايز يبحث عن أكل جديد: فقمات وأسماك، مش الحيوانات اللي بياكلها في السافانا.
يعني قصة كاملة من التكيف!"

معامل الثقة: 0.95
(استدلال سببي موجّه، وليس تخمين عشوائي)
```

---

## 9️⃣ خارطة الطريق (Implementation Roadmap)

### المرحلة 0: MVP صغير (أسبوع 1-2)
**الهدف**: إثبات الفكرة تشتغل

**المخرجات:**
- ✅ `animals_ontology.json` (مجموعة صغيرة: أسد، دب، حيتويات أساسية)
- ✅ `graph_handler.py` (تحميل الـ graph، وراثة بسيطة)
- ✅ `simple_reasoner.py` (استدلال تصنيفي أساسي)
- ✅ واجهة terminal بسيطة تسأل "هل الأسد حيوان؟" وترد مع سلسلة استدلال

**المقاييس:**
- الاستدلال يرجع النتيجة الصحيحة
- Trace chain واضحة ومفهومة

---

### المرحلة 1: Morphology + Disambiguation (أسبوع 2-3)
**الهدف**: فهم الأسئلة بصيغ مختلفة

**المخرجات:**
- ✅ `morphology_analyzer.py` (تفكيك الكلمات العربية)
- ✅ `disambiguation_engine.py` (Spreading Activation)
- ✅ `lexicon_handler.py` (قاموس ديناميكي)

**الاختبارات:**
- "الأسد" = "الأسود" (تصريفات)
- "هل" و"ما" و"هل" = جميعها أسئلة استفهامية

---

### المرحلة 2: Causal Reasoning + Analogy (أسبوع 3-4)
**الهدف**: الإجابة على أسئلة افتراضية

**المخرجات:**
- ✅ `causal_reasoner.py` (بحث عن الأسباب والحلول)
- ✅ `analogy_engine.py` (البحث عن نظائر)
- ✅ توسيع `animals_ontology.json` بعلاقات سببية

**الاختبارات:**
- "لو الأسد في القطب؟" ← يستنتج الفرو السميك
- "ماذا يأكل الأسد في القطب؟" ← يبحث عن نظائر

---

### المرحلة 3: World Management + Conflict Resolution (أسبوع 4-5)
**الهدف**: التعامل مع عوالم متعددة

**المخرجات:**
- ✅ `world_manager.py` (تبديل العوالم)
- ✅ `conflict_resolver.py` (معالجة التعارضات)
- ✅ توسيع `facts.json` بحقائق من عوالم مختلفة

**الاختبارات:**
- "في عالم خيالي، الشمس تشرق من الغرب" ← يحفظها في عالم "خيالي"
- "هل الشمس تشرق من الشرق؟" ← في الواقع نعم، في الخيالي لا

---

### المرحلة 4: Response Generation + Persona (أسبوع 5-6)
**الهدف**: ردود طبيعية مع شخصية

**المخرجات:**
- ✅ `response_generator.py` (templates + personalization)
- ✅ `personas.json` (شخصيات مختلفة)

**الاختبارات:**
- نفس السؤال بشخصيات مختلفة = ردود بأساليب مختلفة

---

### المرحلة 5: Conversation Management (أسبوع 6-7)
**الهدف**: محادثات متعددة الأدوار

**المخرجات:**
- ✅ `conversation_manager.py` (تذكر السياق)
- ✅ `entity_resolver.py` (معرفة من نتكلم عنه)

**الاختبارات:**
- "فيه أسد في السافانا" ← حفظ السياق
- "كام سرعته؟" ← معرفة إننا بتتكلم عن الأسد اللي ذكرنا

---

### المرحلة 6: LLM Integration + Knowledge Extraction (أسبوع 7-8)
**الهدف**: تعليم النموذج من نصوص جديدة

**المخرجات:**
- ✅ `llm_extractor.py` (يستخدم الـ prompt في الفصل 7)
- ✅ `json_validator.py` (التحقق من صيغة الـ JSON)
- ✅ واجهة يدخل فيها نص وترجع الـ JSON المستخرج

**الاختبارات:**
- أعط النموذج قصة جديدة → استخرج منها معرفة جديدة

---

## 🔟 البرنامج الأول (MVP)

### الملفات المطلوبة

```
neuro-symbolic-ai/
├── data/
│   ├── animals_ontology_small.json      # قاعدة المفاهيم (صغيرة)
│   ├── animals_facts.json                # قاعدة الحقائق
│   └── animals_language_rules.json       # قواعد اللغة البسيطة
│
├── src/
│   ├── graph_handler.py                  # تحميل وإدارة الـ graph
│   ├── simple_reasoner.py                # الاستدلال الأساسي
│   ├── response_generator_simple.py      # توليد ردود بسيطة
│   └── main.py                           # البرنامج الرئيسي
│
└── tests/
    ├── test_basic_reasoning.py           # اختبارات الاستدلال
    └── test_queries.py                   # اختبارات الأسئلة
```

### الأسئلة المختبرة في MVP

```
1. "هل الأسد حيوان؟"
   الإجابة المتوقعة: نعم (مع سلسلة استدلال)

2. "هل الأسد مفترس؟"
   الإجابة المتوقعة: نعم (مع سلسلة استدلال)

3. "أين يعيش الأسد؟"
   الإجابة المتوقعة: في السافانا

4. "لو الأسد في القطب، ماذا يحتاج؟"
   الإجابة المتوقعة: فرو سميك (مع سلسلة استدلال سببي)

5. "ما الفرق بين الأسد والدب القطبي؟"
   الإجابة المتوقعة: كلاهما مفترس لكن بفرو مختلف (مع شرح السبب)
```

---

## 📝 ملخص المعمارية

### المراحل من النص إلى الرد:
```
[النص/السؤال]
    ↓
[Morphology + Syntax]
    ↓
[Lexicon Lookup + Disambiguation]
    ↓
[Question Analysis]
    ↓
[World Selection]
    ↓
[Reasoning Engine: Inheritance + Causal + Analogy]
    ↓
[Trace Chain Assembly]
    ↓
[Response Generation]
    ↓
[Persona Application]
    ↓
[Conversation Storage]
    ↓
[Final Output]
```

### ما الذي يجعل هذا النظام مختلفاً:

| الميزة | LLM | نظامنا |
|---|---|---|
| الصدق | احتمالي (هلوسات ممكنة) | مضمون (لا هلوسات، أو "مش عارف") |
| الشفافية | صندوق أسود | سلسلة استدلال كاملة |
| التعليم | freeze بعد التدريب | مستمر طول الوقت |
| الموثوقية | أحسن في الحوار المفتوح | أحسن في المجال المحدود |
| السرعة | بطيء (استدعاء API) | سريع (محلي، رمزي) |

---

**جاهز للتنفيذ؟ الآن يمكنك إعطاء هذه الخطة لأي AI developer ويبدأ في البناء فوراً.**
