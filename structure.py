import os
import logging
from typing import Dict, Optional

import telebot
from telebot import types
from dotenv import load_dotenv

# ─── الإعدادات الأساسية ──────────────────────────────────────────────────────
load_dotenv()

# اسم المتغير في ملف .env يجب أن يكون structure_Bot كما هو مطلوب
TOKEN = os.getenv("structure_Bot")

if not TOKEN:
    raise ValueError("❌ لم يتم العثور على التوكن! تأكد من وجود structure_Bot في ملف .env")

# قائمة معرفات المسؤولين (يمكن إضافتها في .env مفصولة بفواصل)
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# إعداد التسجيل للأخطاء
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

# ─── ذاكرة التخزين المؤقت لمعرفات الصور (لتحسين السرعة) ─────────────────────
cached_file_ids: Dict[str, str] = {}

# ─── روابط الصور (يمكن استبدالها لاحقًا بمعرفات مباشرة) ─────────────────────
SECTION_LOGOS = {
    "MAIN":      "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4782.jpeg",
    "RECEPTION": "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4793.jpeg",
    "LOGIC":     "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4790.jpeg",
    "SECURITY":  "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4791.jpeg",
    "ARCHIVE":   "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4792.jpeg",
    "CORE":      "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4794.jpeg",
    "STRATEGY":  "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4788.jpeg",
    "VISUAL":    "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4787.jpeg",
    "COMMAND":   "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4780.jpeg"
}

# ─── نصوص الأزرار (ثوابت) ────────────────────────────────────────────────────
BTN_RECEPTION = '🤝 قـسـم الاسـتـقـبال ╎ 𝐑𝐄𝐂𝐄𝐏𝐓𝐈𝐎𝐍'
BTN_LOGIC     = '🧠 مُـخـتـبـر الـمـنـطـق ╎ 𝐋𝐎𝐆𝐈𝐂   𝐋𝐀𝐁'
BTN_SEC       = '🛡️ أمـن الـبـيـانـات ╎ 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘   𝐂𝐄𝐍𝐓𝐄𝐑'
BTN_ARCHIVE   = '📂 الأرشــيــف ╎ 𝐓𝐇𝐄   𝐀𝐑𝐂𝐇𝐈𝐕𝐄'
BTN_CORE      = '⚙️ نـواة الـتـطويـر ╎ 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐌𝐄𝐍𝐓   𝐂𝐎𝐑𝐄'
BTN_VISUAL    = '🎨 واجـهة الـنظام ╎ 𝐕𝐈𝐒𝐔𝐀𝐋   𝐀𝐑𝐂𝐀𝐍𝐄'
BTN_STRATEGY  = '🧠 غـرفـة الاسـتـشـارة ╎ 𝐒𝐓𝐑𝐀𝐓𝐄𝐆𝐘   𝐑𝐎𝐎𝐌'
BTN_DEV       = '👤 الـتواصل مـع الـقـيادة ╎ 𝐇𝐈𝐆𝐇   𝐂𝐎𝐌𝐌𝐀𝐍𝐃'

# ─── ردود الأزرار (محتوى كل قسم) ────────────────────────────────────────────
SECTION_RESPONSES = {
    BTN_RECEPTION: {
        "text": ("//ـ ســيـسـتـم أريــس تــك ╎ *𝐀𝐑𝐈𝐒𝐄 𝐓𝐄𝐂𝐇*\n"
                 "• [𝐖𝐞𝐥𝐜𝐨𝐦𝐞   𝐆𝐚𝐭𝐞](https://songjinwoo1.github.io/Bot-Song-Jin-Woo/)"),
        "logo": "RECEPTION"
    },
    BTN_LOGIC: {
        "text": "*//ـ مُـخـتـبـر الـمـنـطـق ╎ 𝐋𝐎𝐆𝐈𝐂   𝐋𝐀𝐁*\n\n\"المنطق هو البوصلة هنا.\"",
        "logo": "LOGIC"
    },
    BTN_SEC: {
        "text": "*//ـ أمـن الـبـيـانـات ╎ 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘   𝐂𝐄𝐍𝐓𝐄𝐑*\n\nجميع البيانات مشفرة تحت إشراف النظام.",
        "logo": "SECURITY"
    },
    BTN_ARCHIVE: {
        "text": "*//ـ الأرشــيــف ╎ 𝐓𝐇𝐄   𝐀𝐑𝐂𝐇𝐈𝐕𝐄*\n\nهنا تُحفظ سجلات المنظمة.",
        "logo": "ARCHIVE"
    },
    BTN_CORE: {
        "text": "*//ـ نـواة الـتـطويـر ╎ 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐌𝐄𝐍𝐓   𝐂𝐎𝐑𝐄*\n\nمنطقة التطوير التقني والتجارب.",
        "logo": "CORE"
    },
    BTN_VISUAL: {
        "text": "*//ـ واجـهة الـنظام ╎ 𝐕𝐈𝐒𝐔𝐀𝐋   𝐀𝐑𝐂𝐀𝐍𝐄*\n\nالهوية البصرية للواجهات.",
        "logo": "VISUAL"
    },
    BTN_STRATEGY: {
        "text": "*//ـ غـرفـة الاسـتـشـارة*\n\n\"الهدوء هو قمة القوة.\"",
        "logo": "STRATEGY"
    },
    BTN_DEV: {
        "text": "*//ـ قـناة الاتـصال الـعـلـيا*\n\nتواصل مع القيادة العليا:",
        "logo": "COMMAND",
        "inline_buttons": [
            {"text": "𝑺𝒐𝒏𝒈 𝑱𝒊𝒏 𝑾𝒐𝒐", "url": "https://wa.me/96597805334"},
            {"text": "𝙺𝚒𝚢𝚘𝚝𝚊𝚔𝚊 𝙰𝚢𝚊𝚗𝚘𝚔𝚘𝚞𝚓𝚒", "url": "https://wa.me/201055719273"}
        ]
    }
}

