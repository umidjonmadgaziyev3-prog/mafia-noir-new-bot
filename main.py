import os
import json
import random
import asyncio
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    BotCommandScopeAllGroupChats,
)
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
BOT_USERNAME = "Noiruzbot"

# ======================= O'YINLAR =======================

ACTIVE_GAMES = {}

NIGHT_DURATION = 60
VOTING_DURATION = 45
DAY_DURATION = 50
JUDGEMENT_DURATION = 30


def get_game_key(chat_id, message_id):
    return f"{chat_id}_{message_id}"


def get_game_text(players):
    if not players:
        return "O‘yin ro‘yxatdan o‘tishi boshlandi."

    lines = []
    for i in range(0, len(players), 4):
        row = players[i:i + 4]
        lines.append("   ".join(row))

    return "\n".join(lines)


def get_join_button(chat_id, message_id):
    game_key = get_game_key(chat_id, message_id)

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Ro‘yxatdan o‘tish",
                url=f"https://t.me/{BOT_USERNAME}?start=join_{game_key}",
            )
        ]
    ])


# ======================= BUYUMLAR =======================

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


# ======================= DATA =======================

def load_data():
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return {}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get_default_user(user_id):
    return {
        "dollar": 0,
        "diamond": 0,
        "vip": user_id == OWNER_ID,
        "hero": 0,
        "hero_xp": 0,
        "hero_wins": 0,
        "active_role": 0,
        "games": 0,
        "wins": 0,
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

    if uid not in data or not isinstance(data[uid], dict):
        data[uid] = get_default_user(user_id)

    user = data[uid]

    user.setdefault("dollar", 0)
    user.setdefault("diamond", 0)
    user["vip"] = user_id == OWNER_ID
    user.setdefault("hero", 0)
    user.setdefault("hero_xp", 0)
    user.setdefault("hero_wins", 0)
    user.setdefault("active_role", 0)
    user.setdefault("games", 0)
    user.setdefault("wins", 0)

    if not isinstance(user.get("items"), dict):
        user["items"] = {}

    if not isinstance(user.get("active_items"), dict):
        user["active_items"] = {}

    for key in ITEMS:
        if key in ("hero", "active_role"):
            continue

        user["items"].setdefault(key, 0)
        user["active_items"].setdefault(key, False)

    data[uid] = user
    save_data(data)

    return data, user


# ======================= START =======================

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
                url=f"https://t.me/{OWNER_USERNAME}",
            )
        ],
        [
            InlineKeyboardButton(
                "Asosiy guruh 👥",
                url="https://t.me/+0eXijyVhioY4ZDMy",
            )
        ],
        [
            InlineKeyboardButton(
                "Guruhga qo‘shish ➕",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
            )
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if context.args and context.args[0].startswith("join_"):
        await register_game_player(update, context)
        return

    await update.message.reply_text(
        "🌍 Tilni tanlang:",
        reply_markup=get_language_buttons(),
    )


async def language_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    await query.message.edit_text(
        "🖤 Salom! Xush kelibsiz!\n\n"
        "🌃 Men Mafia Noir botiman. "
        "Mafia o‘ynash uchun meni guruhingizga qo‘shing.",
        reply_markup=get_main_buttons(),
    )


# ======================= PROFILE =======================

def get_profile_text(user):
    _, data = get_user_data(user.id)

    vip_line = "\n👑 VIP: Ha" if data["vip"] else ""

    games = data.get("games", 0)
    wins = data.get("wins", 0)

    if games > 0:
        percent = int((wins / games) * 100)
    else:
        percent = 0

    return (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {user.first_name or 'Noma’lum'}\n"
        f"🆔 ID: {user.id}"
        f"{vip_line}\n\n"
        f"💵 Dollar: {data['dollar']}\n"
        f"💎 Olmos: {data['diamond']}\n\n"
        f"🛡 Qora qalqon: {data['items']['shield']}\n"
        f"📜 Soxta hujjat: {data['items']['document']}\n"
        f"⚖️ Afv tamg‘asi: {data['items']['forgiveness']}\n"
        f"🩸 Qotil niqobi: {data['items']['killer_mask']}\n"
        f"🔫 Noir miltig‘i: {data['items']['gun']}\n"
        f"💊 Qora dori: {data['items']['black_medicine']}\n"
        f"🧪 Verbena ekstrakti: {data['items']['verbena']}\n"
        f"🥷 Sirli niqob: {data['items']['mystery_mask']}\n"
        f"🛡️ Geroydan himoya: {data['items']['hero_protection']}\n\n"
        f"⚔️ Geroy: {'Bor' if data['hero'] > 0 else 'Yo‘q'}\n"
        f"🃏 Faol rol: "
        f"{'Bor' if data['active_role'] > 0 else 'Yo‘q'}\n\n"
        f"🎯 G‘alabalar: {wins}\n"
        f"🎲 Barcha o‘yinlar: {games}\n"
        f"📊 G‘alaba foizi: {percent}%"
    )


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar_exchange")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="diamond_buy")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items_info")],
        [InlineKeyboardButton("🔻", callback_data="item_control")],
    ])


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        get_profile_text(update.effective_user),
        reply_markup=get_profile_buttons(),
    )


