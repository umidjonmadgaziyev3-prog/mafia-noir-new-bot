import os
import json
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("data.json")

OWNER_ID = 8402159260
OWNER_USERNAME = "Umarov_uuu"


# =========================================================
# MAHSULOTLAR
# =========================================================

ITEMS = {
    "shield": ("🛡 Qora qalqon", 200, "dollar"),
    "document": ("📜 Soxta hujjat", 1, "diamond"),
    "forgiveness": ("⚖️ Afv tamg‘asi", 150, "dollar"),
    "killer_mask": ("🩸 Qotil niqobi", 150, "dollar"),
    "gun": ("🔫 Noir miltig‘i", 1, "diamond"),
    "black_medicine": ("💊 Qora dori", 250, "dollar"),
    "verbena": ("🧪 Verbena ekstrakti", 300, "dollar"),
    "mystery_mask": ("🥷 Sirli niqob", 2, "diamond"),
    "hero_protection": ("🛡️ Geroydan himoya", 6, "diamond"),
    "hero": ("⚔️ Geroy", 90, "diamond"),
    "active_role": ("🃏 Faol rol", 3, "diamond"),
}


# =========================================================
# DATA
# =========================================================

def load_data():
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_default_user(user_id):
    return {
        "dollar": 0,
        "diamond": 0,
        "vip": user_id == OWNER_ID,

        "hero": 0,
        "hero_xp": 0,
        "hero_wins": 0,

        "active_role": 0,

        "items": {
            key: 0
            for key in ITEMS
            if key not in ("hero", "active_role")
        },

        "active_items": {
            key: False
            for key in ITEMS
            if key not in ("hero", "active_role")
        },
    }


def get_user_data(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = get_default_user(user_id)

    user = data[uid]

    user.setdefault("dollar", 0)
    user.setdefault("diamond", 0)
    user["vip"] = user_id == OWNER_ID

    user.setdefault("hero", 0)
    user.setdefault("hero_xp", 0)
    user.setdefault("hero_wins", 0)

    user.setdefault("active_role", 0)
    user.setdefault("items", {})
    user.setdefault("active_items", {})

    for key in ITEMS:
        if key not in ("hero", "active_role"):
            user["items"].setdefault(key, 0)
            user["active_items"].setdefault(key, False)

    save_data(data)

    return data, user


# =========================================================
# START
# =========================================================

def get_language_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kk")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ])


def get_main_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Owner 🎩",
                url="https://t.me/Umarov_uuu"
            )
        ],
        [
            InlineKeyboardButton(
                "Asosiy guruh 👥",
                url="https://t.me/+0eXijyVhioY4ZDMy"
            )
        ],
        [
            InlineKeyboardButton(
                "Guruhga qo‘shish ➕",
                url="https://t.me/Noiruzbot?startgroup=true"
            )
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Tilni tanlang
