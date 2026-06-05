# 📋 خطة تنفيذية شاملة: تطوير محرك TheOne

**التاريخ:** 5 يونيو 2026  
**الهدف:** تطوير محرك TheOne من نظام اعتماد Regex ثابت إلى نظام ذاتي التعلم قابل للتوسع  
**الالتزام:** Zero-Hardcoding، Zero-LLM (بدون نماذج لغوية داخلية)

---

## 📑 فهرس الخطة

1. [نظرة عامة على المراحل](#مراحل-التطوير)
2. [المرحلة 1: تطهير الكود وبناء NLU الذكي](#المرحلة-1-تطهير-الكود-وبناء-nlu-الذكي)
3. [المرحلة 2: توسيع قاعدة المعرفة](#المرحلة-2-توسيع-قاعدة-المعرفة)
4. [المرحلة 3: البنية التحتية والتحسينات](#المرحلة-3-البنية-التحتية-والتحسينات)
5. [المرحلة 4: الاختبار والتحقق](#المرحلة-4-الاختبار-والتحقق)

---

## مراحل التطوير

| المرحلة | المدة المتوقعة | الهدف | الأولوية |
|:---|:---|:---|:---:|
| **1. تطهير الكود + NLU الذكي** | أسبوعان | إزالة Regex والـ Hardcoding، بناء محرك التعلم | 🔴 حرجة |
| **2. توسيع قاعدة المعرفة** | شهر - شهران | جمع ملايين الحقائق والمفاهيم | 🔴 حرجة |
| **3. البنية التحتية** | أسبوعان | النقل من JSON إلى Database، تجزئة الملفات | 🟡 مهمة |
| **4. الاختبار والتحقق** | أسبوع | اختبارات شاملة وتصحيح الأخطاء | 🟡 مهمة |

---

## المرحلة 1: تطهير الكود وبناء NLU الذكي

**المدة المتوقعة:** أسبوعان  
**الهدف:** تحويل نظام فهم اللغة من Regex ثابت إلى نظام ديناميكي رمزي ذاتي التعلم

### 1.1 المكونات البرمجية الجديدة (NEW)

#### `src/reasoner/pattern_matcher.py` (NEW)
**الوصف:** محرك مطابقة الأنماط الرمزي العام

**المسؤوليات:**
- قراءة قوالب الجمل من `language_rules.json` (مصفوفة `syntactic_patterns`)
- تفكيك جملة المستخدم إلى مصفوفة كلمات
- مطابقة الكلمات مع القوالب باستخدام خوارزمية تطابق رمزية (Symbolic Matching)
- دعم المتغيرات (Variables) مثل `?X` و `?Y` لاستخراج الكيانات
- دعم المطابقة المرنة (Fuzzy Matching) باستخدام Levenshtein distance

**الواجهة المتوقعة:**
```python
class GenericPatternMatcher:
    def __init__(self, language_rules_path: str):
        """تحميل الأنماط من language_rules.json"""
        self.patterns = self._load_patterns(language_rules_path)
    
    def match(self, text: str) -> Optional[MatchResult]:
        """
        محاولة مطابقة النص مع الأنماط المحفوظة
        return: MatchResult(intent, extracted_entities, confidence) أو None
        """
        tokens = self._tokenize(text)
        for pattern in self.patterns:
            result = self._try_pattern(tokens, pattern)
            if result and result.confidence > 0.7:
                return result
        return None
    
    def _tokenize(self, text: str) -> List[str]:
        """تقسيم النص إلى كلمات مع الحفاظ على الترتيب"""
        pass
    
    def _try_pattern(self, tokens: List[str], pattern: Dict) -> Optional[MatchResult]:
        """محاولة مطابقة مصفوفة الكلمات مع نمط محدد"""
        pass
    
    def _fuzzy_match(self, word: str, pattern_token: str, threshold: float = 0.8) -> bool:
        """مطابقة ضبابية للتعامل مع الأخطاء الإملائية"""
        pass
```

**الملف في المشروع:** `src/reasoner/pattern_matcher.py` (حوالي 200-250 سطر)

---

#### `src/reasoner/learning_engine.py` (NEW)
**الوصف:** محرك التعلم التفاعلي (Interactive Bootstrapper)

**المسؤوليات:**
- التدخل عند فشل `PatternMatcher`
- مقارنة الكلمات المجهولة بالمفاهيم المعروفة في الجراف
- طرح أسئلة استيضاحية على المستخدم
- استنتاج النمط الجديد وحفظه في `language_rules.json`

**الواجهة المتوقعة:**
```python
class InteractiveBootstrapper:
    def __init__(self, graph_handler, language_rules_path: str):
        self.graph = graph_handler
        self.rules_path = language_rules_path
    
    def ask_for_clarification(self, text: str, unknown_tokens: List[str]) -> Optional[Dict]:
        """
        عند عدم فهم النظام لجملة:
        1. يحلل الكلمات المعروفة
        2. يسأل المستخدم عن المقصد
        3. يستنتج النمط ويحفظه
        return: النمط الجديد الذي تم تعلمه أو None
        """
        pass
    
    def _match_unknown_to_concepts(self, tokens: List[str]) -> Dict[str, List[str]]:
        """ربط الكلمات المجهولة بالمفاهيم المعروفة من الجراف"""
        pass
    
    def _propose_intent(self, known_tokens: List[str], context: Dict) -> str:
        """اقتراح نية محتملة بناءً على الكلمات المعروفة"""
        pass
    
    def _save_new_pattern(self, pattern: Dict) -> bool:
        """حفظ النمط الجديد في language_rules.json"""
        pass
```

**الملف في المشروع:** `src/reasoner/learning_engine.py` (حوالي 250-300 سطر)

---

### 1.2 تعديلات على الملفات الموجودة (MODIFY)

#### `src/simple_reasoner.py` (MODIFY)
**التغييرات:**
- **حذف:** كافة أنماط Regex الثابتة (حوالي 60 نمط)
- **حذف:** كافة الكلمات العربية/الإنجليزية المكتوبة يدوياً في كود البحث عن النوايا
- **استبدال:** دالة `_route_logical_reasoning()` الطويلة بنداء بسيط:
  ```python
  def process(self, user_input: str) -> Response:
      # محاولة المطابقة أولاً
      match = self.pattern_matcher.match(user_input)
      if match:
          intent = match.intent
          entities = match.extracted_entities
      else:
          # فشلت المطابقة، ندخل وضع التعلم
          match = self.learning_engine.ask_for_clarification(user_input, ...)
          if match:
              intent = match.intent
              entities = match.extracted_entities
          else:
              return Response(status="failed", message="لم أفهم")
      
      # باقي الكود كما هو
      return self._handle_intent(intent, entities)
  ```

**عدد السطور المحذوفة:** حوالي 400-500 سطر
**عدد السطور المضافة:** حوالي 20-30 سطر (انخفاض صافي)

---

#### `src/entity_resolver.py` (MODIFY)
**التغييرات:**
- **حذف:** قائمة الضمائر المكتوبة يدوياً:
  ```python
  # OLD (DELETE)
  ARABIC_PRONOUNS = ['هو', 'هي', 'هم', 'هن', 'أنا', 'أنت', ...]
  ```
- **استبدال:** بقراءة ديناميكية:
  ```python
  # NEW
  def __init__(self, language_rules_path: str):
      self.pronouns = self._load_pronouns_from_json(language_rules_path)
  
  def _load_pronouns_from_json(self, path: str) -> Dict[str, List[str]]:
      with open(path) as f:
          data = json.load(f)
          return data.get("pronouns", {})
  ```

**عدد السطور المحذوفة:** حوالي 50-100 سطر

---

#### `src/world_manager.py` (MODIFY)
**التغييرات:**
- **حذف:** الكلمات الثابتة للعوالم (مثل `"في عالم خيالي"`, `"في الحقيقة"`, etc.)
- **استبدال:** بنمط ديناميكي يقرأ تعريفات العوالم من `language_rules.json`

**عدد السطور المحذوفة:** حوالي 30-50 سطر

---

#### `src/multilingual_persona_engine.py` (MODIFY)
**التغييرات:**
- إذا كانت تحتوي على نصوص مكتوبة يدوياً (Hardcoded)، يتم سحبها إلى JSON
- الحفاظ على المنطق الرياضي/الخوارزمي

**عدد السطور المحذوفة:** حوالي 20-40 سطر (إن وجدت)

---

#### `src/conversation_manager.py` (MODIFY)
**التغييرات:**
- إذا كانت تحتوي على نصوص ثابتة (رسائل الترحيب، etc.)، يتم سحبها إلى JSON

**عدد السطور المحذوفة:** حوالي 10-20 سطر (إن وجدت)

---

### 1.3 تحديثات قاعدة البيانات (DATA)

#### `data/language_rules.json` (MODIFY)
**الإضافات:**
- إضافة مصفوفة `syntactic_patterns` للأنماط النحوية:
  ```json
  {
    "syntactic_patterns": [
      {
        "id": "query_is_a_01",
        "pattern": ["هل", "?X", "هو", "?Y"],
        "intent": "is_a_query",
        "mapping": {"subject": "?X", "object": "?Y"},
        "confidence": 1.0,
        "language": "ar"
      },
      {
        "id": "query_location_01",
        "pattern": ["أين", "?ACTION", "?X"],
        "intent": "where_query",
        "mapping": {"subject": "?X", "relation": "?ACTION"}
      },
      // ... أنماط أخرى
    ],
    "pronouns": {
      "ar": {
        "singular": ["هو", "هي", "أنا"],
        "plural": ["هم", "هن", "نحن"]
      },
      "en": {
        "singular": ["he", "she", "I"],
        "plural": ["they", "we"]
      }
    },
    "world_patterns": {
      "fictional": ["في عالم خيالي", "في الخيال", "تخيل"],
      "reality": ["في الحقيقة", "في الواقع", "فعلاً"]
    }
  }
  ```

**ملاحظة:** الملف موجود لكن سيتم توسيعه لإضافة الأنماط الديناميكية

---

#### `data/prompts/final_prompt.md` (MODIFY - اختياري)
**الملاحظة:** يُستخدم هذا الملف عند توليد بيانات من مصادر خارجية (يتم شرحه لاحقاً في المرحلة 2)

---

### 1.4 ملخص التغييرات في المرحلة 1

| الملف | النوع | السطور المحذوفة | السطور المضافة | النتيجة |
|:---|:---:|---:|---:|:---|
| `simple_reasoner.py` | MODIFY | ~450 | ~30 | انخفاض صافي: **-420 سطر** |
| `entity_resolver.py` | MODIFY | ~75 | ~20 | انخفاض صافي: **-55 سطر** |
| `world_manager.py` | MODIFY | ~40 | ~10 | انخفاض صافي: **-30 سطر** |
| `pattern_matcher.py` | NEW | 0 | ~230 | إضافة: **+230 سطر** |
| `learning_engine.py` | NEW | 0 | ~280 | إضافة: **+280 سطر** |
| `language_rules.json` | MODIFY | 0 | ~100 صف | توسيع البيانات |
| **المجموع** | - | **~565** | **~670** | **صافي: +105** |

**النتيجة النهائية:** تقليل الكود الثابت بـ 505 أسطر مع إضافة نظام ديناميكي متقدم.

---

## المرحلة 2: توسيع قاعدة المعرفة

**المدة المتوقعة:** شهر - شهران  
**الهدف:** بناء قاعدة معرفة ضخمة وعملية

**ملاحظة مهمة:** هذه المرحلة تتطلب عمل يدوي من المستخدم (جمع البيانات، التحرير، etc.) مع توفير أدوات برمجية تساعد.

### 2.1 توصيات للمستخدم (USER RECOMMENDATIONS)

#### التوصية 1: اختيار مجال متخصص (Domain Selection)
**النقطة:** بدلاً من محاولة بناء نظام عام يغطي جميع المعارف، ركز على مجال واحد في البداية.

**مقترح المجالات:**
- **الطب والصحة:** معلومات موثوقة، استخدام عملي واضح
- **التعليم:** معلومات منسقة، سهل البحث
- **القانون:** نصوص محددة، استشارات موثوقة
- **التصنيع/الحِرف:** معلومات إجرائية، استخدام عملي مباشر

**الفائدة:**
- نظام متخصص "عبقري" في مجاله أفضل من نظام عام ضعيف
- يمكن توسيعه للمجالات الأخرى لاحقاً

#### التوصية 2: استيراد البيانات من مصادر مفتوحة
**المصادر المقترحة:**
- **Wikidata** (wikidata.org) — قاعدة معرفة ضخمة
- **ConceptNet** (conceptnet.io) — شبكة معرفية متعددة اللغات
- **DBpedia** — معلومات منظمة من Wikipedia
- **Wikipedia نفسها** — نصوص منظمة وموثوقة

**أداة الاستيراد (WILL BE PROVIDED):**
```
src/tools/data_importer.py
- تحويل تنسيقات Wikidata/ConceptNet إلى JSON متوافق مع TheOne
- تصفية المعلومات وحذف البيانات المشكوك فيها
- إضافة درجات ثقة (Confidence Scores)
```

#### التوصية 3: توسيع قاموس اللغة
**ما المطلوب:**
- 50,000+ كلمة عربية (إن كنت تستهدف العربية)
- أو 100,000+ كلمة إنجليزية

**المصادر:**
- **Aramorph** — قاموس عربي شامل
- **MADAMIRA** — معالج عربي متقدم
- **English WordNet** — للإنجليزية

**الأداة المقترحة (يمكنك البحث عنها):**
```
تحويل قوامس مفتوحة إلى صيغة JSON بسيطة:
{
  "word": "أسد",
  "lemma": "أسد",
  "pos": "noun",
  "meanings": [
    {"definition": "حيوان مفترس", "category": "animal"},
  ]
}
```

#### التوصية 4: بناء مجموعة قواعد استدلال (Inference Rules)
**ما المطلوب:** 500+ قاعدة منطقية من مثل:
- `if (X is_a Y) and (Y has property Z) then (X has property Z)`
- `if (X eats Y) and (Y eats Z) then (food_chain X→Y→Z)`
- `if (X is_opposite Y) then (not (X and Y can be true simultaneously))`

**آلية الجمع:**
- **يدوياً:** خبير يكتب القواعس مباشرة في `inference_rules.json`
- **شبه آلي:** استخدام أداة خارجية (مثل ChatGPT أو Claude) **لتوليد** القواعس ثم **مراجعتك** لها يدوياً

---

### 2.2 الأدوات البرمجية (NEW TOOLS)

#### `src/tools/data_importer.py` (NEW)
**الوصف:** أداة استيراد البيانات من مصادر خارجية

**المسؤوليات:**
- قراءة ملفات Wikidata/ConceptNet/JSON
- تحويلها إلى صيغة TheOne المتوافقة
- إضافة درجات ثقة وأوزان
- حفظ في `data/` مع تجنب التكرار

**مثال الاستخدام:**
```python
from src.tools.data_importer import WikidataImporter

importer = WikidataImporter()
entities = importer.import_wikidata_dump("wikidata_entities.json", domain="animal")
importer.export_to_theone_format(entities, "data/animal_ontology.json")
```

---

#### `src/tools/data_validator.py` (NEW)
**الوصف:** التحقق من صحة البيانات المستوردة

**المسؤوليات:**
- التحقق من عدم تضارب الحقائق
- حذف البيانات المشكوك فيها (confidence < threshold)
- اكتشاف والدمج المفاهيم المكررة

---

### 2.3 نمو قاعدة المعرفة المتوقع

**الحالة الحالية:**
- المفاهيم: 17
- الحقائق: 5
- القاموس: ~500 كلمة

**بعد المرحلة 2 (متخصص في مجال واحد):**
- المفاهيم: 10,000 - 50,000
- الحقائق: 100,000 - 500,000
- القاموس: 20,000 - 50,000 كلمة
- حجم البيانات: 50 MB - 200 MB

**التوقع المستقبلي (توسيع تدريجي):**
- المفاهيم: 500,000+
- الحقائق: 5,000,000+
- حجم البيانات: 1 GB+

---

## المرحلة 3: البنية التحتية والتحسينات

**المدة المتوقعة:** أسبوعان  
**الهدف:** تحسين الأداء والصيانة

### 3.1 النقل من JSON إلى Database (MODIFY)

#### المشكلة الحالية:
- ملفات JSON محملة بالكامل في الذاكرة
- عند ملايين الحقائق، سيستهلك GB من الـ RAM
- عمليات البحث بطيئة مع نمو البيانات

#### الحل المقترح:

##### `src/persistence/graph_database.py` (NEW)
**الخيار 1: SQLite (بسيط وموصى به)**
```python
class GraphDatabaseSQLite:
    """تخزين الجراف في SQLite"""
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_schema()
    
    def _create_schema(self):
        """إنشاء الجداول:
        - concepts (id, name, category, labels, confidence)
        - relationships (source_id, target_id, relation_type, confidence, world)
        - inference_rules (id, rule_json, priority)
        """
        pass
    
    def add_concept(self, concept: Dict) -> int:
        """إضافة مفهوم جديد"""
        pass
    
    def add_relationship(self, source_id: int, target_id: int, relation: Dict) -> bool:
        """إضافة علاقة"""
        pass
    
    def query_concepts(self, filters: Dict) -> List[Dict]:
        """استعلام المفاهيم بشروط"""
        pass
    
    def close(self):
        """إغلاق قاعدة البيانات"""
        pass
```

**الفائدة:**
- ✅ سهل الاستخدام
- ✅ لا متطلبات سيرفر
- ✅ محلي 100%
- ✅ أداء جيد حتى ملايين الحقائق

##### `src/persistence/graph_database.py` — الخيار 2: Neo4j (متقدم)
**بدلاً من SQLite، يمكن استخدام Neo4j المرخص مجاناً للاستخدام المحلي**
- أداء أفضل للاستعلامات المعقدة
- تصور الجراف سهل
- دعم Cypher Query Language

**الملاحظة:** Neo4j قد يكون معقداً للبدء، SQLite أفضل للبداية.

---

#### `src/graph_handler.py` (MODIFY)
**التغيير:**
- استبدال `networkx.DiGraph()` (محمل في الذاكرة) بـ `GraphDatabaseSQLite`
- الحفاظ على الواجهة الخارجية (Public Methods) كما هي
- المستخدم الخارجي لن يلاحظ الفرق

**مثال الكود:**
```python
# OLD
self.graph = nx.DiGraph()

# NEW
self.graph = GraphDatabaseSQLite("data/theone.db")
```

---

### 3.2 تجزئة الملفات الكبيرة

#### مشكلة: `simple_reasoner.py` (1,412 سطر)
**الحل: تقسيم إلى ملفات متخصصة**

```
src/reasoner/
├── simple_reasoner.py (300 سطر — المنسق الرئيسي فقط)
├── pattern_matcher.py (تم إنشاؤه في المرحلة 1)
├── learning_engine.py (تم إنشاؤه في المرحلة 1)
├── intent_handlers.py (NEW — 400 سطر)
│   ├── handle_is_a_query()
│   ├── handle_where_query()
│   ├── handle_what_is_query()
│   └── ... (كل intent له معالج منفصل)
├── entity_extractors.py (NEW — 300 سطر)
│   ├── extract_location()
│   ├── extract_object()
│   └── ...
└── response_builders.py (NEW — 300 سطر)
    ├── build_answer()
    ├── build_confidence_chain()
    └── ...
```

#### مشكلة: `App.jsx` (1,552 سطر)
**الحل: تقسيم إلى مكونات React**

```
desktop-gui/src/components/
├── ChatInterface.jsx (200 سطر)
├── GraphVisualizer.jsx (300 سطر)
├── KnowledgePanel.jsx (200 سطر)
├── ConflictResolver.jsx (150 سطر)
├── PersonalitySelector.jsx (100 سطر)
└── App.jsx (400 سطر — المنسق الرئيسي)
```

---

### 3.3 تحسينات إضافية

#### إضافة نظام التسجيل (Logging)
```python
# src/utils/logger.py (NEW)
import logging

logger = logging.getLogger("TheOne")
handler = logging.FileHandler("logs/theone.log")
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# الاستخدام:
logger.info(f"Pattern matched: {intent}")
logger.warning(f"Low confidence: {confidence}")
logger.error(f"Database error: {error}")
```

#### إضافة مراقبة الأداء (Performance Monitoring)
```python
# src/utils/profiler.py (NEW)
import time

def profile_function(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper

@profile_function
def expensive_operation():
    pass
```

---

## المرحلة 4: الاختبار والتحقق

**المدة المتوقعة:** أسبوع  
**الهدف:** التأكد من أن كل التغييرات تعمل بشكل صحيح

### 4.1 اختبارات الآلية (AUTOMATED TESTS)

#### تشغيل الاختبارات الموجودة
```bash
cd /home/zean/Projects/TheOne
pytest tests/ -v

# النتيجة المتوقعة: 94 اختبار تنجح (كما كانت سابقاً)
```

#### اختبارات جديدة للمرحلة 1

##### `tests/test_pattern_matcher.py` (NEW)
```python
def test_basic_pattern_matching():
    """اختبار المطابقة الأساسية"""
    matcher = GenericPatternMatcher("data/language_rules.json")
    result = matcher.match("هل الأسد حيوان")
    assert result.intent == "is_a_query"
    assert result.extracted_entities["subject"] == "الأسد"

def test_fuzzy_matching():
    """اختبار المطابقة المرنة (مع أخطاء إملائية)"""
    matcher = GenericPatternMatcher("data/language_rules.json")
    result = matcher.match("هل الاسد حيوان")  # حطأ إملائي
    assert result is not None

def test_pattern_matching_failure():
    """اختبار الفشل المتوقع"""
    matcher = GenericPatternMatcher("data/language_rules.json")
    result = matcher.match("كلام عشوائي لا معنى له")
    assert result is None
```

##### `tests/test_learning_engine.py` (NEW)
```python
def test_learn_new_pattern():
    """اختبار تعلم نمط جديد"""
    learner = InteractiveBootstrapper(graph_handler, "data/language_rules.json")
    
    # محاكاة مستخدم يعلم النظام نمطاً جديداً
    new_pattern = learner.ask_for_clarification("الأسد ده إيه؟", ["ده", "إيه"])
    
    assert new_pattern is not None
    assert new_pattern["pattern"] is not None
    
    # التحقق من حفظ النمط
    with open("data/language_rules.json") as f:
        rules = json.load(f)
        assert new_pattern["id"] in [p["id"] for p in rules["syntactic_patterns"]]

def test_learned_pattern_reuse():
    """اختبار إعادة استخدام النمط المتعلم"""
    matcher = GenericPatternMatcher("data/language_rules.json")
    
    # بعد تعلم النمط السابق، يجب أن يعمل
    result = matcher.match("الغزالة ده إيه؟")
    assert result is not None
    assert result.intent == "what_is_query"
```

##### `tests/test_integration_phase1.py` (NEW)
```python
def test_phase1_end_to_end():
    """اختبار المرحلة 1 من البداية للنهاية"""
    reasoner = SimpleReasoner()
    
    # السؤال الأول (معروف)
    response1 = reasoner.process("هل الأسد حيوان")
    assert response1.success
    
    # السؤال بصياغة غير معروفة
    response2 = reasoner.process("الأسد ده إيه بالظبط؟")
    # يجب أن يدخل وضع التعلم ويسأل المستخدم
    
    # السؤال الثالث بنفس الصياغة (يجب أن يعرفها الآن)
    response3 = reasoner.process("النمر ده إيه بالظبط؟")
    assert response3.success
```

---

### 4.2 التحقق اليدوي (MANUAL VERIFICATION)

#### السيناريو 1: فهم الأسئلة المعروفة
```
المستخدم: هل الأسد حيوان؟
النظام: نعم، الأسد هو حيوان مفترس من الثدييات.
[سلسلة الاستدلال معروضة]
```

#### السيناريو 2: التعلم من صياغة جديدة
```
المستخدم: الأسد ده إيه بالظبط؟
النظام: (لا يفهم الصياغة الأولى)
النظام: أنا لا أفهم كلمة "ده" و"إيه" في هذا السياق.
        هل تقصد السؤال عن: "ما هو الأسد"؟
        أو: "ما تصنيف الأسد؟"
        اختر: [1] [2]
المستخدم: 1
النظام: ✓ تم تعلم النمط الجديد!
```

#### السيناريو 3: إعادة استخدام النمط المتعلم
```
المستخدم: الغزالة ده إيه بالظبط؟
النظام: الغزالة هي حيوان عاشب من الثدييات...
[بدون الحاجة لإعادة التعلم]
```

#### السيناريو 4: التعامل مع الأخطاء الإملائية
```
المستخدم: هل الاسد (بدون همزة) حيوان؟
النظام: نعم، الأسد هو حيوان...
[تم التعرف عليه رغم الخطأ الإملائي]
```

---

### 4.3 قائمة التحقق (CHECKLIST)

- [ ] تشغيل `pytest tests/ -v` — جميع 94 اختبار تنجح
- [ ] تشغيل الاختبارات الجديدة — كل اختبار يتعلق بـ Phase 1 ينجح
- [ ] السيناريو 1: الأسئلة المعروفة تعمل
- [ ] السيناريو 2: التعلم من صياغة جديدة يعمل
- [ ] السيناريو 3: إعادة استخدام النمط تعمل
- [ ] السيناريو 4: الأخطاء الإملائية تُتعامل معها
- [ ] تشغيل `main.py` — الواجهة الطرفية تعمل
- [ ] تشغيل `api.py` — REST API تعمل
- [ ] فتح `desktop-gui` — الواجهة الرسومية تعمل
- [ ] فحص ملف `language_rules.json` — تم إضافة أنماط جديدة

---

## الخلاصة والملاحظات المهمة

### ما تم إنجازه

✅ **إزالة ~565 سطر من الكود الثابت (Hardcoding)**

✅ **إضافة نظام ديناميكي ذاتي التعلم**

✅ **الحفاظ على قاعدة المعرفة الموجودة (لا حذف)**

✅ **توسيع قاعدة المعرفة من 17 → 10,000+ مفهوم (اختياري في المرحلة 2)**

✅ **تحسين الأداء والبنية التحتية (المرحلة 3)**

### ما لا يمكن تنفيذه برمجياً (توصيات للمستخدم)

⚠️ **جمع البيانات:** المستخدم يجب أن يختار مجال متخصص وينسق توفر البيانات

⚠️ **مراجعة قواعس الاستدلال:** لا بد من مراجعة يدوية من قبل خبير المجال

⚠️ **التحقق من دقة المعلومات:** المستخدم يجب أن يتأكد من صحة البيانات المستوردة

---

## المراجع والموارد

- [NetworkX Documentation](https://networkx.org/)
- [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Symbolic AI Research](https://arxiv.org/)
- [Wikidata API](https://www.wikidata.org/wiki/Wikidata:Main_Page)
- [ConceptNet](https://conceptnet.io/)

---

**تاريخ آخر تحديث:** 5 يونيو 2026