# ======================= DOLLAR =======================

DOLLAR_PACKAGES = [
    (1, 600),
    (2, 1200),
    (3, 1800),
    (5, 3000),
    (10, 6000),
    (20, 12000),
]


def get_dollar_buttons():
    keyboard = []

    for diamonds, dollars in DOLLAR_PACKAGES:
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {diamonds} → 💵 {dollars}",
                callback_data=f"exchange_{diamonds}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    return InlineKeyboardMarkup(keyboard)


async def dollar_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    await query.message.edit_text(
        "💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Olmosni Dollarga almashtiring:",
        reply_markup=get_dollar_buttons(),
    )


async def exchange_dollar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        amount = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        await query.answer("❌ Xatolik", show_alert=True)
        return

    data, user = get_user_data(query.from_user.id)

    if query.from_user.id != OWNER_ID:
        if user["diamond"] < amount:
            await query.answer("❌ Olmos yetarli emas", show_alert=True)
            return

        user["diamond"] -= amount

    user["dollar"] += amount * 600

    save_data(data)

    await query.answer("✅ Savdo muvaffaqiyatli amalga oshirildi!")

    await query.message.edit_text(
        get_profile_text(query.from_user),
        reply_markup=get_profile_buttons(),
    )


# ======================= OLMOS =======================

DIAMOND_PACKAGES = [
    (5, 4000),
    (10, 8000),
    (25, 20000),
    (50, 40000),
    (100, 80000),
    (250, 200000),
]


def get_diamond_buttons():
    keyboard = []

    for amount, price in DIAMOND_PACKAGES:
        price_text = f"{price:,}".replace(",", " ")

        keyboard.append([
            InlineKeyboardButton(
                f"💎 {amount} ta — {price_text} so‘m",
                url=f"https://t.me/{OWNER_USERNAME}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    return InlineKeyboardMarkup(keyboard)


async def diamond_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    await query.message.edit_text(
        "💎 • 𝑶𝒍𝒎𝒐𝒔 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Kerakli paketni tanlang:",
        reply_markup=get_diamond_buttons(),
    )


# ======================= SHOP =======================

def get_shop_buttons():
    keyboard = []

    for key, (name, price, currency) in ITEMS.items():
        emoji = "💵" if currency == "dollar" else "💎"

        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {emoji} {price}",
                callback_data=f"buy_{key}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    return InlineKeyboardMarkup(keyboard)


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "Kerakli buyumni tanlang:",
        reply_markup=get_shop_buttons(),
    )


async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    key = query.data.replace("buy_", "", 1)

    if key not in ITEMS:
        await query.answer("❌ Xatolik", show_alert=True)
        return

    name, price, currency = ITEMS[key]

    data, user = get_user_data(query.from_user.id)

    if query.from_user.id != OWNER_ID:
        if user[currency] < price:
            await query.answer("❌ Mablag‘ yetarli emas", show_alert=True)
            return

        user[currency] -= price

    if key == "hero":
        user["hero"] += 1
    elif key == "active_role":
        user["active_role"] += 1
    else:
        user["items"][key] += 1

    save_data(data)

    await query.answer("✅ Xarid muvaffaqiyatli amalga oshirildi!")

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "✅ Xarid muvaffaqiyatli amalga oshirildi.\n\n"
        "Yana buyum tanlang:",
        reply_markup=get_shop_buttons(),
    )


# ======================= BUYUMLAR HAQIDA =======================

DESCRIPTIONS = {
    "shield": "bir marta hujumdan himoya qiladi.",
    "document": "tekshiruvda rolni yashirishga yordam beradi.",
    "forgiveness": "bir marta jazodan qutqaradi.",
    "killer_mask": "qotilni aniqlashni qiyinlashtiradi.",
    "gun": "bir marta hujum qilish imkonini beradi.",
    "black_medicine": "salbiy ta’sirni olib tashlaydi.",
    "verbena": "vampirdan himoya qiladi.",
    "mystery_mask": "rolni vaqtincha yashiradi.",
    "hero_protection": "geroy hujumidan bir marta himoya qiladi.",
    "hero": "sotib olingandan keyin sizga Geroy beriladi.",
    "active_role": "1 ta o‘yin uchun tasodifiy faol rol beradi.",
}


async def items_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    text = "📖 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓 𝒉𝒂𝒒𝒊𝒅𝒂 •\n\n"

    for key, (name, _, _) in ITEMS.items():
        text += f"{name} — {DESCRIPTIONS[key]}\n"

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Orqaga", callback_data="profile")]
        ]),
    )


