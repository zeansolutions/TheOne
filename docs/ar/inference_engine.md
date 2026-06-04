# محرك الاستدلال الديناميكي والاستنتاج التراكمي (Inference & Forward Chaining)

## 📋 نظرة عامة
يستخدم محرك **TheOne** **محرك استدلال تراكمي رمزي (Forward Chaining Inference Engine)** ديناميكي بالكامل يعمل دون الحاجة للذكاء الاصطناعي التوليدي في وقت الاستعلام. بدلاً من البرمجة الصلبة للمنطق (Hardcoding)، يقوم المحرك بتحميل قواعد منطقية (Horn clauses) متمثلة في شروط وأنماط تحتوي على متغيرات، ويطابقها تكرارياً مع الرسم البياني للمعرفة الحالية لاستنتاج علاقات وحقائق جديدة حتى يصل إلى مرحلة الاستقرار المنطقي (Fixpoint - حيث لا يمكن استنتاج أي روابط جديدة).

---

## 📂 الملفات المسؤولة
* **الكود المصدري:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) (الدوال `infer_facts` و `find_bindings`) وكلاس التعدي المنطقي [src/reasoner/transitive_chaining.py](file:///home/zean/Projects/TheOne/src/reasoner/transitive_chaining.py)
* **قواعد الاستدلال:** [data/inference_rules.json](file:///home/zean/Projects/TheOne/data/inference_rules.json) وملف العلاقات الوصفية [data/relations_metadata.json](file:///home/zean/Projects/TheOne/data/relations_metadata.json)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `GraphHandler` (الاستدلال والتطابق)
ميثودات في كلاس `GraphHandler` لتشغيل الاستقراء والربط المنطقي.

#### `find_bindings(self, conditions, bindings=None)`
* **الوصف:** يبحث تراجعياً في الرسم البياني عن المتغيرات المنطقية (مثل مطابقة المتغير `?x` بمفهوم محدد) التي تحقق مجموعة من الشروط الثلاثية.
* **المعاملات:**
  * `conditions` (*list*): قائمة الشروط المنطقية.
  * `bindings` (*dict*): قيم المتغيرات الحالية، والافتراضي `None`.
* **المخرجات:** قائمة بالمتطابقات المكتشفة كـ قواميس.

#### `infer_facts(self, world_name)`
* **الوصف:** ينفذ حلقة الاستدلال التراكمي التكرارية. يطابق القواعد على حقائق العالم النشط، وينشئ روابط وعلاقات جديدة من نوع `"inferred"` ويحفظها مؤقتاً في الرسم البياني. يتوقف الاستدلال عندما لا يتم إنتاج أي علاقة جديدة.
* **المعاملات:**
  * `world_name` (*str*): العالم المستهدف لتشغيل الاستدلال عليه.
* **المخرجات:** قائمة بخطوات وسلسلة الاستدلال (Trace).

### كلاس `TransitiveChainingReasoner`
الموجود في `src/reasoner/transitive_chaining.py`. يختص بمعالجة العلاقات المتعدية (مثل الوراثة التصنيفية `is_a` والجزء من الكل `part_of`).

#### `compute_transitive_relations(self, concept, relation_type, world)`
* **الوصف:** يتتبع مسارات العلاقات المتعدية عبر قفزات متعددة (مثال: أ جزء من ب، ب جزء من ج $\implies$ أ جزء من ج).
* **المخرجات:** قائمة بالمفاهيم النهائية التي تم التوصل إليها.

---

## 🖥️ طريقة الاستخدام من التيرمينال
1. يتم تشغيل الاستدلال ديناميكياً وتلقائياً عند طرح أي سؤال في التيرمينال (الخيار **1**).
2. عند ضبط مستوى التتبع ليكون مفصلاً `"detailed"` (وهو الخيار الافتراضي)، يتم طباعة خطوات التتبع المنطقي في سطر الأوامر:
   ```text
   👉 Final Response:
   Yes, a lion is a predator.
   
   Reasoning Trace:
   - Inference: lion is_a feline_carnivore based on database ontology
   - Inference: feline_carnivore is_a carnivore based on database ontology
   - Inferred Fact: lion is_a carnivore based on rule 'Taxonomic Inheritance'
   ```

---

## 🚀 التكامل مع واجهة الاستدعاء (API) والواجهة الرسومية (GUI)

### مخرجات التتبع لطلبات HTTP API:
عند إرسال طلب POST للاستعلام `/api/query`، يعيد الخادم رداً بصيغة JSON يحتوي على مصفوفة `"trace"` تسرد بالتفصيل خطوات الاستدلال المنطقي:
```json
{
  "response": "Yes, a lion is a predator.",
  "trace": [
    "Inference: lion is_a feline_carnivore based on database ontology",
    "Inference: feline_carnivore is_a carnivore based on database ontology",
    "Inferred Fact: lion is_a carnivore based on rule 'Taxonomic Inheritance'"
  ],
  "elapsed_ms": 12.5
}
```

### عرض الاستدلال في الواجهة الرسومية (GUI):
* **الرسم البياني الفيزيائي التفاعلي:** يتم تمثيل العلاقات والروابط المستنتجة (Inferred edges) ديناميكياً كـ **خطوط وردية متقطعة (Dashed pink lines)** لتمييزها بصرياً عن الحقائق الأصلية المسجلة يدوياً في قاعدة البيانات (والتي تظهر بخطوط متصلة).
* **لوحة تفاصيل الاستدلال (Reasoning Trace Accordion):** أسفل فقاعة رد المحادثة مباشرة، توجد لوحة تفاعلية قابلة للطي (Reasoning Trace) تعرض تسلسل الاستنتاج المنطقي بالإضافة للزمن المستغرق بالملي ثانية.
* **ترجمة خطوات الاستدلال:** يقوم محرك الصياغة والتعبير بترجمة معرفات الكيانات والعلاقات الداخلية (مثل `lives_in` أو `is_a`) إلى لغة العرض النشطة في التطبيق الرسومي ليفهم المستخدم سلسلة الاستدلال بلغته المختارة.
