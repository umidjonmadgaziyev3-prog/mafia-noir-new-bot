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
DATA_FILE = Path("data.json")

OWNER_ID = 8402159260
OWNER_USERNAME = "Umarov_uuu"


# =========================
# MAHSULOTLAR
# =========================

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


# =========================
# HERO
# =========================

XP_REQUIREMENTS = {
    1: 150,
    2: 300,
    3: 700,
    4: 1300,
}

XP_PER_WIN = 10

HERO_RANKS = {
    1: "🥉 Bronze",
    2: "🥈 Silver",
    3: "🥇 Gold",
    4: "💠 Platinum",
    5: "💎 Diamond",
}

HERO_ABILITIES = {
    1: "⚔️ Hujum",
    2: "🛡️ Himoya",
    3: "🦾 Zirh",
    4: "⚡ Maxsus qobiliyat",
    5: "👑 Ultimate",
}


def get_hero_level(xp):
    if xp < XP_REQUIREMENTS[1]:
        return 1

    if xp < XP_REQUIREMENTS[2]:
        return 2

    if xp < XP_REQUIREMENTS[3]:
        return 3

    if xp < XP_REQUIREMENTS[4]:
        return 4

    return 5


def get_hero_rank(level):
    return HERO_RANKS.get(level, "🥉 Bronze")


def get_next_xp(level):
    if level >= 5:
        return None

    return XP_REQUIREMENTS[level]


def get_win_percent(wins, games):
    if games <= 0:
        return 0

    return round((wins / games) * 100, 1)


def get_hero_profile_text(user_data):
    if user_data["hero"] <= 0:
        return (
            "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
            "❌ Sizda Geroy yo‘q.\n\n"
            "Geroyni Do‘kondan olishingiz mumkin."
        )

    xp = user_data["hero_xp"]
    level = get_hero_level(xp)
    rank = get_hero_rank(level)

    next_xp = get_next_xp(level)

    if next_xp is None:
        xp_line = f"⭐ XP: {xp} / MAX"
    else:
        xp_line = f"⭐ XP: {xp} / {next_xp}"

    abilities = []

    for ability_level in range(1, 6):
        ability_name = HERO_ABILITIES[ability_level]

        if level >= ability_level:
            status = "✅"
        else:
            status = "🔒"

        abilities.append(
            f"{status} {ability_name}"
        )

    return (
        "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
        f"🏅 Rank: {rank}\n"
        f"📊 Daraja: {level} / 5\n"
        f"{xp_line}\n"
        f"🏆 G‘alabalar: {user_data['hero_wins']}\n"
        f"🎲 Barcha o‘yinlar: {user_data['hero_games']}\n\n"
        "⚔️ • Qobiliyatlar •\n\n"
        + "\n".join(abilities)
    )


def get_hero_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔙 Orqaga",
                callback_data="profile"
            )
        ]
    ])


# =========================
# DATA
# =========================

def load_data():
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def get_user_data(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "d
