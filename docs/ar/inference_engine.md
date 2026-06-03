# محرك الاستدلال الديناميكي بالأثر الأمامي (Dynamic Inference & Forward Chaining)

## 📋 نظرة عامة
يطبق نظام **TheOne** محرك استدلال استنتاجي أمامي ديناميكي (Forward Chaining) لا يعتمد على الذكاء الاصطناعي الإحصائي عند التشغيل (Zero-LLM Runtime).
يقوم المحرك بتحميل حزم من القواعد المنطقية (Horn Clauses) الموصوفة بصيغة شروط ونتائج مرنة تحتوي على متغيرات (مثل `?x`, `?y`, `?z`)، ويقوم بمطابقتها بشكل تكراري مع شبكة المعرفة واستنتاج روابط جديدة حتى الوصول لمرحلة الاستقرار المعرفي (Fixpoint).

---

## 📂 الملفات المسؤولة
* **الكود المصدري:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) (الدوال `infer_facts`, `find_bindings`) و [src/reasoner/transitive_chaining.py](file:///home/zean/Projects/TheOne/src/reasoner/transitive_chaining.py)
* **ملفات القواعد والتكوين:** [data/inference_rules.json](file:///home/zean/Projects/TheOne/data/inference_rules.json) و [data/relations_metadata.json](file:///home/zean/Projects/TheOne/data/relations_metadata.json)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `GraphHandler` (الاستدلال الاستنتاجي)
دوال في `GraphHandler` للتحقق وحث الاستدلال.

#### `find_bindings(self, conditions, bindings=None)`
* **الوصف:** تبحث في الرسم البياني عن كيانات تحقق شروط القاعدة (مطابقة أنماط وتعيين قيم للمتغيرات مثل `?x`).
* **المعاملات:**
  * `conditions` (*list*): قائمة بشروط القاعدة.
  * `bindings` (*dict*): تعيينات المتغيرات الحالية.
* **المخرجات:** تعيد قائمة بالمتغيرات المطابقة للكيانات في الرسم البياني.

#### `infer_facts(self, world_name)`
* **الوصف:** تشغل حلقة الاستدلال الاستنتاجي التكرارية. تطبق كافة القواعد على العالم وتدرج الروابط الجديدة المؤقتة من نوع `"inferred"`، وتتوقف عند عدم إنتاج حقائق جديدة.
* **المعاملات:**
  * `world_name` (*str*): العالم المراد تشغيل الاستدلال عليه.
* **المخرجات:** قائمة بسلاسل نصية تشرح خطوات التتبع لكل رابط مستنتج.

### كلاس `TransitiveChainingReasoner`
الموجود في [src/reasoner/transitive_chaining.py](file:///home/zean/Projects/TheOne/src/reasoner/transitive_chaining.py). يدير العلاقات المتعدية (مثل الوراثة الفئوية `is_a` أو الاحتواء الجزئي `part_of`).

#### `compute_transitive_relations(self, concept, relation_type, world)`
* **الوصف:** يتتبع مسار العلاقات المتعدية عبر قفزات متعددة (مثل أ جزء من ب، وب جزء من ج $\implies$ أ جزء من ج).
* **المخرجات:** يعيد قائمة بجميع الكيانات المستنتجة بالتعدي.

---

## 🖥️ طريقة الاستخدام من التيرمينال
1. يتم تشغيل قواعد الاستدلال تلقائياً فور طرح أي سؤال على النظام (الخيار رقم **1**).
2. في حال تفعيل وضع التتبع المفصل (`"detailed"`)، يطبع النظام مسار الاستدلال كاملاً خطوة بخطوة:
   ```text
   👉 Final Response:
   Yes, a lion is a predator.
   
   Reasoning Trace:
   - Inference: lion is_a feline_carnivore based on database ontology
   - Inference: feline_carnivore is_a carnivore based on database ontology
   - Inferred Fact: lion is_a carnivore based on rule 'Taxonomic Inheritance'
   ```