# ======================= ITEM CONTROL =======================

def get_control_buttons(user):
    keyboard = []

    for key, (name, _, _) in ITEMS.items():
        if key in ("hero", "active_role"):
            continue

        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {user['items'][key]}",
                callback_data=f"noop_{key}",
            )
        ])

        status = "🟢 ON" if user["active_items"][key] else "⚪ OFF"

        keyboard.append([
            InlineKeyboardButton(
                status,
                callback_data=f"toggle_{key}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    return InlineKeyboardMarkup(keyboard)


async def item_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    _, user = get_user_data(query.from_user.id)

    await query.message.edit_text(
        "🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\n"
        "Buyumni ON yoki OFF holatiga o‘tkazing.",
        reply_markup=get_control_buttons(user),
    )


async def toggle_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    key = query.data.replace("toggle_", "", 1)

    if key not in ITEMS:
        await query.answer("❌ Xatolik", show_alert=True)
        return

    data, user = get_user_data(query.from_user.id)

    if key not in user["items"]:
        await query.answer("❌ Xatolik", show_alert=True)
        return

    if user["items"][key] <= 0:
        await query.answer(
            "❌ Bu buyum sizda mavjud emas",
            show_alert=True,
        )
        return

    user["active_items"][key] = not user["active_items"][key]

    save_data(data)

    await query.answer()

    await query.message.edit_text(
        "🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\n"
        "Buyumni ON yoki OFF holatiga o‘tkazing.",
        reply_markup=get_control_buttons(user),
    )


# ======================= HERO =======================

HERO_LEVELS = [
    ("🥉 I — Bronze", 0, "⚔️ Hujum"),
    ("🥈 II — Silver", 100, "🛡️ Himoya"),
    ("🥇 III — Gold", 300, "🪖 Zirh"),
    ("💎 IV — Diamond", 700, "⚡ Maxsus qobiliyat"),
    ("🖤 V — Noir", 1500, "👑 Maxsus kuch"),
]


def get_hero_level(xp):
    level = 1

    for index, (_, needed_xp, _) in enumerate(HERO_LEVELS):
        if xp >= needed_xp:
            level = index + 1

    return level


def get_hero_progress(xp):
    level = get_hero_level(xp)
    current = HERO_LEVELS[level - 1]

    if level >= 5:
        next_xp = None
    else:
        next_xp = HERO_LEVELS[level][1]

    return current[0], current[1], current[2], next_xp


def get_hero_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Darajalar", callback_data="hero_levels")],
        [InlineKeyboardButton("⚡ Qobiliyatlar", callback_data="hero_skills")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="profile")],
    ])


async def hero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.message.edit_text(
            "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
            "❌ Sizda Geroy mavjud emas.\n\n"
            "💎 Do‘kondan Geroy sotib olishingiz mumkin.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Do‘konga", callback_data="shop")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="profile")],
            ]),
        )
        return

    xp = user.get("hero_xp", 0)
    wins = user.get("hero_wins", 0)

    level = get_hero_level(xp)
    name, _, power, next_xp = get_hero_progress(xp)

    if next_xp is None:
        xp_line = f"⭐ XP: {xp} — MAX"
        next_line = "👑 Maksimal daraja ochilgan"
    else:
        xp_line = f"⭐ XP: {xp} / {next_xp}"
        next_line = f"📈 Keyingi daraja: {next_xp} XP"

    shield = (
        "🛡️ Himoya: Faol"
        if level >= 2
        else "🛡️ Himoya: Hali ochilmagan"
    )

    text = (
        "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
        f"👤 Egasi: {query.from_user.first_name or 'Noma’lum'}\n\n"
        f"⚔️ Geroylar: {user['hero']} ta\n"
        f"🏆 Daraja: {name}\n"
        f"{xp_line}\n\n"
        f"🎯 G‘alabalar: {wins}\n"
        f"{shield}\n"
        f"⚡ Qobiliyat: {power}\n\n"
        f"{next_line}\n\n"
        "━━━━━━━━━━━━━━\n"
        "🥉 I — Bronze\n"
        "🥈 II — Silver\n"
        "🥇 III — Gold\n"
        "💎 IV — Diamond\n"
        "🖤 V — Noir"
    )

    await query.message.edit_text(
        text,
        reply_markup=get_hero_buttons(),
    )


