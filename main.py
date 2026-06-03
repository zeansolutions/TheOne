import os
import sys
import time
import argparse
from src.graph_handler import GraphHandler
from src.simple_reasoner import SimpleReasoner
from src.manager.multilingual_persona_engine import MultilingualPersonaEngine

# Default CLI Language
active_lang = "en"

# Multilingual Translations dictionary for CLI
translations = {
  "en": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Neuro-Symbolic AI Engine - MVP      ",
    "banner_sub": "  Honest, Transparent, and 100% Hallucination-Free Logical Reasoning Engine",
    "banner_options": "Available Options:",
    "menu_ask": " 1. Ask the system any question in natural language",
    "menu_graph": " 2. Show current knowledge graph (Concepts & Relations)",
    "menu_teach": " 3. Teach the system a new fact (Add relationship in graph)",
    "menu_worlds": " 4. Show stored fact worlds",
    "menu_lang": " 5. Change CLI Interface Language",
    "menu_exit": " 6. Exit",
    "menu_choice": "\nChoose an option (1-6): ",
    "ask_prompt": "\nAsk the logical mind (e.g. 'Is a lion an animal?' or 'If a lion was in the arctic, what would it require?'): ",
    "graph_title": "\n--- Current Concepts & Relationships in Knowledge Graph ---",
    "graph_concepts_count": "Total Concepts (Nodes): {count}",
    "graph_relations_count": "Total Relations (Edges): {count}",
    "graph_registered": "Registered Concepts:",
    "graph_cat_nodes": "  * Category [{cat}]: {nodes}",
    "graph_active_rels": "\nActive Relationships & Links:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (World: {world})",
    "worlds_title": "\n--- Stored Fact Worlds in the System ---",
    "worlds_available": "Available Worlds: {worlds}",
    "worlds_active": "Currently Active World: '{world}'",
    "teach_title": "\n--- Teach the System a New Fact ---",
    "teach_warning": "Warning: The relationship will be added to the graph and immediately active in reasoning!",
    "teach_concepts_available": "Available Concepts:",
    "teach_choose_from": "\nChoose the first concept (Source): ",
    "teach_choose_to": "Choose the second concept (Target): ",
    "teach_invalid_concept": "Invalid concept selection.",
    "teach_relations_available": "\nAvailable Relation Types:",
    "teach_choose_rel": "Choose relation number: ",
    "teach_which_world": "Which world does this fact belong to? (default: reality): ",
    "teach_success": "\nFact ingested successfully!",
    "teach_error": "Error during teaching: {error}",
    "press_enter": "Press [Enter] to continue...",
    "exit_msg": "\nThank you! See you in a new reasoning session.",
    "invalid_choice": "Invalid selection, please enter a number between 1 and 6.",
    "lang_switch_title": "\n--- CLI Language Selection / اختيار لغة واجهة التحكم ---",
    "lang_switch_prompt": "Select language / اختر اللغة (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ Language changed successfully!",
    "active_world": "Active World",
    "language": "Language",
    "persona": "Persona",
    "final_response": "Final Response",
    "confidence": "Confidence",
    "perf_took": "[PERF] Processing took {elapsed:.2f}ms"
  },
  "ar": {
    "banner_title": "=" * 75,
    "banner_header": "      نظام عقل منطقي (TheOne - Neuro-Symbolic AI Engine) - MVP      ",
    "banner_sub": "         عقل منطقي صادق وشفاف وخالٍ تماماً من الهلوسة الإحصائية         ",
    "banner_options": "الخيارات المتاحة:",
    "menu_ask": " 1. اسأل النظام أي سؤال باللغة الطبيعية",
    "menu_graph": " 2. اعرض شبكة المعرفة الحالية (Concepts & Relations)",
    "menu_teach": " 3. علم النظام حقيقة جديدة (اضف علاقة في الرسم البياني)",
    "menu_worlds": " 4. اعرض عوالم الحقائق المخزنة",
    "menu_lang": " 5. تغيير لغة واجهة التحكم",
    "menu_exit": " 6. خروج",
    "menu_choice": "\nاختر رقماً من القائمة (1-6): ",
    "ask_prompt": "\nاسأل عقل منطقي (مثال: 'هل الأسد حيوان؟' أو 'لو الأسد في القطب ماذا يحتاج؟'): ",
    "graph_title": "\n--- شبكة المفاهيم والعلاقات الحالية في قاعدة البيانات ---",
    "graph_concepts_count": "إجمالي المفاهيم (العقد): {count}",
    "graph_relations_count": "إجمالي العلاقات والروابط: {count}",
    "graph_registered": "المفاهيم المسجلة:",
    "graph_cat_nodes": "  * تصنيف [{cat}]: {nodes}",
    "graph_active_rels": "\nالعلاقات والروابط النشطة:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (عالم: {world})",
    "worlds_title": "\n--- عوالم الحقائق المخزنة في النظام ---",
    "worlds_available": "العوالم المتاحة: {worlds}",
    "worlds_active": "العالم الفعال حالياً: '{world}'",
    "teach_title": "\n--- تعليم النظام حقيقة جديدة ---",
    "teach_warning": "تنبيه: سيتم إضافة العلاقة للرسم البياني وتفعيلها فوراً في محرك الاستدلال!",
    "teach_concepts_available": "المفاهيم المتاحة:",
    "teach_choose_from": "\nاختر المفهوم الأول (المصدر): ",
    "teach_choose_to": "اختر المفهوم الثاني (الهدف): ",
    "teach_invalid_concept": "اختيار غير صالح.",
    "teach_relations_available": "\nأنواع العلاقات المتاحة:",
    "teach_choose_rel": "اختر رقم العلاقة: ",
    "teach_which_world": "ما هو العالم الذي تنتمي إليه هذه الحقيقة؟ (افتراضياً reality): ",
    "teach_success": "\nتم امتصاص الحقيقة بنجاح!",
    "teach_error": "خطأ أثناء التعليم: {error}",
    "press_enter": "اضغط [Enter] للاستمرار...",
    "exit_msg": "\nشكراً لك! إلى اللقاء في جلسة تفكير جديدة.",
    "invalid_choice": "اختيار غير صالح، يرجى إدخال رقم بين 1 و 6.",
    "lang_switch_title": "\n--- اختيار لغة واجهة التحكم / CLI Language Selection ---",
    "lang_switch_prompt": "اختر اللغة / Select language (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ تم تغيير لغة الواجهة بنجاح!",
    "active_world": "العالم النشط",
    "language": "اللغة",
    "persona": "الشخصية",
    "final_response": "الرد النهائي",
    "confidence": "معامل اليقين/الثقة",
    "perf_took": "[PERF] استغرقت المعالجة {elapsed:.2f} ملي ثانية"
  },
  "fr": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Moteur d'IA Neuro-Symbolique - MVP      ",
    "banner_sub": "  Moteur de raisonnement logique honnête, transparent et 100% sans hallucination",
    "banner_options": "Options Disponibles:",
    "menu_ask": " 1. Poser une question au système en langage naturel",
    "menu_graph": " 2. Afficher le graphe de connaissances actuel",
    "menu_teach": " 3. Enseigner un nouveau fait au système (Ajouter relation)",
    "menu_worlds": " 4. Afficher les mondes de faits stockés",
    "menu_lang": " 5. Changer la langue du terminal",
    "menu_exit": " 6. Quitter",
    "menu_choice": "\nChoisissez une option (1-6): ",
    "ask_prompt": "\nPoser une question (ex: 'Est-ce que le lion est un animal?'): ",
    "graph_title": "\n--- Concepts et Relations actuels dans le Graphe ---",
    "graph_concepts_count": "Total Concepts (Nœuds): {count}",
    "graph_relations_count": "Total Relations (Arcs): {count}",
    "graph_registered": "Concepts Enregistrés:",
    "graph_cat_nodes": "  * Catégorie [{cat}]: {nodes}",
    "graph_active_rels": "\nRelations et Liens Actifs:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (Monde: {world})",
    "worlds_title": "\n--- Mondes de faits stockés dans le système ---",
    "worlds_available": "Mondes Disponibles: {worlds}",
    "worlds_active": "Monde Actif Actuellement: '{world}'",
    "teach_title": "\n--- Enseigner un nouveau fait ---",
    "teach_warning": "Attention: La relation sera ajoutée au graphe et active immédiatement dans le raisonnement!",
    "teach_concepts_available": "Concepts Disponibles:",
    "teach_choose_from": "\nChoisir le premier concept (Source): ",
    "teach_choose_to": "Choisir le deuxième concept (Cible): ",
    "teach_invalid_concept": "Sélection de concept invalide.",
    "teach_relations_available": "\nTypes de relations disponibles:",
    "teach_choose_rel": "Choisir le numéro de relation: ",
    "teach_which_world": "À quel monde appartient ce fait? (par défaut: reality): ",
    "teach_success": "\nFait ingéré avec succès!",
    "teach_error": "Erreur lors de l'apprentissage: {error}",
    "press_enter": "Appuyez sur [Entrée] pour continuer...",
    "exit_msg": "\nMerci! À bientôt pour une nouvelle session de raisonnement.",
    "invalid_choice": "Sélection invalide, veuillez entrer un nombre entre 1 et 6.",
    "lang_switch_title": "\n--- Sélection de la Langue du Terminal / CLI Language Selection ---",
    "lang_switch_prompt": "Choisir la langue (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ Langue changée avec succès!",
    "active_world": "Monde Actif",
    "language": "Langue",
    "persona": "Persona",
    "final_response": "Réponse Finale",
    "confidence": "Confiance",
    "perf_took": "[PERF] Traitement effectué en {elapsed:.2f}ms"
  },
  "es": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Motor de IA Neuro-Simbólico - MVP      ",
    "banner_sub": "  Motor de razonamiento lógico honesto, transparente y 100% libre de alucinaciones",
    "banner_options": "Opciones Disponibles:",
    "menu_ask": " 1. Hacer una pregunta en lenguaje natural",
    "menu_graph": " 2. Mostrar el grafo de conocimiento actual (Conceptos y Relaciones)",
    "menu_teach": " 3. Enseñar un nuevo hecho al sistema (Agregar relación)",
    "menu_worlds": " 4. Mostrar los mundos de hechos guardados",
    "menu_lang": " 5. Cambiar el idioma del terminal",
    "menu_exit": " 6. Salir",
    "menu_choice": "\nSeleccione una opción (1-6): ",
    "ask_prompt": "\nHacer pregunta (ej. '¿Es el león un animal?'): ",
    "graph_title": "\n--- Conceptos y Relaciones actuales en el Grafo ---",
    "graph_concepts_count": "Total Conceptos (Nodos): {count}",
    "graph_relations_count": "Total Relaciones (Aristas): {count}",
    "graph_registered": "Conceptos Registrados:",
    "graph_cat_nodes": "  * Categoría [{cat}]: {nodes}",
    "graph_active_rels": "\nRelaciones y Enlaces Activos:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (Mundo: {world})",
    "worlds_title": "\n--- Mundos de hechos guardados en el sistema ---",
    "worlds_available": "Mundos Disponibles: {worlds}",
    "worlds_active": "Mundo Activo Actualmente: '{world}'",
    "teach_title": "\n--- Enseñar un nuevo hecho ---",
    "teach_warning": "Advertencia: La relación se agregará al grafo y se activará de inmediato en el razonamiento.",
    "teach_concepts_available": "Conceptos Disponibles:",
    "teach_choose_from": "\nSeleccione el primer concepto (Origen): ",
    "teach_choose_to": "Seleccione el segundo concepto (Destino): ",
    "teach_invalid_concept": "Selección de concepto no válida.",
    "teach_relations_available": "\nTipos de relaciones disponibles:",
    "teach_choose_rel": "Seleccione número de relación: ",
    "teach_which_world": "¿A qué mundo pertenece este hecho? (por defecto: reality): ",
    "teach_success": "\n¡Hecho guardado con éxito!",
    "teach_error": "Error al enseñar hecho: {error}",
    "press_enter": "Presione [Enter] para continuar...",
    "exit_msg": "\n¡Gracias! Nos vemos en una nueva sesión de razonamiento.",
    "invalid_choice": "Selección no válida, ingrese un número entre 1 y 6.",
    "lang_switch_title": "\n--- Selección de idioma del terminal / CLI Language Selection ---",
    "lang_switch_prompt": "Seleccione idioma (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ ¡Idioma cambiado con éxito!",
    "active_world": "Mundo Activo",
    "language": "Idioma",
    "persona": "Persona",
    "final_response": "Respuesta Final",
    "confidence": "Confianza",
    "perf_took": "[PERF] El procesamiento tardó {elapsed:.2f}ms"
  },
  "zh": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - 神经符号 AI 推理引擎 - MVP      ",
    "banner_sub": "  诚实、透明且 100% 无幻觉的逻辑推理引擎",
    "banner_options": "可用选项:",
    "menu_ask": " 1. 使用自然语言向系统提问",
    "menu_graph": " 2. 显示当前知识图谱（概念与关系）",
    "menu_teach": " 3. 传授新事实（在图谱中添加关系）",
    "menu_worlds": " 4. 显示存储的事实世界",
    "menu_lang": " 5. 更改命令行界面语言",
    "menu_exit": " 6. 退出",
    "menu_choice": "\n请选择选项 (1-6): ",
    "ask_prompt": "\n向逻辑大脑提问（例如：'狮子是动物吗？'）： ",
    "graph_title": "\n--- 知识图谱中的当前概念与关系 ---",
    "graph_concepts_count": "总概念（节点）: {count}",
    "graph_relations_count": "总关系（边）: {count}",
    "graph_registered": "已注册概念:",
    "graph_cat_nodes": "  * 分类 [{cat}]: {nodes}",
    "graph_active_rels": "\n活跃关系与链接:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (世界: {world})",
    "worlds_title": "\n--- 系统中存储的事实世界 ---",
    "worlds_available": "可用世界: {worlds}",
    "worlds_active": "当前活跃世界: '{world}'",
    "teach_title": "\n--- 传授新事实 ---",
    "teach_warning": "警告: 该关系将添加到图谱中，并在推理中立即生效！",
    "teach_concepts_available": "可用概念:",
    "teach_choose_from": "\n选择第一个概念（源）: ",
    "teach_choose_to": "选择第二个概念（目标）: ",
    "teach_invalid_concept": "无效的概念选择。",
    "teach_relations_available": "\n可用关系类型:",
    "teach_choose_rel": "选择关系编号: ",
    "teach_which_world": "此事实属于哪个世界？（默认: reality）: ",
    "teach_success": "\n事实传授成功！",
    "teach_error": "传授错误: {error}",
    "press_enter": "按 [回车键] 继续...",
    "exit_msg": "\n谢谢！期待下次推理会话再见。",
    "invalid_choice": "选择无效，请输入 1 到 6 之间的数字。",
    "lang_switch_title": "\n--- 命令行界面语言选择 / CLI Language Selection ---",
    "lang_switch_prompt": "选择语言 (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ 语言更改成功！",
    "active_world": "活跃世界",
    "language": "语言",
    "persona": "角色",
    "final_response": "最终回答",
    "confidence": "置信度",
    "perf_took": "[PERF] 处理耗时 {elapsed:.2f}毫秒"
  },
  "tr": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Nöro-Sembolik Yapay Zeka Motoru - MVP      ",
    "banner_sub": "  Dürüst, Şeffaf ve %100 Halüsinasyonsuz Mantıksal Muhakeme Motoru",
    "banner_options": "Mevcut Seçenekler:",
    "menu_ask": " 1. Doğal dilde sisteme bir soru sorun",
    "menu_graph": " 2. Mevcut bilgi grafiğini göster (Kavramlar ve İlişkiler)",
    "menu_teach": " 3. Sisteme yeni bir gerçek öğret (Grafiğe ilişki ekle)",
    "menu_worlds": " 4. Kaydedilmiş gerçek dünyalarını göster",
    "menu_lang": " 5. Terminal Arayüzü Dilini Değiştir",
    "menu_exit": " 6. Çıkış",
    "menu_choice": "\nBir seçenek seçin (1-6): ",
    "ask_prompt": "\nMantıksal zihne sorun (ör. 'Aslan bir hayvan mıdır?'): ",
    "graph_title": "\n--- Bilgi Grafiğindeki Mevcut Kavramlar ve İlişkiler ---",
    "graph_concepts_count": "Toplam Kavram (Düğüm): {count}",
    "graph_relations_count": "Toplam İlişki (Kenar): {count}",
    "graph_registered": "Kayıtlı Kavramlar:",
    "graph_cat_nodes": "  * Kategori [{cat}]: {nodes}",
    "graph_active_rels": "\nAktif İlişkiler ve Bağlantılar:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (Dünya: {world})",
    "worlds_title": "\n--- Sistemde Kayıtlı Gerçek Dünyaları ---",
    "worlds_available": "Mevcut Dünyalar: {worlds}",
    "worlds_active": "Aktif Dünya: '{world}'",
    "teach_title": "\n--- Yeni Bir Gerçek Öğret ---",
    "teach_warning": "Uyarı: İlişki grafiğe eklenecek ve akıl yürütmede hemen aktif olacaktır!",
    "teach_concepts_available": "Mevcut Kavramlar:",
    "teach_choose_from": "\nİlk kavramı seçin (Kaynak): ",
    "teach_choose_to": "İkinci kavramı seçin (Hedef): ",
    "teach_invalid_concept": "Geçersiz kavram seçimi.",
    "teach_relations_available": "\nMevcut İlişki Türleri:",
    "teach_choose_rel": "İlişki numarasını seçin: ",
    "teach_which_world": "Bu gerçek hangi dünyaya ait? (varsayılan: reality): ",
    "teach_success": "\nGerçek başarıyla alındı!",
    "teach_error": "Öğretme sırasında hata oluştu: {error}",
    "press_enter": "Devam etmek için [Enter] tuşuna basın...",
    "exit_msg": "\nTeşekkürler! Yeni bir akıl yürütme oturumunda görüşmek üzere.",
    "invalid_choice": "Geçersiz seçim, lütfen 1 ile 6 arasında bir sayı girin.",
    "lang_switch_title": "\n--- Terminal Dili Seçimi / CLI Language Selection ---",
    "lang_switch_prompt": "Dil seçin (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ Dil başarıyla değiştirildi!",
    "active_world": "Aktif Dünya",
    "language": "Dil",
    "persona": "Persona",
    "final_response": "Final Yanıtı",
    "confidence": "Güven Derecesi",
    "perf_took": "[PERF] İşlem {elapsed:.2f}ms sürdü"
  },
  "de": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Neuro-Symbolische KI-Engine - MVP      ",
    "banner_sub": "  Ehrliche, transparente und 100% halluzinationsfreie logische Argumentations-Engine",
    "banner_options": "Verfügbare Optionen:",
    "menu_ask": " 1. Stellen Sie dem System eine Frage in natürlicher Sprache",
    "menu_graph": " 2. Zeigen Sie den aktuellen Wissensgraphen an",
    "menu_teach": " 3. Bringen Sie dem System einen neuen Fakt bei (Beziehung hinzufügen)",
    "menu_worlds": " 4. Gespeicherte Faktenwelten anzeigen",
    "menu_lang": " 5. CLI-Schnittstellensprache ändern",
    "menu_exit": " 6. Beenden",
    "menu_choice": "\nWählen Sie eine Option (1-6): ",
    "ask_prompt": "\nFragen Sie den logischen Verstand (z. B. 'Ist ein Löwe ein Tier?'): ",
    "graph_title": "\n--- Aktuelle Begriffe und Beziehungen im Wissensgraphen ---",
    "graph_concepts_count": "Begriffe insgesamt (Knoten): {count}",
    "graph_relations_count": "Beziehungen insgesamt (Kanten): {count}",
    "graph_registered": "Registrierte Begriffe:",
    "graph_cat_nodes": "  * Kategorie [{cat}]: {nodes}",
    "graph_active_rels": "\nAktive Beziehungen und Verbindungen:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (Welt: {world})",
    "worlds_title": "\n--- Im System gespeicherte Faktenwelten ---",
    "worlds_available": "Verfügbare Welten: {worlds}",
    "worlds_active": "Aktuell aktive Welt: '{world}'",
    "teach_title": "\n--- Einen neuen Fakt lehren ---",
    "teach_warning": "Warnung: Die Beziehung wird dem Graphen hinzugefügt und ist sofort wirksam!",
    "teach_concepts_available": "Verfügbare Begriffe:",
    "teach_choose_from": "\nWählen Sie den ersten Begriff (Quelle): ",
    "teach_choose_to": "Wählen Sie den zweiten Begriff (Ziel): ",
    "teach_invalid_concept": "Ungültige Begriffsauswahl.",
    "teach_relations_available": "\nVerfügbare Beziehungstypen:",
    "teach_choose_rel": "Beziehungsnummer auswählen: ",
    "teach_which_world": "Zu welcher Welt gehört dieser Fakt? (Standard: reality): ",
    "teach_success": "\nFakt erfolgreich gelernt!",
    "teach_error": "Fehler beim Lernen: {error}",
    "press_enter": "Drücken Sie [Enter], um fortzufahren...",
    "exit_msg": "\nVielen Dank! Bis zu einer neuen Argumentationssitzung.",
    "invalid_choice": "Ungültige Auswahl, bitte geben Sie eine Zahl zwischen 1 und 6 ein.",
    "lang_switch_title": "\n--- CLI-Sprachauswahl / CLI Language Selection ---",
    "lang_switch_prompt": "Sprache wählen (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ Sprache erfolgreich geändert!",
    "active_world": "Aktive Welt",
    "language": "Sprache",
    "persona": "Persona",
    "final_response": "Antwort",
    "confidence": "Konfidenz",
    "perf_took": "[PERF] Verarbeitung dauerte {elapsed:.2f}ms"
  },
  "ru": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Нейро-символический процессор ИИ - MVP      ",
    "banner_sub": "  Честный, прозрачный и 100% свободный от галлюцинаций логический движок",
    "banner_options": "Доступные варианты:",
    "menu_ask": " 1. Задать вопрос на естественном языке",
    "menu_graph": " 2. Показать текущий граф знаний (Концепты и Связи)",
    "menu_teach": " 3. Обучить систему новому факту (Добавить связь в граф)",
    "menu_worlds": " 4. Показать сохраненные миры фактов",
    "menu_lang": " 5. Изменить язык интерфейса терминала",
    "menu_exit": " 6. Выйти",
    "menu_choice": "\nВыберите вариант (1-6): ",
    "ask_prompt": "\nСпросите логический разум (например, 'Лев — животное?'): ",
    "graph_title": "\n--- Текущие концепты и связи в графе знаний ---",
    "graph_concepts_count": "Всего концептов (Узлов): {count}",
    "graph_relations_count": "Всего отношений (Связей): {count}",
    "graph_registered": "Зарегистрированные концепты:",
    "graph_cat_nodes": "  * Категория [{cat}]: {nodes}",
    "graph_active_rels": "\nАктивные связи и отношения:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (Мир: {world})",
    "worlds_title": "\n--- Сохраненные миры фактов в системе ---",
    "worlds_available": "Доступные миры: {worlds}",
    "worlds_active": "Текущий активный мир: '{world}'",
    "teach_title": "\n--- Обучить систему новому факту ---",
    "teach_warning": "Внимание: Отношение будет добавлено в граф и сразу же станет активным в рассуждениях!",
    "teach_concepts_available": "Доступные концепты:",
    "teach_choose_from": "\nВыберите первый концепт (Источник): ",
    "teach_choose_to": "Выберите второй концепт (Цель): ",
    "teach_invalid_concept": "Неверный выбор концепта.",
    "teach_relations_available": "\nДоступные типы отношений:",
    "teach_choose_rel": "Выберите номер отношения: ",
    "teach_which_world": "К какому миру относится этот факт? (по умолчанию: reality): ",
    "teach_success": "\nФакт успешно усвоен!",
    "teach_error": "Ошибка при обучении: {error}",
    "press_enter": "Нажмите [Enter] для продолжения...",
    "exit_msg": "\nСпасибо! До встречи в новом сеансе рассуждений.",
    "invalid_choice": "Неверный выбор, введите число от 1 до 6.",
    "lang_switch_title": "\n--- Выбор языка терминала / CLI Language Selection ---",
    "lang_switch_prompt": "Выберите язык (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ Язык успешно изменен!",
    "active_world": "Активный мир",
    "language": "Язык",
    "persona": "Персона",
    "final_response": "Итоговый ответ",
    "confidence": "Достоверность",
    "perf_took": "[PERF] Обработка заняла {elapsed:.2f}мс"
  },
  "pt": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - Motor de IA Neuro-Simbólica - MVP      ",
    "banner_sub": "  Motor de raciocínio lógico honesto, transparente e 100% livre de alucinações",
    "banner_options": "Opções Disponíveis:",
    "menu_ask": " 1. Fazer uma pergunta ao sistema em linguagem natural",
    "menu_graph": " 2. Mostrar o grafo de conhecimento atual (Conceitos e Relações)",
    "menu_teach": " 3. Ensinar um novo fato ao sistema (Adicionar relação)",
    "menu_worlds": " 4. Mostrar os mundos de fatos armazenados",
    "menu_lang": " 5. Alterar o idioma do terminal",
    "menu_exit": " 6. Sair",
    "menu_choice": "\nEscolha uma opção (1-6): ",
    "ask_prompt": "\nPergunte à mente lógica (ex: 'O leão é um animal?'): ",
    "graph_title": "\n--- Conceitos e Relações atuais no Grafo de Conhecimento ---",
    "graph_concepts_count": "Total de Conceitos (Nós): {count}",
    "graph_relations_count": "Total de Relações (Arestas): {count}",
    "graph_registered": "Conceitos Registrados:",
    "graph_cat_nodes": "  * Categoria [{cat}]: {nodes}",
    "graph_active_rels": "\nRelações e Conexões Ativas:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (Mundo: {world})",
    "worlds_title": "\n--- Mundos de fatos armazenados no sistema ---",
    "worlds_available": "Mundos Disponíveis: {worlds}",
    "worlds_active": "Mundo Ativo Atualmente: '{world}'",
    "teach_title": "\n--- Ensinar um novo fato ---",
    "teach_warning": "Aviso: A relação será adicionada ao grafo e estará ativa imediatamente no raciocínio!",
    "teach_concepts_available": "Conceitos Disponíveis:",
    "teach_choose_from": "\nEscolha o primeiro conceito (Origem): ",
    "teach_choose_to": "Escolha o segundo conceito (Destino): ",
    "teach_invalid_concept": "Seleção de conceito inválida.",
    "teach_relations_available": "\nTipos de relações disponíveis:",
    "teach_choose_rel": "Escolha o número da relação: ",
    "teach_which_world": "A qual mundo este fato pertence? (padrão: reality): ",
    "teach_success": "\nFato aprendido com sucesso!",
    "teach_error": "Erro ao ensinar fato: {error}",
    "press_enter": "Pressione [Enter] para continuar...",
    "exit_msg": "\nObrigado! Até uma próxima sessão de raciocínio.",
    "invalid_choice": "Seleção inválida, digite um número entre 1 e 6.",
    "lang_switch_title": "\n--- Seleção de idioma do terminal / CLI Language Selection ---",
    "lang_switch_prompt": "Selecione o idioma (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ Idioma alterado com sucesso!",
    "active_world": "Mundo Ativo",
    "language": "Idioma",
    "persona": "Persona",
    "final_response": "Resposta Final",
    "confidence": "Confiança",
    "perf_took": "[PERF] O processamento levou {elapsed:.2f}ms"
  },
  "ja": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - 神経記号論理 AI エンジン - MVP      ",
    "banner_sub": "  誠実で透明、100%ハルシネーションフリーの論理推論エンジン",
    "banner_options": "利用可能なオプション:",
    "menu_ask": " 1. 自然言語でシステムに質問する",
    "menu_graph": " 2. 現在の知識グラフを表示する (概念と関係)",
    "menu_teach": " 3. システムに新しい事実を教える (グラフに関係を追加)",
    "menu_worlds": " 4. 保存された事実の世界を表示する",
    "menu_lang": " 5. CLI表示言語を変更する",
    "menu_exit": " 6. 終了する",
    "menu_choice": "\nオプションを選択してください (1-6): ",
    "ask_prompt": "\n論理の脳に尋ねる (例: 'ライオンは動物ですか？'): ",
    "graph_title": "\n--- 知識グラフの現在の概念と関係 ---",
    "graph_concepts_count": "概念の総数 (ノード): {count}",
    "graph_relations_count": "関係の総数 (エッジ): {count}",
    "graph_registered": "登録された概念:",
    "graph_cat_nodes": "  * カテゴリ [{cat}]: {nodes}",
    "graph_active_rels": "\nアクティブな関係とリンク:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (世界: {world})",
    "worlds_title": "\n--- システムに保存されている事実の世界 ---",
    "worlds_available": "利用可能な世界: {worlds}",
    "worlds_active": "現在アクティブな世界: '{world}'",
    "teach_title": "\n--- 新しい事実を教える ---",
    "teach_warning": "警告: 関係はグラフに追加され、推論で即座にアクティブになります！",
    "teach_concepts_available": "利用可能な概念:",
    "teach_choose_from": "\n最初の概念を選択してください (ソース): ",
    "teach_choose_to": "2番目の概念を選択してください (ターゲット): ",
    "teach_invalid_concept": "無効な概念の選択です。",
    "teach_relations_available": "\n利用可能な関係タイプ:",
    "teach_choose_rel": "関係番号を選択してください: ",
    "teach_which_world": "この事実はどの世界に属しますか？ (デフォルト: reality): ",
    "teach_success": "\n事実が正常に取り込まれました！",
    "teach_error": "教示エラー: {error}",
    "press_enter": "[Enter] を押して続行します...",
    "exit_msg": "\nありがとうございました！またの推論セッションでお会いしましょう。",
    "invalid_choice": "無効な選択です。1から6の数字を入力してください。",
    "lang_switch_title": "\n--- ターミナル表示言語の選択 / CLI Language Selection ---",
    "lang_switch_prompt": "言語を選択してください (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ 表示言語を変更しました！",
    "active_world": "アクティブな世界",
    "language": "言語",
    "persona": "ペルソナ",
    "final_response": "最終回答",
    "confidence": "確信度",
    "perf_took": "[PERF] 処理時間 {elapsed:.2f}ms"
  },
  "ko": {
    "banner_title": "=" * 75,
    "banner_header": "      TheOne - 신경-기호 AI 엔진 - MVP      ",
    "banner_sub": "  정직하고 투명하며 100% 환각 없는 논리 추론 엔진",
    "banner_options": "이용 가능한 옵션:",
    "menu_ask": " 1. 자연어로 시스템에 질문하기",
    "menu_graph": " 2. 현재 지식 그래프 표시 (개념 및 관계)",
    "menu_teach": " 3. 시스템에 새로운 사실 가르치기 (관계 추가)",
    "menu_worlds": " 4. 저장된 사실 세계 표시",
    "menu_lang": " 5. CLI 인터페이스 언어 변경",
    "menu_exit": " 6. 종료",
    "menu_choice": "\n옵션을 선택하십시오 (1-6): ",
    "ask_prompt": "\n논리 엔진에 질문하십시오 (예: '사자는 동물입니까?'): ",
    "graph_title": "\n--- 지식 그래프의 현재 개념 및 관계 ---",
    "graph_concepts_count": "총 개념 수 (노드): {count}",
    "graph_relations_count": "총 관계 수 (엣지): {count}",
    "graph_registered": "등록된 개념:",
    "graph_cat_nodes": "  * 카테고리 [{cat}]: {nodes}",
    "graph_active_rels": "\n활성 관계 및 링크:",
    "graph_rel_format": "  - [{from_lbl}] --({rel})--> [{to_lbl}]   (세계: {world})",
    "worlds_title": "\n--- 시스템에 저장된 사실 세계 ---",
    "worlds_available": "이용 가능한 세계: {worlds}",
    "worlds_active": "현재 활성화된 세계: '{world}'",
    "teach_title": "\n--- 새로운 사실 가르치기 ---",
    "teach_warning": "경고: 관계가 그래프에 추가되며 추론에 즉시 반영됩니다!",
    "teach_concepts_available": "이용 가능한 개념:",
    "teach_choose_from": "\n첫 번째 개념을 선택하십시오 (소스): ",
    "teach_choose_to": "두 번째 개념을 선택하십시오 (타깃): ",
    "teach_invalid_concept": "잘못된 개념 선택입니다.",
    "teach_relations_available": "\n이용 가능한 관계 유형:",
    "teach_choose_rel": "관계 번호를 선택하십시오: ",
    "teach_which_world": "이 사실은 어떤 세계에 속합니까? (기본값: reality): ",
    "teach_success": "\n사실이 성공적으로 주입되었습니다!",
    "teach_error": "가르치기 오류: {error}",
    "press_enter": "[Enter]를 눌러 계속하십시오...",
    "exit_msg": "\n감사합니다! 새로운 추론 세션에서 뵙겠습니다.",
    "invalid_choice": "잘못된 선택입니다. 1에서 6 사이의 숫자를 입력해 주십시오.",
    "lang_switch_title": "\n--- CLI 언어 선택 / CLI Language Selection ---",
    "lang_switch_prompt": "언어를 선택하십시오 (en, ar, fr, es, zh, tr, de, ru, pt, ja, ko): ",
    "lang_switch_success": "✅ 언어가 성공적으로 변경되었습니다!",
    "active_world": "활성 세계",
    "language": "언어",
    "persona": "페르소나",
    "final_response": "최종 답변",
    "confidence": "신뢰도",
    "perf_took": "[PERF] 처리에 {elapsed:.2f}ms 소요되었습니다"
  }
}

