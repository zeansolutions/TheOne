# محرك الفضول النشط ودورة الاسترخاء المعرفي (Curiosity & Sleep Cycle)

## 📋 نظرة عامة
لضمان التعلم المستمر واستقرار الذاكرة دلالياً، يحتوي نظام **TheOne** على نظامين للصيانة الدورية التلقائية:
1. **محرك الفضول النشط (Curiosity Engine):** يبحث عن الفجوات المعرفية في الرسم البياني للـ Graph (عقد معزولة، صفات ناقصة لكيانات معينة) ويصيغ أسئلة تلقائية باللغة الطبيعية ليطرحها على المستخدم لملء هذه الفجوات.
2. **دورة النوم والاسترخاء (Cognitive Sleep Cycle):** تحاكي النوم البيولوجي لترتيب المعرفة وتتضمن: تشغيل التعدي المنطقي التراكمي، تقوية روابط العلاقات المتكررة، وتقليم وحذف العلاقات الضعيفة ذات الثقة المنخفضة، ودمج العقد المترادفة.

---

## 📂 الملفات المسؤولة
* **محرك الفضول:** [src/reasoner/curiosity_engine.py](file:///home/zean/Projects/TheOne/src/reasoner/curiosity_engine.py) والملف التنفيذي [curious.py](file:///home/zean/Projects/TheOne/curious.py)
* **دورة النوم:** [src/maintenance/sleep_cycle.py](file:///home/zean/Projects/TheOne/src/maintenance/sleep_cycle.py) والملف التنفيذي [sleep.py](file:///home/zean/Projects/TheOne/sleep.py)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `CuriosityEngine`
الموجود في `src/reasoner/curiosity_engine.py`.

#### `generate_questions(self, limit=3, lang="en")`
* **الوصف:** يحلل درجات ارتباط العقد والعلاقات الأساسية المفقودة، ويحسب معدل "الغموض" (Mystery Score) للكيانات ويولد أسئلة تفاعلية.
* **المعاملات:**
  * `limit` (*int*): الحد الأقصى للأسئلة المولدة.
  * `lang` (*str*): لغة الأسئلة المطلوبة.
* **المخرجات:** قائمة بقواميس الأسئلة.

### كلاس `CognitiveSleepCycle`
الموجود في `src/maintenance/sleep_cycle.py`.

#### `run_sleep_cycle(self)`
* **الوصف:** ينفذ مهام الصيانة والتقوية للرسم البياني:
  * **التعدي (Transitive Closure):** كتابة وحفظ الحقائق المستنتجة بالتعدي بشكل دائم.
  * **التقوية (Strengthening):** زيادة قيمة الثقة للروابط التي تم استدعاؤها بشكل متكرر.
  * **التقليم (Pruning):** حذف روابط العلاقات التي تقل ثقتها عن `0.15`.
  * **دمج المترادفات (Deduplication):** دمج العقد التي تمثل نفس الشيء بناءً على روابط الترادف.
* **المخرجات:** يعيد إحصائيات التغييرات المعرفية.

---

## 🖥️ طريقة الاستخدام من التيرمينال

### تشغيل محرك الفضول النشط
يمكنك تشغيل واجهة الفضول باستخدام سكربت التحكم start.sh:
```bash
./start.sh curious --limit=5 --lang=ar
```
يطبع النظام أسئلة الفضول الحالية الناتجة عن فجوات البيانات، مثل:
`"I notice feline_carnivore is a subcategory of animal, but I don't know where it lives. Where does feline_carnivore live?"`

### تشغيل دورة النوم المعرفية
لتشغيل دورة الصيانة الاسترخائية وتصفية الشبكة:
```bash
./start.sh sleep --depth=2 --cleanup
```
يطبع التيرمينال الخطوات والنتائج دلالياً كالتالي:
```text
🌙 Starting Cognitive Sleep Cycle...
  - Running transitive chaining consolidation...
  - Running edge pruning (removing confidence < 0.15)...
  - Running node deduplication...
✅ Sleep cycle finished!
Summary of changes:
  * Synonym links merged: 0
  * Transitive links committed: 2
  * Edges pruned: 1
```

---

## 🚀 التكامل مع واجهة الاستدعاء (API) والواجهة الرسومية (GUI)

### نقاط استدعاء REST API:
* **GET `/api/curiosity`**: جلب أسئلة الفضول ديناميكياً. يدعم معامل `limit` ومعامل `lang` لاختيار لغة الأسئلة.
* **POST `/api/sleep`**: بدء دورة النوم يدوياً. يستقبل جسم الطلب بصيغة JSON: `{"depth": 2, "cleanup": true}`.

### عناصر الواجهة الرسومية (GUI):
* **قسم الأسئلة النشطة (Curiosity Panel):** تحت تبويب المحادثة (Chat Tab)، توجد لوحة تعرض الأسئلة الحالية لفضول العقل. بالضغط على أي سؤال، يتم نسخه تلقائياً لخانة الإدخال لتسهيل الإجابة وتلقين العقل.
* **لوحة دورة النوم (Maintenance Tab):** واجهة مخصصة لتفعيل دورة الاسترخاء المعرفي (Sleep Cycle). يمكنك تعديل عمق الفحص (عدد القفزات Hops) وتفعيل تنظيف العلاقات الضعيفة. يتم عرض نتائج الصيانة (عدد العقد المدمجة، العلاقات المحذوفة، إلخ) على هيئة بطاقات إحصائية متوهجة بتصميم مستقبلي.