async def hero_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.answer("❌ Sizda Geroy yo‘q", show_alert=True)
        return

    current_level = get_hero_level(user.get("hero_xp", 0))

    text = (
        "🏆 • 𝑮𝒆𝒓𝒐𝒚 𝑫𝒂𝒓𝒂𝒋𝒂𝒍𝒂𝒓𝒊 •\n\n"
        "🥉 I — Bronze\n"
        "⚔️ Hujum\n"
        "🔓 0 XP\n\n"
        "🥈 II — Silver\n"
        "🛡️ Himoya\n"
        "🔓 100 XP\n\n"
        "🥇 III — Gold\n"
        "🪖 Zirh\n"
        "🔓 300 XP\n\n"
        "💎 IV — Diamond\n"
        "⚡ Maxsus qobiliyat\n"
        "🔓 700 XP\n\n"
        "🖤 V — Noir\n"
        "👑 Maxsus kuch\n"
        "🔓 1500 XP\n\n"
        f"📍 Hozirgi daraja: {current_level}/5"
    )

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Geroy profiliga", callback_data="hero")]
        ]),
    )


async def hero_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.answer("❌ Sizda Geroy yo‘q", show_alert=True)
        return

    level = get_hero_level(user.get("hero_xp", 0))
    skills = [item[2] for item in HERO_LEVELS[:level]]

    text = (
        "⚡ • 𝑮𝒆𝒓𝒐𝒚 𝑸𝒐𝒃𝒊𝒍𝒊𝒚𝒂𝒕𝒍𝒂𝒓𝒊 •\n\n"
        f"🏆 Daraja: {level}/5\n\n"
        + "\n".join(skills)
    )

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Geroy profiliga", callback_data="hero")]
        ]),
    )


# ======================= 25 TA ROL =======================

ROLES = [
    ("🎩 Don", "don"),
    ("🥷 Mafia", "mafia"),
    ("🎭 Aferist", "aferist"),
    ("🔪 Qotil", "qotil"),
    ("👮 Komissar", "komissar"),
    ("👨‍⚕️ Doktor", "doktor"),
    ("👮‍♂️ Serjant", "serjant"),
    ("🎖️ Kapitan", "kapitan"),
    ("👤 Fuqaro", "fuqaro"),
    ("👣 Daydi", "daydi"),
    ("⚖️ Sudya", "sudya"),
    ("👨‍⚖️ Advokat", "advokat"),
    ("💀 Qasoskor", "qasoskor"),
    ("🦎 Buqalamun", "buqalamun"),
    ("🕵️ Kuzatuvchi", "kuzatuvchi"),
    ("🛡️ Bodyguard", "bodyguard"),
    ("🧙 Sehrgar", "sehrgar"),
    ("📰 Jurnalist", "jurnalist"),
    ("🔬 Kimyogar", "kimyogar"),
    ("💣 Minyor", "minyor"),
    ("⚡ Koldun", "koldun"),
    ("🕶️ Maxfiy agent", "agent"),
    ("👻 Arvoh", "arvoh"),
    ("🤡 Joker", "joker"),
    ("🧛 Vampir", "vampir"),
]


# ======================= ROL XABARLARI =======================