# ─── محرك الإرسال السريع (مع تخزين file_id واستخدام الرابط كبديل) ───────────
def send_interface(chat_id: int, text: str, reply_markup=None, logo_key: str = "MAIN") -> None:
    """إرسال واجهة تحتوي على صورة ونص، مع تخزين معرف الصورة لتسريع الإرسال لاحقاً."""
    image = cached_file_ids.get(logo_key, SECTION_LOGOS.get(logo_key))
    try:
        sent = bot.send_photo(chat_id, image,
                              caption=text,
                              reply_markup=reply_markup,
                              parse_mode='Markdown')
        if logo_key not in cached_file_ids:
            cached_file_ids[logo_key] = sent.photo[-1].file_id
            logger.info(f"Cached file_id for {logo_key}")
    except Exception as e:
        logger.error(f"Failed to send photo for {logo_key}: {e}")
        # إرسال النص فقط في حال فشل الصورة
        bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode='Markdown')

# ─── أوامر المسؤول ───────────────────────────────────────────────────────────
@bot.message_handler(commands=['reload'])
def reload_cache(message):
    """إعادة تحميل ذاكرة التخزين المؤقت للصور (للمسؤولين فقط)"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ غير مصرح.")
        return
    cached_file_ids.clear()
    bot.reply_to(message, "✅ تم إعادة تحميل ذاكرة الصور.")

# ─── واجهة الترحيب الرئيسية ──────────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def welcome(message):
    """عرض لوحة المفاتيح الرئيسية عند بدء البوت"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [BTN_RECEPTION, BTN_LOGIC, BTN_SEC,
               BTN_ARCHIVE, BTN_CORE, BTN_VISUAL,
               BTN_STRATEGY, BTN_DEV]
    markup.add(*buttons)

    text = (f"*//ـ الـتـعـرف عـلى الـهـوية ╎ 𝐒𝐓𝐑𝐔𝐂𝐓𝐔𝐑𝐄   𝟎𝟏*\n\n"
            f"◈ الـمـستخـدم: `{message.from_user.first_name}`\n"
            "\"المنطق هو الحقيقة الوحيدة هنا.\"")
    send_interface(message.chat.id, text, markup, logo_key="MAIN")

# ─── معالجة الأزرار (ردود الأقسام) ──────────────────────────────────────────
@bot.message_handler(func=lambda message: message.text in SECTION_RESPONSES)
def handle_section(message):
    """معالجة الأزرار المعرفة في SECTION_RESPONSES"""
    cid = message.chat.id
    data = SECTION_RESPONSES[message.text]

    # تحضير الـ inline keyboard إذا وُجد
    markup = None
    if "inline_buttons" in data:
        markup = types.InlineKeyboardMarkup()
        for btn in data["inline_buttons"]:
            markup.add(types.InlineKeyboardButton(btn["text"], url=btn["url"]))

    send_interface(cid, data["text"], markup, logo_key=data.get("logo", "MAIN"))

# ─── معالجة النصوص غير المعروفة (اختياري) ────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def unknown(message):
    """رد على أي رسالة نصية غير معروفة"""
    bot.reply_to(message, "❓ الأمر غير معروف. استخدم القائمة الرئيسية.")

# ─── تشغيل البوت ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 STRUCTURE 01 IS ONLINE...")
    logger.info("Bot started")
    bot.infinity_polling(timeout=90)