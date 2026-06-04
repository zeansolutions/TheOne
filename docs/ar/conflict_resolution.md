# حل التعارضات واكتشاف التناقضات (Conflict Resolution)

## 📋 نظرة عامة
للحفاظ على الاتساق المنطقي لشبكة البيانات، يحتوي نظام **TheOne** على **نظام متكامل لمعالجة التعارضات واكتشاف التناقضات المنطقية**. عند تلقين النظام حقائق جديدة، يتحقق تلقائياً من وجود تصادم منطقي (مثل تعارض الخصائص المتباينة لكيان واحد في نفس العالم). يتم حل التعارض ذاتياً بناءً على درجات الثقة، أو يتم توجيه السؤال للمستخدم لاتخاذ القرار المناسب تفاعلياً.

---

## 📂 الملفات المسؤولة
* **الكود المصدري:** [src/conflict_resolver.py](file:///home/zean/Projects/TheOne/src/conflict_resolver.py) و [src/graph_handler.py](file:///home/zean/Projects/TheOne/src/graph_handler.py) (الميثود `add_or_update_fact`)
* **حزمة الاختبارات:** [tests/test_contradiction.py](file:///home/zean/Projects/TheOne/tests/test_contradiction.py)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `ConflictResolver`
الموجود في `src/conflict_resolver.py`.

#### `resolve_conflict(self, concept_id, relation_type)`
* **الوصف:** يتحقق مما إذا كان لكيان معين حقائق متعارضة عبر عوالم أو مسارات مختلفة.
* **المعاملات:**
  * `concept_id` (*str*): معرف الكيان المستهدف.
  * `relation_type` (*str*): نوع العلاقة المراد فحصها.
* **المخرجات:** قائمة بتفاصيل التعارضات المكتشفة.

### ميثود الإضافة بكلاس `GraphHandler`
الموجود في `src/graph_handler.py`.

#### `add_or_update_fact(self, subj, obj, relation, world, confidence=1.0, reason=None, interactive=False, modality=None, language="en")`
* **الوصف:** يضيف أو يحدّث العلاقات مع تطبيق استراتيجية حل النزاع ثلاثية المراحل:
  1. **الحل التلقائي:** يتم استبدال الحقيقة القديمة إذا كانت ثقة الحقيقة الجديدة أعلى بفرق أكبر من `0.3`، أو رفضها تلقائياً إذا كانت ثقة القديمة أعلى بنفس المقدار.
  2. **الحل التفاعلي / إرسال تنبيه تعارض للـ GUI:** إذا كان الفارق بين درجتي الثقة أقل من `0.3`، يتم تعليق الإضافة وتخيير المستخدم بين:
     * **الاستبدال (Replace):** مسح الحقيقة القديمة وحفظ الجديدة وأرشفة السابقة.
     * **الدمج (Merge):** الاحتفاظ بالحقيقتين بالتوازي.
     * **التجاهل (Ignore):** التخلي عن الحقيقة الجديدة والاحتفاظ بالقديمة.
* **المخرجات:** تقرير بصيغة قاموس يحتوي على تفاصيل التعارض ورسالة التنبيه.

---

## 🖥️ طريقة الاستخدام من التيرمينال
1. افتح الواجهة التفاعلية واختر الخيار **3** لتلقين العقل.
2. إذا قمت بإدخال حقيقة تتعارض مع حقيقة قائمة في نفس العالم (مثلاً إدخال أن الأسد ذو فرو خفيف `thin_fur` بينما مسجل مسبقاً فرو كثيف `thick_fur` في عالم الواقع `reality` وبنفس نسبة الثقة)، سيقف النظام ويعرض قائمة الحل:
   ```text
   ⚠️ [Fact Conflict] The new fact conflicts with a recorded fact in world 'reality'!
   Current fact: [lion] --(has_property)--> [thick fur] (confidence: 1.0)
   New fact: [lion] --(has_property)--> [thin fur] (confidence: 1.0)
   --------------------------------------------------
   Please choose a resolution option:
    1. Replace
    2. Merge
    3. Ignore
   Choose resolution option (1-3): 
   ```

---

## 🚀 التكامل مع واجهة الاستدعاء (API) والواجهة الرسومية (GUI)

### نقاط استدعاء REST API:
* **POST `/api/teach`** - عند اكتشاف تعارض وكانت الفروق أقل من `0.3`، يعيد الخادم رداً بحالة `"conflict"` مع تفاصيل الحقيقتين المتعارضتين:
  ```json
  {
    "status": "conflict",
    "conflict": {
      "subject": "feline_carnivore",
      "relation": "has_property",
      "old_object": "thick_fur",
      "new_object": "thin_fur",
      "world": "reality"
    }
  }
  ```
* **POST `/api/resolve_conflict`** - لتأكيد الخيار المختار لحل التعارض. يستقبل جسم الطلب التالي:
  ```json
  {
    "action": "replace | merge | ignore",
    "subject": "subject_concept",
    "relation": "relation_type",
    "old_object": "old_val",
    "new_object": "new_val",
    "world": "world_name",
    "confidence": 1.0,
    "modality": "modality_val",
    "reason": "reason_string"
  }
  ```

### نافذة حل التعارض بالواجهة الرسومية (GUI Conflict Modal):
في واجهة Electron الرسومية، عند تعليم العقل حقيقة جديدة تتسبب في تعارض منطقي، تظهر فوراً نافذة منبثقة تفاعلية (Modal window) تعرض مقارنة جنباً إلى جنب بين الحقيقة القائمة والحقيقة المدخلة، وتتيح ثلاثة أزرار واضحة:
1. **الاستبدال (Overwrite):** مسح الحقيقة القديمة واعتماد الجديدة.
2. **الدمج بالتوازي (Merge Parallel):** الاحتفاظ بكلا الحقيقتين.
3. **التجاهل (Discard):** إغلاق الطلب دون تعديل شبكة المعرفة الحالية.
