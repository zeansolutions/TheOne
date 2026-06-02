# TheOne Advanced Roadmap — Integrating LEGEND Ideas

## 🎯 الهدف الاستراتيجي

دمج الأفكار المتقدمة من مشروع LEGEND في TheOne، مع **الحفاظ الصارم على مبدأ: LLM كمُعلّم فقط (Training Phase)، صفر LLM في Runtime**.

---

## ⚡ الشرط الذهبي (Non-Negotiable)

```
┌──────────────────────────────────────────────────┐
│ TRAINING PHASE (one-time, LLM allowed)          │
├──────────────────────────────────────────────────┤
│ User/LLM → extracts knowledge → JSON            │
│          ↓                                       │
│ TheOne stores in DB                             │
│          ↓                                       │
│ ✅ LLM's role ENDS                              │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ RUNTIME PHASE (all the time, ZERO LLM)          │
├──────────────────────────────────────────────────┤
│ User Question → Symbolic Reasoning Engine       │
│              → Graph Operations                 │
│              → Inference Rules (JSON-based)    │
│              → Spreading Activation             │
│              → Persona Selection                │
│              → Response                         │
│                                                  │
│ ❌ NO LLM calls                                 │
│ ❌ NO API requests                              │
│ ✅ 100% Deterministic, Transparent, Fast       │
└──────────────────────────────────────────────────┘
```

**كل ميزة جديدة يجب أن تلتزم بهذا الشرط.**

---

## 📋 المراحل والأولويات

### Phase 1 (الشهر الأول) — Foundation

#### P0: Relation-Agnostic Transitive Chaining
**الحالة الحالية:**
```python
# قاعدة محددة لكل علاقة
if is_a(A, B) and is_a(B, C):
    infer is_a(A, C)
```

**المشكلة:** لو أضاف المستخدم علاقة جديدة "resembles"، النظام ما يعرف إنها متعدية.

**الحل المطلوب:**

1. **اكتشاف تلقائي للعلاقات المتعدية:**
```json
// in knowledge_base.json
{
  "relations": [
    {
      "id": "is_a",
      "transitive": true,
      "decay": 0.0
    },
    {
      "id": "causes",
      "transitive": true,
      "decay": 0.1
    },
    {
      "id": "resembles",
      "transitive": true,
      "decay": 0.3
    }
  ]
}
```

2. **محرك Transitive Chaining العام:**
```python
class TransitiveChainingEngine:
    def apply_transitive_rule(self, relation_id, depth=3):
        """
        لأي علاقة متعدية، ابحث عن السلاسل وطبق القاعدة
        مع حساب confidence decay
        """
        # البحث عن: (A, relation, B) و (B, relation, C)
        # النتيجة: (A, relation, C) بـ confidence = conf(A,B) * conf(B,C) * (1 - decay)
        pass
```

3. **التطبيق:**
- عند تحميل DB: احسب كل العلاقات المتعدية تلقائياً
- عند إضافة fact جديد: طبق الـ transitive rules على الفور
- في الـ reasoning: استخدم النتائج المحسوبة مباشرة (لا runtime calculation)

**الـ LLM:** لا دور له. كل شيء رياضي محض.

---

#### P1: Thought Experiment Sandbox
**الحالة الحالية:**
```
سؤال افتراضي: "لو الأسد عاش في القطب؟"
المشكلة: قد تضيف facts افتراضية للـ Graph الحقيقي
```

**الحل المطلوب:**

1. **Sandbox Manager:**
```python
class SandboxManager:
    def __init__(self, graph):
        self.original_graph = graph
        self.sandbox_graph = None
    
    def enter_sandbox(self, scenario):
        """
        انسخ الـ graph → اشتغل عليها الافتراضيات فقط
        """
        self.sandbox_graph = deepcopy(self.original_graph)
        self.sandbox_graph.metadata["is_sandbox"] = True
        self.sandbox_graph.metadata["scenario"] = scenario
    
    def exit_sandbox(self):
        """
        اتخلص من الـ sandbox → الـ original سليم
        """
        self.sandbox_graph = None
        return True
```

2. **التطبيق في reasoning:**
```python
# عند كشف سؤال افتراضي:
if question.has_conditional():  # "لو"، "افترض"
    sandbox.enter_sandbox(question.scenario)
    result = reasoning_engine.infer(question, sandbox.sandbox_graph)
    sandbox.exit_sandbox()
    return result
else:
    # سؤال عادي على الـ real graph
    return reasoning_engine.infer(question, graph)
```

3. **الـ LLM:** لا دور له. Sandbox = copy-on-write محض.

---

### Phase 2 (الشهر الثاني) — Maintenance + Improvements

#### P1: Cognitive Sleep Cycle
**الغرض:** تنظيف الـ Graph من الأخطاء والتكرارات

**الحل المطلوب:**

1. **Sleep Mode مُشغّل يدوياً:**
```bash
./start.sh sleep --depth=2 --cleanup
```

2. **عمليات الـ Sleep:**

```python
class CognitiveSleepCycle:
    def run_sleep(self):
        """
        تنظيف شامل للـ Graph
        """
        # 1. Deduplication
        self.merge_similar_nodes()  # "اسد" + "أسد" → "أسد"
        
        # 2. Weak edge removal
        self.remove_low_confidence_edges(threshold=0.1)
        
        # 3. Triangle strengthening
        self.strengthen_transitive_paths()  # قوّي الحواف في الثلاثات القوية
        
        # 4. Isolated nodes detection
        self.flag_isolated_nodes()  # "في انتظار الحذف"
        
        # 5. Redundancy cleanup
        self.remove_redundant_facts()  # حقائق موجودة ترتب من حقائق أخرى
        
        # 6. Persistence
        self.save_cleaned_graph()
```

