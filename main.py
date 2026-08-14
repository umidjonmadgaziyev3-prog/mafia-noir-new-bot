import os
import json
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("data.json")

ITEMS = {
    "Qora qalqon": ("🛡", 700, "Himoya"),
    "Soxta hujjat": ("📜", 900, "Tekshiruvni chalg‘itadi"),
    "Afv tamg‘asi": ("⚖️", 1200, "Ovozdan qutqaradi"),
    "Qotil niqobi": ("🩸", 1500, "Hujumni yashiradi"),
    "Noir miltig‘i": ("🔫", 1800, "Maxsus hujum"),
    "Qora dori": ("💊", 1000, "Himoya beradi"),
    "Verbena ekstrakti": ("🧪", 1300, "Vampirga qarshi"),
    "Sirli niqob": ("🎭", 1600, "Rolni yashiradi"),
    "Geroydan himoya": ("🛡️", 2000, "Geroydan himoya"),
}

def load():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"users": {}, "games": {}}

DATA = load()

def save():
    DATA_FILE.write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def user_data(user):
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
            "items": {x: 0 for x in ITEMS},
        }
    DATA["users"][uid]["name"] = user.first_name or "O‘yinchi"
    return DATA["users"][uid]

def profile_text(u):
    games = u["games"]
    percent = round(u["wins"] / games * 100, 1) if games else 0

    text = (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {u['name']}\n"
        f"🆔 ID: {u['id']}\n\n"
        f"💵 Dollar: {u['money']}\n"
        f"💎 Olmos: {u['gems']}\n\n"
    )

    for name, (emoji, _, _) in ITEMS.items():
        text += f"{emoji} {name}: {u['items'].get(name, 0)}\n"

    text += (
        f"\n🎯 G‘alabalar: {u['wins']}\n"
        f"🎲 Barcha o‘yinlar: {games}\n"
        f"📊 G‘alaba foizi: {percent}%\n\n"
        f"🃏 Faol rol: {u['role'] or 'Yo‘q'}"
    )
    return text

def profile_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 Dollar olish", callback_data="money"),
            InlineKeyboardButton("💎 Olmos olish", callback_data="gems"),
        ],
        [
            InlineKeyboardButton("🦸 Mening Geroyim", callback_data="hero"),
            InlineKeyboardButton("🛒 Do‘kon", callback_data="shop"),
        ],
        [
            InlineKeyboardButton("🔽 Pastga", callback_data="down"),
            InlineKeyboardButton("📖 Buyumlar haqida", callback_data="info"),
        ],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data(update.effective_user)
    save()
    await update.message.reply_text(
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        "🌑 Sirlar yashirin.\n"
        "🎭 Rollar noma’lum.\n"
        "🔥 Ishonch esa xavfli.\n\n"
        "/game — O‘yinni boshlash\n"
        "/profile — Profil"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = user_data(update.effective_user)
    save()
    await update.message.reply_text(
        profile_text(u),
        reply_markup=profile_keyboard()
    )

async def roles(update: Update, context: Context
