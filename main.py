import os
import json
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
FILE = Path("data.json")

ITEMS = {
    "Qora qalqon": ("🛡️", 700),
    "Soxta hujjat": ("📜", 900),
    "Afv tamg‘asi": ("⚖️", 1200),
    "Qotil niqobi": ("🩸", 1500),
    "Noir miltig‘i": ("🔫", 1800),
    "Qora dori": ("💊", 1000),
    "Verbena ekstrakti": ("🧪", 1300),
    "Sirli niqob": ("🎭", 1600),
    "Geroydan himoya": ("🛡️", 2000),
}

def load():
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"users": {}, "games": {}}

DATA = load()

def save():
    FILE.write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def get_user(user):
    uid = str(user.id)

    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "id": user.id,
            "name": user.first_name or "O‘yinchi",
            "money": 0,
            "gems": 0,
            "para": False,
            "wins": 0,
            "games": 0,
            "hero": None,
            "hero_xp": 0,
            "role": None,
            "items": {x: 0 for x in ITEMS}
        }

    DATA["users"][uid]["name"] = user.first_name or "O‘yinchi"
    return DATA["users"][uid]

def keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 Dollar olish", callback_data="money"),
            InlineKeyboardButton("💎 Olmos olish", callback_data="gems")
        ],
        [
            InlineKeyboardButton("🦸 Mening Geroyim", callback_data="hero"),
            InlineKeyboardButton("🛒 Do‘kon", callback_data="shop")
        ],
        [
            InlineKeyboardButton("🔽 Pastga", callback_data="down"),
            InlineKeyboardButton("📖 Buyumlar haqida", callback_data="info")
        ]
    ])

def profile_text(u):
    percent = round(u["wins"] / u["games"] * 100, 1) if u["games"] else 0

    text = (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {u['name']}\n"
        f"🆔 ID: {u['id']}\n\n"
        f"💵 Dollar: {u['money']}\n"
        f"💎 Olmos: {u['gems']}\n\n"
    )

    for name, (emoji, _) in ITEMS.items():
