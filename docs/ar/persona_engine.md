# اختيار الشخصيات المعرفية وصياغة التعبيرات (Persona Engine)

## 📋 نظرة عامة
يحتوي محرك **TheOne** على **محرك الشخصيات اللغوية المتعددة (Multilingual Persona Engine)** الذي يقوم بصياغة الإجابات المنطقية الجافة ووضعها في قالب لغوي يعكس طبيعة الشخصية المختارة.
يقوم النظام بتقييم سمات السؤال وسياق الحوار لاختيار الشخصية الأنسب ذاتياً، ثم ينشئ الرد النهائي باستخدام قوالب لغوية مترجمة وسلاسل استدلال مطابقة للغة الحوار.

---

## 📂 الملفات المسؤولة
* **محرك الشخصية الرئيسي:** [src/manager/multilingual_persona_engine.py](file:///home/zean/Projects/TheOne/src/manager/multilingual_persona_engine.py)
* **محدد الشخصية:** [src/reasoner/persona_selector.py](file:///home/zean/Projects/TheOne/src/reasoner/persona_selector.py)
* **مصيغ التعبيرات اللغوية:** [src/renderer/expression_renderer.py](file:///home/zean/Projects/TheOne/src/renderer/expression_renderer.py)
* **ملف إعدادات الشخصيات:** [config/personas_multilingual.json](file:///home/zean/Projects/config/personas_multilingual.json)

---

## ⚙️ تفاصيل واجهة البرمجة (Python API)

### كلاس `MultilingualPersonaEngine`
الذي ينسق عملية الصياغة في `src/manager/multilingual_persona_engine.py`.

#### `process_response(self, question, logical_response, conversation_history=None, user_preference=None, force_persona_id=None)`
* **الوصف:** ينفذ خط معالجة الصياغة اللغوية بالكامل: كشف لغة الإدخال، تحديد لغة الرد، تصنيف سياق الحديث، اختيار الشخصية المنشودة، وصياغة وتنسيق الرد النهائي.
* **المعاملات:**
  * `question` (*str*): نص سؤال المستخدم.
  * `logical_response` (*dict*): الإجابة المنطقية المستخرجة من الرسم البياني.
  * `conversation_history` (*list*): قائمة تحتوي على تاريخ المحادثة.
  * `user_preference` (*str*): تخطي وتحديد لغة الرد يدوياً.
  * `force_persona_id` (*str*): تحديد شخصية معينة لفرض استخدامها (`sage_friend` أو `scientist` أو `witty_mentor`).
* **المخرجات:** قاموس يحتوي على الرد النصي النهائي `"response"`، واللغة المستخدمة `"language"`، والشخصية المفعلة `"persona"`.

### كلاس `MultilingualPersonaSelector`
الموجود في `src/reasoner/persona_selector.py`. يطابق سياق السؤال بالشخصية الأنسب:
1. **الصديق الحكيم (Sage Friend):** رد متعاطف، تفصيلي، هادئ ولطيف.
2. **العالِم (Scientist):** رد رسمي، حيادي، موضوعي ومبني على الأدلة العلمية الجافة.
3. **المرشد المرح (Witty Mentor):** رد مرح، نشط، فكاهي ويستخدم بعض التعبيرات الدارجة.

---

## 🖥️ الاستخدام من التيرمينال والواجهة الرسومية (GUI)

### التفاعل عبر التيرمينال:
1. اطرح سؤالاً على النظام في الواجهة التفاعلية (الخيار رقم **1**).
2. يطبع النظام اسم الشخصية التي صاغت الرد:
   ```text
   ==================================================
   Active World: 'reality'
   Language: en | Persona: scientist
   Final Response:
   👉 Based on empirical facts, a lion is a subcategory of animal.
   ==================================================
   ```

### عناصر الواجهة الرسومية (GUI):
* **قائمة اختيار الشخصية (Persona Selector Dropdown):** تقع بجانب حقل إدخال الرسائل مباشرة في شاشة الدردشة، وتتيح للمستخدم تحديد أحد الخيارات التالية يدوياً:
  * **الاختيار التلقائي (Auto-Select):** يترك للنظام تحديد الشخصية المناسبة تلقائياً بناءً على سياق الحوار.
  * **الصديق الحكيم (Sage Friend).**
  * **العالِم (Scientist).**
  * **المرشد المرح (Witty Mentor).**
* **ربط واجهة الاستدعاء (API):** يتم تمرير كود الشخصية المحددة يدوياً كمعامل `force_persona_id` في متن طلب الاستعلام المرسل لـ POST `/api/query` لفرض أسلوب الرد المطلوب.