ROLE_MESSAGES = {
    "don": (
        "🎩 • DON •\n\n"
        "Siz Don bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz mafiyaning boshlig‘isiz.\n"
        "Bugun kimni yo‘q qilmoqchisiz?"
    ),
    "mafia": (
        "🥷 • MAFIA •\n\n"
        "Siz Mafia bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Sizning vazifangiz — tinchliksevarlarni yo‘q qilish."
    ),
    "aferist": (
        "🎭 • AFERIST •\n\n"
        "Siz Aferist bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Aldov va hiyla orqali o‘yinda omon qoling."
    ),
    "qotil": (
        "🔪 • QOTIL •\n\n"
        "Siz Qotil bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Bugun kimni o‘ldirmoqchisiz?"
    ),
    "komissar": (
        "👮 • KOMISSAR •\n\n"
        "Siz Komissar bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Avval harakatni tanlaysiz:\n\n"
        "🔎 Tekshirish\n"
        "🔫 O‘ldirish"
    ),
    "doktor": (
        "👨‍⚕️ • DOKTOR •\n\n"
        "Siz Doktor bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz kimnidir davolashingiz mumkin."
    ),
    "serjant": (
        "👮‍♂️ • SERJANT •\n\n"
        "Siz Serjant bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Hozircha hech qanday harakat qilishingiz shart emas."
    ),
    "kapitan": (
        "🎖️ • KAPITAN •\n\n"
        "Siz Kapitan bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Maxsus qobiliyatingiz keyingi bosqichlarda ishlatiladi."
    ),
    "fuqaro": (
        "👤 • FUQARO •\n\n"
        "Siz Fuqaro bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Hozircha hech qanday qobiliyatingiz yo‘q.\n"
        "Omon qoling va ertalab ovoz berishda qatnashing."
    ),
    "daydi": (
        "👣 • DAYDI •\n\n"
        "Siz Daydi bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz mustaqil o‘ynaysiz."
    ),
    "sudya": (
        "⚖️ • SUDYA •\n\n"
        "Siz Sudya bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Sizning asosiy kuchingiz ovoz berishda ishlaydi."
    ),
    "advokat": (
        "👨‍⚖️ • ADVOKAT •\n\n"
        "Siz Advokat bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz tanlagan o‘yinchini himoya qilishingiz mumkin."
    ),
    "qasoskor": (
        "💀 • QASOSKOR •\n\n"
        "Siz Qasoskor bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Sizning maxsus qobiliyatingiz keyinchalik ishlatiladi."
    ),
    "buqalamun": (
        "🦎 • BUQALAMUN •\n\n"
        "Siz Buqalamun bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Sizning kuchingiz rolni yashirishga bog‘liq."
    ),
    "kuzatuvchi": (
        "🕵️ • KUZATUVCHI •\n\n"
        "Siz Kuzatuvchi bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz o‘yinchilar harakatini kuzatasiz."
    ),
    "bodyguard": (
        "🛡️ • BODYGUARD •\n\n"
        "Siz Bodyguard bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz kimnidir himoya qilishingiz mumkin."
    ),
    "sehrgar": (
        "🧙 • SEHRGAR •\n\n"
        "Siz Sehrgar bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Sizning maxsus qobiliyatingiz keyinchalik ishlatiladi."
    ),
    "jurnalist": (
        "📰 • JURNALIST •\n\n"
        "Siz Jurnalist bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz ma’lumot yig‘ishingiz mumkin."
    ),
    "kimyogar": (
        "🔬 • KIMYOGAR •\n\n"
        "Siz Kimyogar bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz maxsus moddalar bilan ishlaysiz."
    ),
    "minyor": (
        "💣 • MINYOR •\n\n"
        "Siz Minyor bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz tuzoqdan foydalanishingiz mumkin."
    ),
    "koldun": (
        "⚡ • KOLDUN •\n\n"
        "Siz Koldun bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz sirli kuchlardan foydalanasiz."
    ),
    "agent": (
        "🕶️ • MAXFIY AGENT •\n\n"
        "Siz Maxfiy agent bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz yashirin topshiriqlarni bajarasiz."
    ),
    "arvoh": (
        "👻 • ARVOH •\n\n"
        "Siz Arvoh bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Sizning maxsus kuchingiz o‘yindan chiqqaningizdan keyin ishlaydi."
    ),
    "joker": (
        "🤡 • JOKER •\n\n"
        "Siz Joker bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Maqsadingiz o‘yinni chalkashtirish."
    ),
    "vampir": (
        "🧛 • VAMPIR •\n\n"
        "Siz Vampir bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.\n"
        "Siz tunda harakat qilasiz."
    ),
}


def get_role_keyboard(role, players):
    if role == "komissar":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔎 Tekshirish",
                    callback_data="night_check",
                ),
                InlineKeyboardButton(
                    "🔫 O‘ldirish",
                    callback_data="night_kill",
                ),
            ]
        ])

    if role == "doktor":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "❤️ Davolash",
                    callback_data="night_heal",
                )
            ]
        ])

    if role == "don":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔪 O‘ldirish",
                    callback_data="night_don_kill",
                )
            ]
        ])

    if role == "qotil":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔪 O‘ldirish",
                    callback_data="night_killer",
                )
            ]
        ])

    if role == "bodyguard":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🛡️ Himoya",
                    callback_data="night_guard",
                )
            ]
        ])

    return None