3. **الـ LLM:** لا دور له. كل شيء heuristics على البيانات الموجودة.

---

#### P2: Fuzzy-Modal Logic
**الغرض:** تعليم ألطف يعكس عدم اليقين

**الحل المطلوب:**

1. **توسيع التعليم ليقبل modalities:**
```json
// تعليم قديم:
{ "subject": "أسد", "relation": "eats", "object": "meat", "confidence": 0.95 }

// تعليم جديد (مع modality):
{
  "subject": "أسد",
  "relation": "eats",
  "object": "meat",
  "confidence": 0.95,
  "modality": "usually",  // usually, sometimes, rarely, possibly
  "frequency": 0.8
}
```

2. **محرك التفسير:**
```python
def interpret_modality(modality):
    modalities = {
        "always": 1.0,
        "usually": 0.8,
        "sometimes": 0.5,
        "rarely": 0.2,
        "possibly": 0.1
    }
    return modalities.get(modality, 0.5)

# عند الاستدلال:
final_confidence = base_confidence * interpret_modality(modality)
```

3. **الـ LLM:** لا دور له. الـ modality تُقرر عند التعليم يدوياً (أو من LLM في Phase التدريب بس).

---

### Phase 3 (الشهر الثالث) — Proactive Learning

#### P2: Active Curiosity Engine
**الغرض:** النظام يبادر بطلب معرفة ناقصة

**الحل المطلوب:**

1. **كشف Knowledge Gaps:**
```python
class CuriosityEngine:
    def detect_gaps(self):
        """
        ابحث عن عقد في الـ graph ناقصة معلومات
        """
        gaps = []
        for node in graph.nodes:
            # هل العقدة لها سياق (مثل "اسد")؟
            if node.context_related and node.relations_count < 5:
                gaps.append({
                    "node": node,
                    "missing_relations": self.infer_missing(node)
                })
        return gaps
    
    def ask_user(self, gap):
        """
        عرض السؤال للمستخدم
        """
        print(f"🤔 لاحظت: {gap['node'].label} ناقص معلومات")
        print(f"   المتوقع: {', '.join(gap['missing_relations'])}")
        print(f"   تقدر تساعدني؟")
```

2. **التطبيق:**
```bash
./start.sh curious --interval=300  # كل 5 دقايق
```

3. **الـ LLM:** لا دور له. الـ gap detection = تحليل graph محض.

---

## 🔧 تفاصيل التنفيذ

### ملفات جديدة مطلوبة:

```
src/
├── reasoner/
│   ├── transitive_chaining.py       [P0] — محرك العلاقات المتعدية
│   ├── sandbox_manager.py           [P1] — Thought Experiment
│   └── curiosity_engine.py          [P2] — Active Curiosity
├── maintenance/
│   └── sleep_cycle.py               [P1] — Cognitive Sleep
└── enrichment/
    └── fuzzy_modal.py               [P2] — Fuzzy-Modal Logic

data/
├── relations_metadata.json          [جديد] — خصائص العلاقات
└── modalities.json                  [جديد] — قائمة الـ modalities
```

### تعديلات على الملفات الموجودة:

```python
# src/reasoner/inference_engine.py
# أضيف: استدعاء TransitiveChainingEngine
# أضيف: check if sandbox mode active

# src/manager/conversation_manager.py
# أضيف: sandbox context tracking

# src/manager/knowledge_manager.py
# أضيف: fuzzy confidence handling
```

---

## ✅ Testing Strategy

لكل ميزة:

```python
# tests/test_transitive_chaining.py
def test_transitive_decay():
    """يجب أن تنخفض الـ confidence مع السلاسل الطويلة"""
    
# tests/test_sandbox.py
def test_sandbox_isolation():
    """الـ sandbox changes ما تؤثر على الـ real graph"""

# tests/test_sleep_cycle.py
def test_deduplication():
    """الـ duplicates تُدمج بالكامل"""
```

---

## 🚀 الترتيب الزمني المقترح

| المرحلة | الأسبوع | الأولوية | الميزات |
|---|---|---|---|
| **Phase 1** | 1-4 | P0+P1 | Transitive Chaining + Sandbox |
| **Phase 2** | 5-8 | P1+P2 | Sleep Cycle + Fuzzy-Modal |
| **Phase 3** | 9-12 | P2 | Curiosity Engine |

---

## 🎯 القائمة النهائية (للنموذج البرمجي)

**ابدأ مباشرة بـ:**

1. ✅ تحديث `relations_metadata.json` بـ `transitive` + `decay`
2. ✅ بناء `TransitiveChainingEngine`
3. ✅ بناء `SandboxManager`
4. ✅ إضافة sandwich detection في `conversation_manager.py`
5. ✅ كتابة tests لكل ميزة

**اتفقت معاك أن:**
- ❌ لا LLM في Runtime
- ✅ كل شيء Symbolic + Deterministic
- ✅ كل ميزة مستقلة (modular)
- ✅ كل شيء قابل للاختبار (testable)

---

**النموذج البرمجي:** ابدأ من الآن.
