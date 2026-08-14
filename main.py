import os
import json
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

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

try:
    DATA = json.loads(FILE.read_text(encoding="utf-8"))
except Exception:
    DATA = {"users": {}, "games": {}}


def save():
    FILE.write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def user(tg_user):
    uid = str(tg_user.id)

    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "id": tg_user.id,
            "name": tg_user.first_name or "O‘yinchi",
            "money": 1000,
            "gems": 10,
            "para": False,
            "wins": 0,
            "games": 0,
            "hero": None,
            "hero_xp": 0,
            "role": None,
            "items": {name: 0 for name in ITEMS},
        }
        save()

    # Eski foydal