async def send_role_to_player(
    context,
    player_id,
    player_name,
    role_name,
    role_key,
    players,
):
    text = ROLE_MESSAGES.get(
        role_key,
        f"🎭 Siz {role_name} bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    )

    keyboard = get_role_keyboard(role_key, players)

    try:
        await context.bot.send_message(
            chat_id=int(player_id),
            text=text,
            reply_markup=keyboard,
        )
        return True
    except Exception:
        return False


# ======================= ROLES KOMANDASI =======================

def get_roles_buttons():
    keyboard = []

    for index in range(0, len(ROLES), 2):
        row = [
            InlineKeyboardButton(
                ROLES[index][0],
                callback_data=f"role_{ROLES[index][1]}",
            )
        ]

        if index + 1 < len(ROLES):
            row.append(
                InlineKeyboardButton(
                    ROLES[index + 1][0],
                    callback_data=f"role_{ROLES[index + 1][1]}",
                )
            )

        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
        "Kerakli rolni tanlang:",
        reply_markup=get_roles_buttons(),
    )


async def role_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    role_key = query.data.replace("role_", "", 1)

    description = {
        key: (
            f"{name}\n\n"
            "🎭 Bu rol Mafia Noir o‘yinidagi maxsus rol."
        )
        for name, key in ROLES
    }

    await query.answer(
        description.get(
            role_key,
            "❌ Bu rol haqida ma’lumot topilmadi.",
        ),
        show_alert=True,
    )


# ======================= O'YIN RO'YXATDAN O'TISH =======================

async def gamecreate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.effective_chat.type not in ("group", "supergroup"):
        return

    message = await update.message.reply_text(
        "O‘yin ro‘yxatdan o‘tishi boshlandi."
    )

    game_key = get_game_key(
        update.effective_chat.id,
        message.message_id,
    )

    ACTIVE_GAMES[game_key] = {
        "chat_id": update.effective_chat.id,
        "message_id": message.message_id,
        "players": {},
        "started": False,
        "phase": "registration",
        "night_actions": {},
    }

    await message.edit_text(
        "O‘yin ro‘yxatdan o‘tishi boshlandi.",
        reply_markup=get_join_button(
            update.effective_chat.id,
            message.message_id,
        ),
    )


async def register_game_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text("🖤 Salom! Xush kelibsiz!")
        return

    payload = context.args[0]

    if not payload.startswith("join_"):
        await update.message.reply_text("🖤 Salom! Xush kelibsiz!")
        return

    game_key = payload[5:]
    game = ACTIVE_GAMES.get(game_key)

    if not game:
        await update.message.reply_text(
            "❌ Bu o‘yin ro‘yxatdan o‘tishi yopilgan yoki mavjud emas."
        )
        return

    if game.get("started"):
        await update.message.reply_text(
            "❌ Bu o‘yin allaqachon boshlangan."
        )
        return

    user = update.effective_user

    if not user:
        return

    user_id = str(user.id)
    name = user.first_name or user.username or "Noma’lum"

    if user_id in game["players"]:
        await update.message.reply_text(
            "Siz allaqachon o‘yinga ro‘yxatdan o‘tgansiz."
        )
        return

    game["players"][user_id] = name

    players = list(game["players"].values())

    try:
        await context.bot.edit_message_text(
            chat_id=game["chat_id"],
            message_id=game["message_id"],
            text=get_game_text(players),
            reply_markup=get_join_button(
                game["chat_id"],
                game["message_id"],
            ),
        )
    except Exception:
        pass

    await update.message.reply_text(
        "✅ Ro‘yxatdan muvaffaqiyatli o‘tdingiz!"
    )


# ======================= O'YINNI BOSHLASH =======================

def get_latest_game(chat_id):
    games = []

    for game_key, game in ACTIVE_GAMES.items():
        if game.get("chat_id") != chat_id:
            continue

        if game.get("started"):
            continue

        games.append(
            (
                game.get("message_id", 0),
                game_key,
                game,
            )
        )

    if not games:
        return None

    games.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return games[0][1], games[0][2]


def get_night_group_text():
    return (
        "🌙 • 𝑻𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
        "🌃 Shahar uyquga ketdi.\n\n"
        "🌙 Tun 1 daqiqa davom etadi.\n\n"
        "Har bir o‘yinchi shaxsiy chatidagi "
        "o‘z roliga tegishli qobiliyatidan foydalanadi."
    )


async def finish_night(game_key, context):
    game = ACTIVE_GAMES.get(game_key)

    if not game or game.get("phase") != "night":
        return

    game["phase"] = "voting"

    chat_id = game["chat_id"]

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "☀️ • 𝑲𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
                "🌅 Shahar uyg‘ondi.\n\n"
                "🗳 Ovoz berish uchun 45 soniyangiz bor."
            ),
        )
    except Exception:
        pass

    asyncio.create_task(
        finish_voting_after_delay(game_key, context)
    )


