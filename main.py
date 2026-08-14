# main.py
import os
import json
import random
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN", "TOKENINGIZNI_BU_YERGA_QOYING")
DATA_FILE = Path("data.json")

MONEY_MIN_GIVE = 100
GEM_MIN_GIVE = 1
DOLLAR_TO_GEM = 700
STARS_PER_GEM = 10

ROLES = {
    "mafia": [
        ("Don", "🤵🏻"),
        ("Mafia", "🥷"),
        ("Qotil", "🔪"),
        ("Komissar", "🔎"),
        ("Daydi", "🏃"),
        ("Zaharchi", "☠️"),
        ("Advokat", "⚖️"),
        ("Manyak", "🗡️"),
    ],
    "aholi": [
        ("Doktor", "🩺"),
        ("Serjant", "👮"),
        ("Janob", "🎩"),
        ("Tinch axoli", "🧓"),
        ("Sherif", "⭐"),
        ("Qo‘riqchi", "🛡️"),
        ("O‘g‘ri", "🥷"),
        ("Qasoskor", "⚔️"),
        ("Sehrgar", "🪄"),
        ("Jurnalist", "📰"),
        ("Kimyogar", "🧪"),
        ("Himoyachi", "🛡️"),
        ("Jodugar", "🔮"),
    ],
    "yakka": [
        ("Joker", "🃏"),
        ("Vampir", "🧛"),
        ("Ovchi", "🏹"),
        ("Yollanma qotil", "🎯"),
    ],
}

ITEMS = {
    "Qora qalqon": ("🛡", 700, "Bir marta hujumdan himoya qiladi."),
    "Soxta hujjat": ("📜", 900, "Tekshiruvni bir marta chalg‘itadi."),
    "Afv tamg‘asi": ("⚖️", 1200, "Ovoz berishdan bir marta qutqaradi."),
    "Qotil niqobi": ("🩸", 1500, "Hujumni yashirin bajarishga yordam beradi."),
    "Noir miltig‘i": ("🔫", 1800, "Maxsus hujum buyumi."),
    "Qora dori": ("💊", 1000, "Bir marta qo‘shimcha himoya beradi."),
    "Verbena ekstrakti": ("🧪", 1300, "Vampirga qarshi maxsus vosita."),
    "Sirli niqob": ("🎭", 1600, "Rolni yashirishga yordam beradi."),
    "Geroydan himoya": ("🛡️", 2000, "Geroy qobiliyatidan himoya qiladi."),
}

HERO_LEVELS = {
    1: (0, "Oddiy qobiliyat"),
    2: (100, "Kuchaytirilgan qobiliyat"),
    3: (250, "Ikkinchi maxsus qobiliyat"),
    4: (500, "Kuchli himoya"),
    5: (1000, "Maxsus Geroy kuchi"),
}


def load_data():
    if not DATA_FILE.exists():
        return {"users": {}, "games": {}}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"users": {}, "games": {}}


DATA = load_data()


def save_data():
    DATA_FILE.write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2),
        encoding="utf-8",
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
            "items": {name: 0 for name in ITEMS},
            "role": None,
            "active": False,
        }

    DATA["users"][uid]["name"] = user.first_name or "O‘yinchi"
    return DATA["users"][uid]


def win_percent(user):
    if user["games"] == 0:
        return 0
    return round(user["wins"] / user["games"] * 100, 1)


def profile_text(user):
    lines = [
        "🕴
