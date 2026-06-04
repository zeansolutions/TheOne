#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner function
show_banner() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${GREEN}      نظام عقل منطقي (TheOne - Neuro-Symbolic AI Engine) - Control Script     ${NC}"
    echo -e "${BLUE}======================================================================${NC}"
}

# Help function
show_help() {
    show_banner
    echo -e "${YELLOW}الاستخدام (Usage):${NC}"
    echo -e "  ./start.sh [الأمر / Command]"
    echo ""
    echo -e "${YELLOW}الأوامر المتاحة (Available Commands):${NC}"
    echo -e "  ${GREEN}run${NC}      : تشغيل المحرك التفاعلي للتحدث مع عقل منطقي (CLI Chatbot)"
    echo -e "             - يدعم اللغات: العربية (ar)، الإنجليزية (en)، والفرنسية (fr)"
    echo -e "             - كشف تلقائي للغة مع تثبيت سياق الحوار"
    echo -e "             - اختيار ديناميكي للشخصية المناسبة (الحكيم، الباحث، المرشد)"
    echo -e "             - تذكر سياق الكيانات والضمائر عبر اللغات المختلفة"
    echo -e "             - حل تعارض الحقائق التفاعلي والتعلم اللحظي للحقائق"
    echo -e "  ${GREEN}gui${NC}      : تشغيل الواجهة الرسومية المستقبلية للتطبيق باستخدام Electron & React (Futuristic Desktop GUI)"
    echo -e "             - يدعم 11 لغة مع التحول لاتجاه RTL تلقائياً"
    echo -e "             - محاكاة للشبكات العصبية والسيالات العصبية مع حركة ديناميكية"
    echo -e "             - التحكم بالحقائق وقائمة المفاهيم ودورة النوم والتلقين المباشر وحل التعارضات"
    echo -e "  ${GREEN}sleep${NC}    : تشغيل دورة النوم المعرفية لتنظيف وتحسين شبكة المعرفة (Cognitive Sleep Cycle)"
    echo -e "             - يدعم خيارات: --depth=2 --cleanup"
    echo -e "  ${GREEN}curious${NC}  : تشغيل محرك الفضول المعرفي لرصد الفجوات المعرفية وتوليد الأسئلة (Curiosity Engine)"
    echo -e "             - يدعم خيارات: --limit=5 --lang=ar"
    echo -e "  ${GREEN}test${NC}     : تشغيل اختبارات التحقق الآلية الكاملة (Run pytest Suite)"
    echo -e "             - يختبر 32 سيناريو تشمل استدلال الصرف والمنطق والتعارض واللغات المتعددة والشخصيات"
    echo -e "  ${GREEN}setup${NC}    : تهيئة البيئة الافتراضية وتثبيت المكتبات المطلوبة (Initialize venv)"
    echo -e "  ${GREEN}help${NC}     : عرض دليل التعليمات الحالي (Display this help menu)"
    echo ""
    echo -e "${YELLOW}أمثلة (Examples):${NC}"
    echo -e "  ./start.sh run"
    echo -e "  ./start.sh sleep --depth=2 --cleanup"
    echo -e "  ./start.sh curious --limit=3"
    echo -e "  ./start.sh test"
    echo -e "${BLUE}======================================================================${NC}"
}

# Setup environment function
setup_env() {
    echo -e "${BLUE}[+] تهيئة البيئة الافتراضية وتثبيت الاعتمادات...${NC}"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}[✓] تم إنشاء المجلد venv بنجاح.${NC}"
    else
        echo -e "${YELLOW}[!] البيئة الافتراضية venv موجودة بالفعل.${NC}"
    fi
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    echo -e "${GREEN}[✓] تم تثبيت كافة المكتبات بنجاح!${NC}"
}

# Main routing logic
if [ "$#" -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    --help|-h|help)
        show_help
        ;;
    run|start)
        show_banner
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}[!] البيئة الافتراضية غير مهيأة بعد. جاري التشغيل التلقائي للتنصيب...${NC}"
            setup_env
        fi
        echo -e "${BLUE}[+] جاري تشغيل واجهة التيرمينال التفاعلية لعقل منطقي...${NC}"
        echo ""
        PYTHONPATH=. ./venv/bin/python main.py
        ;;
    gui)
        show_banner
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}[!] البيئة الافتراضية غير مهيأة بعد. جاري التشغيل التلقائي للتنصيب...${NC}"
            setup_env
        fi
        echo -e "${BLUE}[+] التحقق من وجود الاعتمادات للواجهة الرسومية...${NC}"
        if [ ! -d "desktop-gui/node_modules" ]; then
            echo -e "${YELLOW}[!] المجلد node_modules غير موجود. جاري تثبيت المكتبات عبر npm...${NC}"
            (cd desktop-gui && npm install)
        fi
        
        echo -e "${BLUE}[+] جاري بناء واجهة React...${NC}"
        (cd desktop-gui && npm run build)
        
        echo -e "${GREEN}[✓] جاري تشغيل تطبيق Electron...${NC}"
        (cd desktop-gui && npm run electron)
        ;;
    sleep)
        show_banner
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}[!] البيئة الافتراضية غير مهيأة بعد. جاري التشغيل التلقائي للتنصيب...${NC}"
            setup_env
        fi
        echo -e "${BLUE}[+] جاري تشغيل دورة النوم المعرفية...${NC}"
        echo ""
        PYTHONPATH=. ./venv/bin/python sleep.py "${@:2}"
        ;;
    curious|curiosity)
        show_banner
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}[!] البيئة الافتراضية غير مهيأة بعد. جاري التشغيل التلقائي للتنصيب...${NC}"
            setup_env
        fi
        echo -e "${BLUE}[+] جاري تشغيل محرك الفضول المعرفي...${NC}"
        echo ""
        PYTHONPATH=. ./venv/bin/python curious.py "${@:2}"
        ;;
    test)
        show_banner
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}[!] البيئة الافتراضية غير مهيأة بعد. جاري التشغيل التلقائي للتنصيب...${NC}"
            setup_env
        fi
        echo -e "${BLUE}[+] جاري تشغيل اختبارات pytest التلقائية...${NC}"
        echo ""
        PYTHONPATH=. ./venv/bin/pytest -v
        ;;
    setup)
        setup_env
        ;;
    *)
        echo -e "${RED}[خطأ] الأمر '$1' غير معروف!${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