async def finish_voting_after_delay(game_key, context):
    await asyncio.sleep(VOTING_DURATION)

    game = ACTIVE_GAMES.get(game_key)

    if not game or game.get("phase") != "voting":
        return

    game["phase"] = "day"

    chat_id = game["chat_id"]

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "☀️ • 𝑲𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
                "🗳 Ovoz berish yakunlandi.\n\n"
                "☀️ Kun 50 soniya davom etadi."
            ),
        )
    except Exception:
        pass

    asyncio.create_task(
        finish_day_after_delay(game_key, context)
    )


async def finish_day_after_delay(game_key, context):
    await asyncio.sleep(DAY_DURATION)

    game = ACTIVE_GAMES.get(game_key)

    if not game or game.get("phase") != "day":
        return

    game["phase"] = "judgement"

    chat_id = game["chat_id"]

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "⚖️ • 𝑯𝑼𝑲𝑴 •\n\n"
                "⚖️ Hukm tashlash uchun 30 soniyangiz bor."
            ),
        )
    except Exception:
        pass

    asyncio.create_task(
        finish_judgement_after_delay(game_key, context)
    )


async def finish_judgement_after_delay(game_key, context):
    await asyncio.sleep(JUDGEMENT_DURATION)

    game = ACTIVE_GAMES.get(game_key)

    if not game or game.get("phase") != "judgement":
        return

    game["phase"] = "night"

    chat_id = game["chat_id"]

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=get_night_group_text(),
        )
    except Exception:
        pass

    asyncio.create_task(
        finish_night_after_delay(game_key, context)
    )


async def finish_night_after_delay(game_key, context):
    await asyncio.sleep(NIGHT_DURATION)

    game = ACTIVE_GAMES.get(game_key)

    if not game or game.get("phase") != "night":
        return

    await finish_night(game_key, context)


async def send_night_action_notice(game, context, role_key, target_name=None):
    chat_id = game["chat_id"]

    messages = {
        "don": "🎩 Don o‘z o‘ljasini tanladi.",
        "mafia": "🥷 Mafia o‘z harakatini amalga oshirdi.",
        "qotil": "🔪 Qotil o‘z o‘ljasini tanladi.",
        "komissar": "👮 Komissar o‘z harakatini tanladi.",
        "doktor": "👨‍⚕️ Doktor navbatchilikka ketdi.",
        "bodyguard": "🛡️ Bodyguard himoya uchun tanlov qildi.",
    }

    text = messages.get(role_key)

    if not text:
        return

    if target_name:
        text += f"\n🎯 Tanlov: {target_name}"

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
        )
    except Exception:
        pass


async def gamestart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.effective_chat.type not in ("group", "supergroup"):
        return

    result = get_latest_game(update.effective_chat.id)

    if not result:
        await update.message.reply_text(
            "❌ Boshlash uchun faol o‘yin topilmadi."
        )
        return

    game_key, game = result
    players = game.get("players", {})

    if not players:
        await update.message.reply_text(
            "❌ O‘yinda hech kim ro‘yxatdan o‘tmagan."
        )
        return

    if len(players) > len(ROLES):
        await update.message.reply_text(
            "❌ O‘yinchilar soni 25 tadan oshmasligi kerak."
        )
        return

    game["started"] = True
    game["phase"] = "night"
    game["roles"] = {}
    game["night_actions"] = {}

    selected_roles = ROLES[:len(players)]
    random.shuffle(selected_roles)

    player_items = list(players.items())

    for index, (player_id, player_name) in enumerate(player_items):
        role_name, role_key = selected_roles[index]

        game["roles"][player_id] = {
            "name": player_name,
            "role_name": role_name,
            "role_key": role_key,
            "alive": True,
        }

    try:
        await context.bot.edit_message_text(
            chat_id=game["chat_id"],
            message_id=game["message_id"],
            text=get_night_group_text(),
        )
    except Exception:
        pass

    for player_id, role_data in game["roles"].items():
        await send_role_to_player(
            context=context,
            player_id=player_id,
            player_name=role_data["name"],
            role_name=role_data["role_name"],
            role_key=role_data["role_key"],
            players=list(players.values()),
        )

    await update.message.reply_text(
        f"🌙 O‘yin boshlandi.\n"
        f"👥 O‘yinchilar: {len(players)}\n"
        f"🎭 Rollar tarqatildi."
    )

    asyncio.create_task(
        finish_night_after_delay(game_key, context)
    )