def t(key, **kwargs):
    global active_lang
    lang_dict = translations.get(active_lang, translations["en"])
    text = lang_dict.get(key, translations["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def print_banner():
    print(t("banner_title"))
    print(t("banner_header"))
    print(t("banner_sub"))
    print(t("banner_title"))
    print(t("banner_options"))
    print(t("menu_ask"))
    print(t("menu_graph"))
    print(t("menu_teach"))
    print(t("menu_worlds"))
    print(t("menu_lang"))
    print(t("menu_exit"))
    print("-" * 75)

def show_graph(handler):
    print(t("graph_title"))
    print(t("graph_concepts_count", count=handler.graph.number_of_nodes()))
    print(t("graph_relations_count", count=handler.graph.number_of_edges()))
    print("-" * 50)
    
    # Display concepts grouped by category
    categories = {}
    for node, data in handler.graph.nodes(data=True):
        if data.get("type") == "concept":
            cat = data.get("category") or "other"
            lbl = data.get("labels", [node])[0]
            categories.setdefault(cat, []).append(f"{lbl} ({node})")
            
    print(t("graph_registered"))
    for cat, nodes in categories.items():
        print(t("graph_cat_nodes", cat=cat, nodes=', '.join(nodes)))
        
    print(t("graph_active_rels"))
    for from_node, to_node, data in handler.graph.edges(data=True):
        rel = data.get("relation")
        world = data.get("world", "reality")
        # Get labels
        from_lbl = handler.graph.nodes[from_node].get("labels", [from_node])[0] if from_node in handler.graph else from_node
        to_lbl = handler.graph.nodes[to_node].get("labels", [to_node])[0] if to_node in handler.graph else to_node
        print(t("graph_rel_format", from_lbl=from_lbl, rel=rel, to_lbl=to_lbl, world=world))
    print("-" * 50)

def show_worlds(handler):
    print(t("worlds_title"))
    worlds = set()
    for _, _, data in handler.graph.edges(data=True):
        if data.get("type") == "fact":
            worlds.add(data.get("world", "reality"))
            
    print(t("worlds_available", worlds=list(worlds)))
    print(t("worlds_active", world=handler.active_world))
    print("-" * 50)

def teach_system(handler):
    print(t("teach_title"))
    print(t("teach_warning"))
    print("-" * 50)
    
    # Simple interactive teaching
    print(t("teach_concepts_available"))
    concepts = [node for node, data in handler.graph.nodes(data=True) if data.get("type") == "concept"]
    for idx, c in enumerate(concepts):
        lbl = handler.graph.nodes[c].get("labels", [c])[0]
        print(f" {idx + 1}. {lbl} ({c})")
        
    try:
        from_idx = int(input(t("teach_choose_from"))) - 1
        to_idx = int(input(t("teach_choose_to"))) - 1
        
        if 0 <= from_idx < len(concepts) and 0 <= to_idx < len(concepts):
            from_c = concepts[from_idx]
            to_c = concepts[to_idx]
            
            print(t("teach_relations_available"))
            print(" 1. is_a")
            print(" 2. lives_in")
            print(" 3. has_property")
            print(" 4. requires")
            print(" 5. provides")
            
            rel_choice = input(t("teach_choose_rel"))
            rel_map = {
                "1": "is_a",
                "2": "lives_in",
                "3": "has_property",
                "4": "requires",
                "5": "provides"
            }
            rel = rel_map.get(rel_choice, "has_property")
            
            world_choice = input(t("teach_which_world")).strip() or "reality"
            
            # Use add_or_update_fact to handle duplicates and contradictions
            update_res = handler.add_or_update_fact(
                from_c,
                to_c,
                relation=rel,
                world=world_choice,
                confidence=1.0,
                interactive=True,
                language=active_lang
            )
            print(f"\n{update_res['message']}")
        else:
            print(t("teach_invalid_concept"))
    except Exception as e:
        print(t("teach_error", error=e))

def change_language():
    global active_lang
    print(t("lang_switch_title"))
    choice = input(t("lang_switch_prompt")).strip().lower()
    if choice in translations:
        active_lang = choice
        print(t("lang_switch_success"))
    else:
        print(f"⚠️ Unsupported language choice: {choice}. Retaining current language: {active_lang}")

def main():
    global active_lang
    import argparse
    parser = argparse.ArgumentParser(description="TheOne Neuro-Symbolic AI CLI")
    parser.add_argument("--trace-level", type=str, choices=["detailed", "minimal"], default="detailed", help="Trace level verbosity")
    args = parser.parse_args()
    
    trace_level = args.trace_level

    # 1. Initialize databases
    handler = GraphHandler()
    
    ontology_path = "data/animals_ontology_small.json"
    facts_path = "data/animals_facts.json"
    language_rules_path = "data/animals_language_rules.json"
    
    # Resolve paths relative to working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(ontology_path):
        ontology_path = os.path.join(base_dir, ontology_path)
        facts_path = os.path.join(base_dir, facts_path)
        language_rules_path = os.path.join(base_dir, language_rules_path)
        
    try:
        handler.load_databases(ontology_path, facts_path, language_rules_path)
    except Exception as e:
        print(f"Error loading databases: {e}")
        sys.exit(1)
        
    reasoner = SimpleReasoner(handler)
    persona_engine = MultilingualPersonaEngine(handler)
    
    # Print welcome
    print_banner()
    
    while True:
        choice = input(t("menu_choice")).strip()
        
        if choice == "1":
            query = input(t("ask_prompt")).strip()
            if not query:
                continue
                
            # Run pipeline
            # 1. Detect language to parse query correctly
            detected_lang = persona_engine.language_engine.detect_language(query)
            selected_lang = persona_engine.language_engine.select_language(detected_lang, user_preference=active_lang)
            
            # 2. Logical reasoning
            start_time = time.perf_counter()
            res = reasoner.process_query(query, interactive=True, language=selected_lang)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            # 3. Multilingual Persona response generation
            history = reasoner.conversation_manager.get_history()
            engine_res = persona_engine.process_response(query, res, conversation_history=history, user_preference=active_lang)
            response = engine_res["response"]
            lang = engine_res["language"]
            persona = engine_res["persona"]
            
            print("\n" + "=" * 50)
            print(f"{t('active_world')}: '{handler.active_world}'")
            print(f"{t('language')}: {lang} | {t('persona')}: {persona}")
            print(f"{t('final_response')}:\n👉 {response}")
            print("=" * 50)
            
            # Print logical trace and performance if trace level is detailed
            if trace_level == "detailed":
                formatted_trace = persona_engine.expression_renderer.format_trace(res.get("trace", []), lang)
                print(formatted_trace)
                print(f"🎯 {t('confidence')}: {res.get('confidence', 1.0):.2f}")
                print(t("perf_took", elapsed=elapsed_ms))
                print("=" * 50)
            
        elif choice == "2":
            show_graph(handler)
        elif choice == "3":
            teach_system(handler)
        elif choice == "4":
            show_worlds(handler)
        elif choice == "5":
            change_language()
            print_banner()
        elif choice == "6" or choice.lower() == "q":
            print(t("exit_msg"))
            break
        else:
            print(t("invalid_choice"))

if __name__ == "__main__":
    main()
