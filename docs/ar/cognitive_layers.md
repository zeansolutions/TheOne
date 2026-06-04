# الطبقات العشر للاستدلال المعرفي المتقدم (10 Advanced Cognitive Layers)

## 📋 نظرة عامة
لتوفير استدلال منطقي عميق خالٍ تماماً من الاستدعاء الخارجي لـ LLM عند التشغيل، يشتمل نظام **TheOne** على **10 طبقات رمزية متكاملة للاستدلال المعرفي**. تتعامل هذه الطبقات مع التراكيب اللغوية المعقدة والمحددات المنطقية.

---

## 📂 الملفات المسؤولة
* **مجلد المعالجات البرمجية:** `src/reasoner/`
* **قواعد البيانات اللغوية والمعرفية (JSON):** `data/`
* **وحدة الدمج والاستدعاء:** [src/simple_reasoner.py](file:///home/zean/Projects/TheOne/src/simple_reasoner.py)

---

## ⚙️ معالجات الطبقات العشر وتفاصيل واجهة البرمجة (Python API)

تم تخصيص كلاس مستقل لكل معالج ضمن مجلد `src/reasoner/`:

### 1. طبقة الأدوار الدلالية (`semantic_processor.py` / `semantic_roles.json`)
* **دورها:** تعيين وتفكيك الأفعال لربطها بالفاعل والمفعول والمكان والزمان (`AGENT`, `PATIENT`, `LOCATION`, `TIME`).
* **الدالة:** `extract_semantic_roles(self, words, language, graph_handler)`

### 2. طبقة المنطق الزمني (`temporal_processor.py` / `temporal_logic.json`)
* **دورها:** كشف العلاقات الزمنية بين الأحداث (`BEFORE`, `AFTER`, `DURING`) وترتيب التواريخ وسلاسل الأحداث.
* **الدالة:** `apply_temporal_reasoning(self, facts, query, language)`

### 3. طبقة الجهة والالتزام (`modality_processor.py` / `modalities.json`)
* **دورها:** كشف وتعديل مؤشرات الاحتمال والضرورة والوجوب (مثل: "يجب"، "يمكن").
* **الدالة:** `process_modality(self, text, language)`

### 4. طبقة السلاسل السببية (`chain_processor.py` / `causal_chains.json`)
* **دورها:** استنتاج ونشر التبعات المترتبة على الأسباب عبر قفزات سببية متعددة.
* **الدالة:** `propagate_causal_chains(self, initial_state, graph_handler)`

### 5. طبقة سور القضية والكميات (`quantifier_processor.py` / `quantifiers.json`)
* **دورها:** فحص دلالات شمولية الحكم (مثل: "كل"، "بعض"، "أغلب") وتقييم صحتها منطقياً.
* **الدالة:** `evaluate_quantifiers(self, statement, query, graph_handler)`

### 6. طبقة النفي والتقابل (`negation_processor.py` / `negation_rules.json`)
* **دورها:** تمييز أدوات النفي وعكس قطبية الجملة ومطابقتها مع الأضداد والمقاربات.
* **الدالة:** `apply_negation(self, query, language)`

### 7. طبقة الاستلزام والتعارض المنطقي (`entailment_processor.py` / `entailment.json`)
* **دورها:** قياس مدى استلزام المقدمة للنتيجة صورياً وكشف التناقضات المباشرة.
* **الدالة:** `check_entailment_and_contradiction(self, premise, hypothesis, graph_handler)`

### 8. طبقة التداولية والمجاز (`pragmatic_processor.py` / `pragmatic_knowledge.json`)
* **دورها:** تفسير الاستعارات والكنايات الثقافية وتحويلها لمعانٍ صريحة رمزية للاستدلال.
* **الدالة:** `resolve_pragmatics(self, concept_id, query_context)`

### 9. طبقة المقارنات والترتيب (`comparison_processor.py` / `comparison.json`)
* **دورها:** إجراء المقارنات التعدية بين الكيانات في مقاييس كمية (مثل: القوة، السرعة، الحجم).
* **الدالة:** `evaluate_comparison(self, entity1, entity2, property_name)`

### 10. طبقة كشف الشذوذ والاستثناءات (`anomaly_processor.py` / `anomaly_detection.json`)
* **دورها:** كشف الخصائص الشاذة للكيانات التي تخالف القواعد العامة وحساب نقاط الشذوذ.
* **الدالة:** `detect_anomaly(self, entity, property_name, graph_handler)`

---

## 🖥️ التيرمينال وتكامل الواجهة الرسومية (GUI)

### 1. التحقق من التيرمينال
لتشغيل اختبارات التحقق الآلية لكافة الطبقات المعرفية:
```bash
./start.sh test
```

### 2. العرض في الواجهة الرسومية (GUI)
* **تبويب الإجراءات المعرفية (Procedural Tab):** يتيح تسجيل الخطوات المنطقية والمهام المتتابعة يدوياً.
* **عرض تفاصيل الطبقات المعرفية:** عند عرض مسارات الاستدلال (Trace Accordion) في شاشة الدردشة، تظهر بالتفصيل الطبقة المعرفية التي تدخلت في التحليل (مثل معالجة النفي، أو مقارنة الترتيب والسرعة، أو إحصائيات تقليل الثقة بناءً على الاحتمال المنطقي للجهة).
