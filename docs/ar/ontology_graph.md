# الأنطولوجيا وتمثيل الرسم البياني للمعرفة (Ontology & Knowledge Graph)

## 📋 نظرة عامة
تمثل شبكة المعرفة النواة الأساسية لمحرك **TheOne**، حيث يتم تمثيلها كـ رسم بياني موجه متعدد العلاقات `MultiDiGraph` باستخدام مكتبة **NetworkX** (والذي يسمح بوجود روابط متوازية متعددة بين نفس الكيانين).
تحدد الأنطولوجيا الكيانات (العقد) والتصنيفات، بينما تحفظ قاعدة البيانات الحقائق (العلاقات والروابط) التي تمثل جمل الاستدلال.

---

## 📂 الملفات المسؤولة
* **الكود المصدري:** [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) و [src/maintenance/db_io_handler.py](file:///home/zean/Projects/TheOne/src/maintenance/db_io_handler.py)
* **ملف الأنطولوجيا:** [data/ontology.json](file:///home/zean/Projects/TheOne/data/ontology.json) (قاعدة بيانات المفاهيم الفارغة للبدء)
* **ملف الحقائق:** [data/facts.json](file:///home/zean/Projects/TheOne/data/facts.json) (قاعدة بيانات الحقائق الأساسية الفارغة للبدء)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `GraphHandler` و `DbIoHandler`
الموجود في `src/graph_handler.py` و `src/maintenance/db_io_handler.py`. يدير الرسم البياني لـ NetworkX ويقوم بتحميل قواعد البيانات وتخزينها واستيراد ملفات الحقائق وتحديث العلاقات.

#### `load_databases(self, ontology_path, facts_path, language_rules_path)`
* **الوصف:** يحلل ملفات الأنطولوجيا والحقائق والقواعد اللغوية من صيغة JSON ويقوم بملء العقد والعلاقات في الرسم البياني عبر تفويض المهمة لكلاس `DbIoHandler`.
* **المعاملات:**
  * `ontology_path` (*str*): مسار ملف JSON الخاص بالأنطولوجيا.
  * `facts_path` (*str*): مسار ملف JSON الخاص بالحقائق.
  * `language_rules_path` (*str*): مسار ملف JSON الخاص بالقواعد اللغوية.
* **المخرجات:** لا شيء.

#### `get_parent(self, concept_id, relation="is_a")`
* **الوصف:** يبحث في الرسم البياني ويعيد الكيان الأب المباشر المرتبط بالعلاقة المحددة (الوراثة التصنيفية).
* **المعاملات:**
  * `concept_id` (*str*): معرف الكيان المراد البحث عنه.
  * `relation` (*str*): نوع علاقة البحث، والقيمة الافتراضية `"is_a"`.
* **المخرجات:** يعيد معرف الكيان الأب (*str*) أو `None` في حال عدم وجوده.

---

## 🚀 التكامل مع واجهة الاستدعاء (API) والواجهة الرسومية (GUI)

### نقطة استدعاء REST API:
* **GET `/api/graph`**: تصدير قائمة العقد والروابط للرسم البياني بهيكل متوافق مع العرض الرسومي:
  ```json
  {
    "nodes": [{"id": "concept_id", "label": "Concept Label", "category": "category_name", "type": "concept"}],
    "edges": [{"source": "u", "target": "v", "relation": "relation_name", "world": "reality", "confidence": 1.0, "type": "fact"}]
  }
  ```

### لوحة الرسم البياني التفاعلية بالواجهة الرسومية (GUI):
توفر واجهة Electron الرسومية لوحة مميزة لعرض الشبكة العصبية والسيالات المعصبية ديناميكياً مبنية على محاكي فيزيائي تفاعلي (Canvas-based physics simulation):
* يتم تلوين الكيانات (Nodes) وفقاً لتصنيفاتها.
* يتم تمثيل الروابط الحقيقية (Facts) بخطوط متصلة.
* الروابط المستنتجة (Inferred) تمثلها خطوط وردية متقطعة (Dashed pink lines).
* عند الضغط على أي عقدة في الرسم البياني، يتم تحديدها وتظليل مساراتها النشطة، ويتم ملؤها تلقائياً في حقول التلقين والتعليم (Teach Form) لتسهيل الإدخال.
