# محرك الشخصيات المتعدد ورندرة التعبيرات (Multilingual Persona Engine)

## 📋 نظرة عامة
يحتوي محرك **TheOne** على **محرك شخصيات متعدد اللغات** يهدف إلى صياغة الرد المنطقي الخالص بأسلوب تعبيري يحمل ملامح شخصية تفاعلية محددة.
يقيم النظام ميزات وسياق الحوار لاختيار الشخصية الأنسب، ويقوم بدمج العبارات التمهيدية والتحيات المترجمة، بالإضافة لترجمة مسار الاستدلال بالكامل إلى اللغة المحددة.

---

## 📂 الملفات المسؤولة
* **الكود المصدري:** [src/manager/multilingual_persona_engine.py](file:///home/zean/Projects/TheOne/src/manager/multilingual_persona_engine.py)
* **كاشف الشخصية:** [src/reasoner/persona_selector.py](file:///home/zean/Projects/TheOne/src/reasoner/persona_selector.py)
* **رندرة التعبيرات:** [src/renderer/expression_renderer.py](file:///home/zean/Projects/TheOne/src/renderer/expression_renderer.py)
* **ملف الشخصيات والتعبيرات:** [config/personas_multilingual.json](file:///home/zean/Projects/TheOne/config/personas_multilingual.json)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `MultilingualPersonaEngine`
منسق العملية بأكملها في `src/manager/multilingual_persona_engine.py`.

#### `process_response(self, question, logical_response, conversation_history=None, user_preference=None)`
* **الوصف:** ينفذ كامل خطوات رندرة الرد: يكتشف لغة الإدخال، ويحدد لغة الرد، ويحلل ميزات السياق لاختيار الشخصية، ثم يولد التعبير التفاعلي النهائي.
* **المخرجات:** يعيد قاموساً يحتوي على: الرد النهائي `"response"`، لغة الرد `"language"`، الشخصية المنتقاة `"persona"`، ومستوى اليقين `"confidence"`.

### كلاس `MultilingualPersonaSelector`
الموجود في `src/reasoner/persona_selector.py`. يقوم بوزن السياق لاختيار إحدى الشخصيات الثلاث:
1. **الحكيم الودود (Sage Friend):** هادئ النبرة، متعاطف، يفصل الردود.
2. **الباحث العلمي (Scientist):** رسمي، موضوعي، يستند للأرقام والبيانات الدقيقة.
3. **المرشد الظريف (Witty Mentor):** فكاهي، حيوي، يستخدم تعبيرات عامية خفيفة.

#### `select_best_persona(self, context)`
* **الوصف:** يعيد معرف الشخصية التي حصلت على الوزن الأعلى بناءً على نوع السؤال، الكلمات المفتاحية، والحالة المزاجية للسياق.
* **المخرجات:** معرف الشخصية (*str*).

---

## 🖥️ طريقة الاستخدام من التيرمينال
1. اطرح سؤالاً على النظام في الواجهة التفاعلية (الخيار رقم **1**).
2. يطبع النظام تفاصيل الشخصية التي تمت محاكاتها ولغة الرد، مثل:
   ```text
   ==================================================
   Active World: 'reality'
   Language: en | Persona: scientist
   Final Response:
   👉 Based on empirical facts, a lion is a subcategory of animal.
   ==================================================
   ```
3. غير أسلوب وكلمات سؤالك لتغيير استجابة محرك الشخصيات تلقائياً. على سبيل المثال، السؤال بـ `"لماذا يأكل الأسد اللحم؟"` سيحفز شخصية الباحث العلمي (`scientist`)، بينما السؤال بـ `"من هو ملك الغابة؟"` سيحفز شخصية الحكيم الودود (`sage_friend`).