# ======================= HOZIRCHA ISHLAMAYDIGAN O'YIN KOMANDALARI =======================

async def inactive_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return


async def inactive_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return


# ======================= GROUP COMMANDS =======================

GROUP_VISIBLE_COMMANDS = [
    BotCommand("gamecreate", "O‘yin yaratish"),
    BotCommand("gamestart", "O‘yinni boshlash"),
    BotCommand("gamestop", "O‘yinni to‘xtatish"),
    BotCommand("gameexit", "O‘yindan chiqish"),
    BotCommand("paragame", "Para o‘yini yaratish"),
]

GROUP_HIDDEN_COMMANDS = [
    "para",
    "mypara",
    "dpara",
    "money",
    "give",
    "gift",
    "contest",
    "dcontest",
    "contesters",
    "top",
    "today",
    "groups",
    "richdiamond",
    "richdollar",
]


async def post_init(application):
    await application.bot.set_my_commands(
        GROUP_VISIBLE_COMMANDS,
        scope=BotCommandScopeAllGroupChats(),
    )


# ======================= CALLBACK =======================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""

    if data.startswith("lang_"):
        await language_button(update, context)

    elif data == "profile":
        await query.answer()

        await query.message.edit_text(
            get_profile_text(query.from_user),
            reply_markup=get_profile_buttons(),
        )

    elif data == "dollar_exchange":
        await dollar_exchange(update, context)

    elif data.startswith("exchange_"):
        await exchange_dollar(update, context)

    elif data == "diamond_buy":
        await diamond_buy(update, context)

    elif data == "shop":
        await shop(update, context)

    elif data.startswith("buy_"):
        await buy_item(update, context)

    elif data == "items_info":
        await items_info(update, context)

    elif data == "item_control":
        await item_control(update, context)

    elif data.startswith("toggle_"):
        await toggle_item(update, context)

    elif data.startswith("noop_"):
        await query.answer()

    elif data == "hero":
        await hero(update, context)

    elif data == "hero_levels":
        await hero_levels(update, context)

    elif data == "hero_skills":
        await hero_skills(update, context)

    elif data.startswith("role_"):
        await role_button(update, context)

    elif data in (
        "night_check",
        "night_kill",
        "night_heal",
        "night_don_kill",
        "night_killer",
        "night_guard",
    ):
        role_messages = {
            "night_check": ("komissar", "👮 Komissar o‘z harakatini tanladi."),
            "night_kill": ("komissar", "👮 Komissar o‘z harakatini tanladi."),
            "night_heal": ("doktor", "👨‍⚕️ Doktor navbatchilikka ketdi."),
            "night_don_kill": ("don", "🎩 Don o‘z o‘ljasini tanladi."),
            "night_killer": ("qotil", "🔪 Qotil o‘z o‘ljasini tanladi."),
            "night_guard": ("bodyguard", "🛡️ Bodyguard himoya uchun tanlov qildi."),
        }

        role_key, notice = role_messages[data]

        game_found = None

        for game in ACTIVE_GAMES.values():
            if game.get("phase") != "night":
                continue

            user_id = str(query.from_user.id)
            role_data = game.get("roles", {}).get(user_id)

            if role_data and role_data.get("role_key") == role_key:
                game_found = game
                break

        if game_found:
            if game_found.setdefault("night_actions", {}).get(
                str(query.from_user.id)
            ):
                await query.answer(
                    "✅ Siz bu tun harakatingizni tanlagansiz.",
                    show_alert=True,
                )
                return

            game_found["night_actions"][str(query.from_user.id)] = True

            try:
                await context.bot.send_message(
                    chat_id=game_found["chat_id"],
                    text=notice,
                )
            except Exception:
                pass

            await query.answer("✅ Harakat qabul qilindi.")
        else:
            await query.answer(
                "❌ Hozir faol tun topilmadi.",
                show_alert=True,
            )

    else:
        await query.answer()


# ======================= MAIN =======================

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    application = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("roles", roles))
    application.add_handler(CommandHandler("gamecreate", gamecreate))
    application.add_handler(CommandHandler("gamestart", gamestart))

    application.add_handler(
        CommandHandler("gamestop", inactive_game_command)
    )

    application.add_handler(
        CommandHandler("gameexit", inactive_game_command)
    )

    application.add_handler(
        CommandHandler("paragame", inactive_game_command)
    )

    for command in GROUP_HIDDEN_COMMANDS:
        application.add_handler(
            CommandHandler(command, inactive_group_command)
        )

    application.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
