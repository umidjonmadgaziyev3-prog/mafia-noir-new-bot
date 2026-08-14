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


# =========================
# DATA
# =========================

try:
    DATA = json.loads(FILE.read_text(encoding="utf-8"))
except Exception:
    DATA = {"users": {}, "games": {}}


def save():
    FILE.write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def user(u):
    uid = str(u.id)

    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "id": u.id,
            "name": u.first_name or "O‘yinchi",
            "money": 0,
            "gems": 0,
            "para": False,
            "wins": 0,
            "games": 0,
            "hero": None,
            "hero_xp": 0,
            "role": None,
            "items": {x: 0 for x in ITEMS},
        }
        save()

    return DATA["users"][uid]


# =========================
# MAIN BUTTONS
# =========================

def buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💵 Dollar olish",
                callback_data="money"
            ),
            InlineKeyboardButton(
                "💎 Olmos olish",
                callback_data="gems"
            ),
        ],
        [
            InlineKeyboardButton(
                "🦸 Mening Geroyim",
                callback_data="hero"
            ),
            InlineKeyboardButton(
                "🛒 Do‘kon",
                callback_data="shop"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔽 Pastga",
                callback_data="down"
            ),
            InlineKeyboardButton(
                "📖 Buyumlar haqida",
                callback_data="info"
            ),
        ],
    ])


# =========================
# PROFILE
# =========================

def profile(u):
    games = u.get("games", 0)
    wins = u.get("wins", 0)

    winrate = round(wins / games * 100, 1) if games else 0

    text = (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {u.get('name', 'O‘yinchi')}\n"
        f"🆔 ID: {u.get('id', '-')}\n\n"
        f"💵 Dollar: {u.get('money', 0)}\n"
        f"💎 Olmos: {u.get('gems', 0)}\n\n"
    )

    for name, item in ITEMS.items():
        count = u.get("items", {}).get(name, 0)
        text += f"{item[0]} {name}: {count}\n"

    hero = u.get("hero")

    if hero:
        hero_text = hero
    else:
        hero_text = "Mavjud emas"

    text += (
        f"\n🦸 Geroy: {hero_text}\n"
        f"⭐ Geroy XP: {u.get('hero_xp', 0)}\n\n"
        f"🎯 G‘alabalar: {wins}\n"
        f"🎲 Barcha o‘yinlar: {games}\n"
        f"📊 G‘alaba foizi: {winrate}%\n\n"
        f"🃏 Faol rol: {u.get('role') or 'Belgilanmagan'}"
    )

    return text


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = user(update.effective_user)

    await update.message.reply_text(
        profile(u),
        reply_markup=buttons()
    )


# =========================
# CALLBACKS
# =========================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    u = user(query.from_user)
    action = query.data

    if action == "money":
        u["money"] += 100
        save()

        await query.edit_message_text(
            "💵 Sizga 100 dollar berildi!\n\n"
            + profile(u),
            reply_markup=buttons()
        )

    elif action == "gems":
        u["gems"] += 1
        save()

        await query.edit_message_text(
            "💎 Sizga 1 ta olmos berildi!\n\n"
            + profile(u),
            reply_markup=buttons()
        )

    elif action == "hero":
        hero = u.get("hero")

        if hero:
            text = (
                "🦸 • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
                f"👤 Geroy: {hero}\n"
                f"⭐ XP: {u.get('hero_xp', 0)}"
            )
        else:
            text = (
                "🦸 • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
                "Sizda hozircha geroy yo‘q."
            )

        await query.edit_message_text(
            text,
            reply_markup=buttons()
        )

    elif action == "shop":
        text = "🛒 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"

        for name, (emoji, price) in ITEMS.items():
            text += (
                f"{emoji} {name} — 💵 {price}\n"
            )

        await query.edit_message_text(
            text,
            reply_markup=buttons()
        )

    elif action == "info":
        text = (
            "📖 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓 𝒉𝒂𝒒𝒊𝒅𝒂 •\n\n"
        )

        descriptions = {
            "Qora qalqon": "🛡️ Himoya buyumi.",
            "Soxta hujjat": "📜 Maxsus hujjat.",
            "Afv tamg‘asi": "⚖️ Afv olish uchun.",
            "Qotil niqobi": "🩸 Maxsus niqob.",
            "Noir miltig‘i": "🔫 Maxsus qurol.",
            "Qora dori": "💊 Maxsus dori.",
            "Verbena ekstrakti": "🧪 Maxsus ekstrakt.",
            "Sirli niqob": "🎭 Sirli buyum.",
            "Geroydan himoya": "🛡️ Geroydan himoya."
        }

        for name, (emoji, price) in ITEMS.items():
            text += (
                f"{emoji} {name}\n"
                f"💵 Narxi: {price}\n"
                f"{descriptions[name]}\n\n"
            )

        await query.edit_message_text(
            text,
            reply_markup=buttons()
        )

    elif action == "down":
        await query.edit_message_text(
            profile(u),
            reply_markup=buttons()
        )

    else:
        await query.edit_message_text(
            profile(u),
            reply_markup=buttons()
        )


# =========================
# ERROR HANDLER
# =========================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("BOT ERROR:", context.error)


# =========================
# RUN BOT
# =========================

def main():
    if not TOKEN:
