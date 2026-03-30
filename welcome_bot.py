import os
import json
import logging
import threading
import random
from datetime import datetime
from typing import List

import telebot
from telebot import types
import google.generativeai as genai
from dotenv import load_dotenv

# -------------------- الإعدادات الأساسية --------------------
load_dotenv()

BOT_TOKEN = os.getenv("WELCOME_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise SystemExit("❌ ERROR: Missing WELCOME_BOT_TOKEN or GEMINI_API_KEY in .env")

ADMIN_IDS = [529456789, 201055719273]  # أضف معرفات المسؤولين هنا

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
AI_MODEL = genai.GenerativeModel("gemini-1.5-flash")
bot = telebot.TeleBot(BOT_TOKEN)

# -------------------- قاعدة البيانات (المجموعات المصرح بها) --------------------
DB_FILE = "authorized_chats.json"
AUTHORIZED_CHATS = set()  # استخدام set لمنع التكرار
db_lock = threading.Lock()

def load_db():
    global AUTHORIZED_CHATS
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                AUTHORIZED_CHATS = set(data)
    except Exception as e:
        logger.error(f"Failed to load DB: {e}")
        AUTHORIZED_CHATS = set()

def save_db():
    with db_lock:
        with open(DB_FILE, "w") as f:
            json.dump(list(AUTHORIZED_CHATS), f)

load_db()

# -------------------- الأصول والمنطق --------------------
LOGO_URL = "https://raw.githubusercontent.com/SongJinwoo1/Structure-01/main/IMG_4793.jpeg"

def generate_ai_welcome(name: str) -> str:
    prompts = [
        f"اكتب ترحيباً قصيراً جداً وبارداً بأسلوب أيانوكوجي لعضو اسمه {name} انضم لمنظمة Arise Tech.",
        f"اكتب ترحيباً مهيباً بأسلوب سونغ جين وو يرحب بظلال جديدة اسمها {name} في أريـس تيك."
    ]
    try:
        response = AI_MODEL.generate_content(random.choice(prompts))
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini error: {e}")
        return "المنطق هو الحقيقة الوحيدة. مرحباً بك في النظام."

def send_styled_welcome(chat_id: int, name: str, uid: int, username: str):
    ai_msg = generate_ai_welcome(name)
    now = datetime.now()
    caption = (
        f"⌯ **WELCOME TO ARISE SYSTEM** ⌯\n"
        f"━━━━━━━━━━━━━━\n"
        f"• `[STATUS: DECRYPTING...]` 🔓\n"
        f"• `{ai_msg}`\n\n"
        f"• الـهـويـة ⇐ `{name}`\n"
        f"• الـكـود ⇐ `{uid}`\n"
        f"• الـمـسـار ⇐ `{username}`\n\n"
        f"📅 تـاريـخ الانـضـمام ⇐ `{now.strftime('%Y/%m/%d')}`\n"
        f"⏰ الـسـاعـة ⇐ `{now.strftime('%I:%M %p')}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"« تـم تـحـلـيـل بـصـمـتـك الـرقـمـيـة بـنـجـاح. »"
    )
    try:
        bot.send_photo(chat_id, LOGO_URL, caption=caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Welcome send error: {e}")

# -------------------- المعالجات --------------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "🔰 **ARISE WELCOME AI V2**\nالـنظام جاهز لـتـأمين الـمجموعات.")

@bot.message_handler(commands=["Arise"])
def activate(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    chat_id = message.chat.id
    if chat_id not in AUTHORIZED_CHATS:
        AUTHORIZED_CHATS.add(chat_id)
        save_db()
        bot.reply_to(message, "✅ **تـم تـفعيل بـروتوكول الـترحيب الـذكي فـي هـذه الـمجموعة.**")
    else:
        bot.reply_to(message, "ℹ️ الـترحيب مُفعل مسبقاً في هذه المجموعة.")

@bot.message_handler(content_types=["new_chat_members"])
def on_join(message):
    if message.chat.id not in AUTHORIZED_CHATS:
        return
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        threading.Thread(
            target=send_styled_welcome,
            args=(
                message.chat.id,
                member.first_name,
                member.id,
                f"@{member.username}" if member.username else "Private"
            )
        ).start()

if __name__ == "__main__":
    print("🚀 ARISE WELCOME AI IS DEPLOYED")
    bot.infinity_polling()