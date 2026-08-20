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

# ============================================================
# O'YINLAR
# ============================================================

ACTIVE_GAMES = {}

NIGHT_SECONDS = 45

# Tun rasmi
NIGHT_IMAGE_URL = (
    "https://cdn.pixabay.com/photo/2016/11/29/03/53/"
    "architecture-1868667_1280.jpg"
)


def get_registration_text(game):
    players = game.get("players", {})

    lines = [
        "Ro‘yxatdan o‘tish davom etmoqda!",
        "Ro‘yxatdan o‘tganlar:",
        "",
    ]

    names = []

    for user_id, player in players.items():
        name = player.get("name", "Noma’lum")
        names.append(
            f'<a href="tg://user?id={user_id}">{name}</a>'
        )

    for i in range(0, len(names), 4):
        lines.append(", ".join(names[i:i + 4]))

    lines.append("")
    lines.append(f"Jami: {len(players)} ta")

    return "\n".join(lines)


def get_join_button(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Qo‘shilish",
                url=f"https://t.me/{BOT_USERNAME}?start=join_{chat_id}",
            )
        ]
    ])


def get_bot_button(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔗 Botga otish",
                url=f"https://t.me/{BOT_USERNAME}",
            )
        ]
    ])


def get_group_button(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔗 Guruhga otish",
                url=f"https://t.me/{BOT_USERNAME}?start=group_{chat_id}",
            )
        ]
    ])


def get_player_button(user_id, name):
    return InlineKeyboardButton(
        name,
        url=f"tg://user?id={user_id}",
    )


# ============================================================
# BUYUMLAR
# ============================================================

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


# ============================================================
# DATA
# ============================================================

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
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
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


# ============================================================
# START
# ============================================================

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
                url="https://t.me/+ABdv1H2Z2_llYWYy",
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


# ============================================================
# PROFILE
# ============================================================

def get_profile_text(user):
    _, data = get_user_data(user.id)

    vip_line = "\n👑 VIP: Ha" if data["vip"] else ""

    games = data.get("games", 0)
    wins = data.get("wins", 0)

    percent = int((wins / games) * 100) if games > 0 else 0

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


# ============================================================
# DOLLAR
# ============================================================

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
            await query.answer(
                "❌ Olmos yetarli emas",
                show_alert=True,
            )
            return

        user["diamond"] -= amount

    user["dollar"] += amount * 600

    save_data(data)

    await query.answer(
        "✅ Savdo muvaffaqiyatli amalga oshirildi!"
    )

    await query.message.edit_text(
        get_profile_text(query.from_user),
        reply_markup=get_profile_buttons(),
    )


# ============================================================
# OLMOS
# ============================================================

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
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile",
        )
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


# ============================================================
# SHOP
# ============================================================

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
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile",
        )
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
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    name, price, currency = ITEMS[key]

    data, user = get_user_data(query.from_user.id)

    if query.from_user.id != OWNER_ID:
        if user[currency] < price:
            await query.answer(
                "❌ Mablag‘ yetarli emas",
                show_alert=True,
            )
            return

        user[currency] -= price

    if key == "hero":
        user["hero"] += 1
    elif key == "active_role":
        user["active_role"] += 1
    else:
        user["items"][key] += 1

    save_data(data)

    await query.answer(
        "✅ Xarid muvaffaqiyatli amalga oshirildi!"
    )

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "✅ Xarid muvaffaqiyatli amalga oshirildi.\n\n"
        "Yana buyum tanlang:",
        reply_markup=get_shop_buttons(),
    )


# ============================================================
# BUYUMLAR HAQIDA
# ============================================================

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
            [
                InlineKeyboardButton(
                    "🔙 Orqaga",
                    callback_data="profile",
                )
            ]
        ]),
    )


# ============================================================
# ITEM CONTROL
# ============================================================

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

        status = (
            "🟢 ON"
            if user["active_items"][key]
            else "⚪ OFF"
        )

        keyboard.append([
            InlineKeyboardButton(
                status,
                callback_data=f"toggle_{key}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile",
        )
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
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    data, user = get_user_data(query.from_user.id)

    if key not in user["items"]:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
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


# ============================================================
# HERO
# ============================================================

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

    return (
        current[0],
        current[1],
        current[2],
        next_xp,
    )


def get_hero_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Darajalar",
                callback_data="hero_levels",
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ Qobiliyatlar",
                callback_data="hero_skills",
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Orqaga",
                callback_data="profile",
            )
        ],
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
                [
                    InlineKeyboardButton(
                        "💰 Do‘konga",
                        callback_data="shop",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Orqaga",
                        callback_data="profile",
                    )
                ],
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
        await query.answer(
            "❌ Sizda Geroy yo‘q",
            show_alert=True,
        )
        return

    current_level = get_hero_level(
        user.get("hero_xp", 0)
    )

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
            [
                InlineKeyboardButton(
                    "🔙 Geroy profiliga",
                    callback_data="hero",
                )
            ]
        ]),
    )


async def hero_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.answer(
            "❌ Sizda Geroy yo‘q",
            show_alert=True,
        )
        return

    level = get_hero_level(
        user.get("hero_xp", 0)
    )

    skills = [
        item[2]
        for item in HERO_LEVELS[:level]
    ]

    text = (
        "⚡ • 𝑮𝒆𝒓𝒐𝒚 𝑸𝒐𝒃𝒊𝒍𝒊𝒚𝒂𝒕𝒍𝒂𝒓𝒊 •\n\n"
        f"🏆 Daraja: {level}/5\n\n"
        + "\n".join(skills)
    )

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Geroy profiliga",
                    callback_data="hero",
                )
            ]
        ]),
    )


# ============================================================
# 25 TA ROL
# ============================================================

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


ROLE_DESCRIPTIONS = {
    "don": "Bu tunda kim o‘lishini siz hal qilasiz. Siz (Mafialar sardori)siz.",
    "mafia": "Bu tunda Mafia jamoasi bilan birga harakat qilasiz.",
    "aferist": "Aldov va hiyla orqali o‘yinda omon qolishga harakat qilasiz.",
    "qotil": "Siz mustaqil qotilsiz.",
    "komissar": "Siz shubhali o‘yinchilarni tekshirishingiz yoki o‘ldirishingiz mumkin.",
    "doktor": "Siz tunda o‘yinchini himoya qilishingiz mumkin.",
    "serjant": "Siz tunda maxsus harakat qilishingiz mumkin.",
    "kapitan": "Siz tunda maxsus harakat qilishingiz mumkin.",
    "fuqaro": "Siz tinchliksevar jamoa tarafidasiz.",
    "daydi": "Siz tunda mustaqil harakat qilasiz.",
    "sudya": "Siz ovoz berishda maxsus huquqqa egasiz.",
    "advokat": "Siz o‘yinchini himoya qilishga yordam berasiz.",
    "qasoskor": "Siz maxsus qasos qobiliyatiga egasiz.",
    "buqalamun": "Siz o‘z rolingizni yashirishga qodirsiz.",
    "kuzatuvchi": "Siz o‘yinchilar harakatini kuzatasiz.",
    "bodyguard": "Siz boshqa o‘yinchini himoya qilishingiz mumkin.",
    "sehrgar": "Siz maxsus sehrli qobiliyatga egasiz.",
    "jurnalist": "Siz muhim ma’lumotlarni aniqlashga harakat qilasiz.",
    "kimyogar": "Siz maxsus moddalar bilan ishlaysiz.",
    "minyor": "Siz tunda maxsus tuzoq qo‘yishingiz mumkin.",
    "koldun": "Siz sirli kuchlardan foydalanasiz.",
    "agent": "Siz yashirin topshiriqlarni bajarasiz.",
    "arvoh": "Siz maxsus ta’sirga ega bo‘lishingiz mumkin.",
    "joker": "Siz o‘yinni chalkashtirib, o‘z maqsadingizga erishasiz.",
    "vampir": "Siz tunda harakat qiladigan mustaqil rolsiz.",
}


# ============================================================
# ROL TURLARI
# ============================================================

MAFIA_ROLES = {
    "don",
    "mafia",
}

NIGHT_ACTION_ROLES = {
    "don",
    "mafia",
    "qotil",
    "komissar",
    "doktor",
    "serjant",
    "kapitan",
    "daydi",
    "qasoskor",
    "buqalamun",
    "kuzatuvchi",
    "bodyguard",
    "sehrgar",
    "kimyogar",
    "minyor",
    "koldun",
    "agent",
    "vampir",
}

NO_NIGHT_ACTION_ROLES = {
    "aferist",
    "fuqaro",
    "sudya",
    "advokat",
    "jurnalist",
    "arvoh",
    "joker",
}


def get_roles_for_player_count(count):
    """
    Kichik o'yinlarda ham Komissar tushishi mumkin.
    Katta o'yinlarda maxsus rollar ko'proq ochiladi.
    """

    if count <= 6:
        pool = [
            "don",
            "mafia",
            "komissar",
            "doktor",
            "qotil",
            "fuqaro",
        ]

    elif count <= 10:
        pool = [
            "don",
            "mafia",
            "komissar",
            "doktor",
            "qotil",
            "serjant",
            "kapitan",
            "fuqaro",
            "daydi",
            "bodyguard",
        ]

    elif count <= 15:
        pool = [
            "don",
            "mafia",
            "aferist",
            "qotil",
            "komissar",
            "doktor",
            "serjant",
            "kapitan",
            "fuqaro",
            "daydi",
            "sudya",
            "advokat",
            "qasoskor",
            "buqalamun",
            "kuzatuvchi",
        ]

    elif count <= 20:
        pool = [
            "don",
            "mafia",
            "aferist",
            "qotil",
            "komissar",
            "doktor",
            "serjant",
            "kapitan",
            "fuqaro",
            "daydi",
            "sudya",
            "advokat",
            "qasoskor",
            "buqalamun",
            "kuzatuvchi",
            "bodyguard",
            "sehrgar",
            "jurnalist",
            "kimyogar",
            "minyor",
        ]

    else:
        pool = [
            key
            for _, key in ROLES
        ]

    return pool


def make_random_roles(count):
    pool = get_roles_for_player_count(count)

    if count <= len(pool):
        selected = random.sample(pool, count)
    else:
        selected = random.choices(pool, k=count)

    # Komissar kichik o'yinda ham tushishi uchun
    # agar pool ichida Komissar bo'lsa, u random tanlanadi.
    random.shuffle(selected)

    return selected


# ============================================================
# ROL XABARLARI
# ============================================================

def get_role_message(role_name, role_key):
    description = ROLE_DESCRIPTIONS.get(
        role_key,
        "Siz maxsus rol egasisiz.",
    )

    return (
        f"Siz — {role_name}siz!\n"
        f"{description}"
    )


def get_partner_text(game, player_id):
    role_data = game.get("roles", {}).get(str(player_id))

    if not role_data:
        return None

    role_key = role_data.get("role_key")

    if role_key not in MAFIA_ROLES:
        return None

    partners = []

    for other_id, other_role in game["roles"].items():
        if str(other_id) == str(player_id):
            continue

        if other_role.get("role_key") in MAFIA_ROLES:
            partners.append(
                (
                    other_id,
                    other_role.get(
                        "name",
                        "Noma’lum",
                    ),
                    other_role.get(
                        "role_name",
                        "",
                    ),
                )
            )

    if not partners:
        return None

    lines = [
        "Sheriklaringizni eslab qoling!",
        "",
    ]

    for partner_id, name, role_name in partners:
        lines.append(
            f'<a href="tg://user?id={partner_id}">'
            f'{name}</a> - {role_name}'
        )

    return "\n".join(lines)


def get_action_text(role_key):
    actions = {
        "don": "Kimni o‘ldirasiz?",
        "mafia": "Kimni o‘ldirasiz?",
        "qotil": "Kimni o‘ldirasiz?",
        "doktor": "Kimni davolaysiz?",
        "serjant": "Kimni kuzatasiz?",
        "kapitan": "Kimni himoya qilasiz?",
        "daydi": "Kimning oldiga borasiz?",
        "qasoskor": "Kimdan qasos olasiz?",
        "buqalamun": "Kimning rolini yashirasiz?",
        "kuzatuvchi": "Kimni kuzatasiz?",
        "bodyguard": "Kimni himoya qilasiz?",
        "sehrgar": "Kimga sehr ishlatasiz?",
        "kimyogar": "Kimga dori ishlatasiz?",
        "minyor": "Kimga tuzoq qo‘yasiz?",
        "koldun": "Kimga sehr ishlatasiz?",
        "agent": "Kimni kuzatasiz?",
        "vampir": "Kimni tishlaysiz?",
    }

    return actions.get(
        role_key,
        "Kimni tanlaysiz?",
    )


def get_alive_player_buttons(game, current_player_id):
    keyboard = []

    for player_id, player_data in game["players"].items():
        if str(player_id) == str(current_player_id):
            continue

        role_data = game.get("roles", {}).get(str(player_id))

        if role_data and not role_data.get("alive", True):
            continue

        name = player_data.get(
            "name",
            "Noma’lum",
        )

        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=(
                    f"nighttarget_{game['chat_id']}_"
                    f"{current_player_id}_{player_id}"
                ),
            )
        ])

    return InlineKeyboardMarkup(keyboard)


def get_commissioner_action_buttons(chat_id, player_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🔪 O‘ldirish",
                callback_data=(
                    f"commkill_{chat_id}_{player_id}"
                ),
            ),
            InlineKeyboardButton(
                "🔎 Tekshirish",
                callback_data=(
                    f"commcheck_{chat_id}_{player_id}"
                ),
            ),
        ]
    ])


# ============================================================
# O'YIN YARATISH
# ============================================================

async def gamecreate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.effective_chat.type not in (
        "group",
        "supergroup",
    ):
        return

    chat_id = update.effective_chat.id

    old_game = ACTIVE_GAMES.get(chat_id)

    old_players = {}

    if old_game:
        old_players = dict(
            old_game.get("players", {})
        )

        old_message_id = old_game.get("message_id")

        if old_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=old_message_id,
                )
            except Exception:
                pass

    new_game = {
        "chat_id": chat_id,
        "message_id": None,
        "players": old_players,
        "started": False,
        "phase": "registration",
        "roles": {},
        "group_messages": [],
        "night_action_messages": {},
        "night_started": False,
    }

    message = await context.bot.send_message(
        chat_id=chat_id,
        text=get_registration_text(new_game),
        reply_markup=get_join_button(chat_id),
        parse_mode="HTML",
    )

    new_game["message_id"] = message.message_id

    ACTIVE_GAMES[chat_id] = new_game

    try:
        await context.bot.pin_chat_message(
            chat_id=chat_id,
            message_id=message.message_id,
            disable_notification=True,
        )
    except Exception:
        pass


# ============================================================
# O'YINGA QO'SHILISH
# ============================================================

async def register_game_player(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "🖤 Salom! Xush kelibsiz!"
        )
        return

    payload = context.args[0]

    if not payload.startswith("join_"):
        await update.message.reply_text(
            "🖤 Salom! Xush kelibsiz!"
        )
        return

    try:
        chat_id = int(payload[5:])
    except (ValueError, TypeError):
        await update.message.reply_text(
            "❌ O‘yin topilmadi."
        )
        return

    game = ACTIVE_GAMES.get(chat_id)

    if not game:
        await update.message.reply_text(
            "❌ Bu o‘yin ro‘yxatdan o‘tishi yopilgan "
            "yoki mavjud emas."
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

    name = (
        user.first_name
        or user.username
        or "Noma’lum"
    )

    if user_id in game["players"]:
        await update.message.reply_text(
            "ℹ️ Siz allaqachon ro‘yxatdan o‘tgansiz."
        )
        return

    if len(game["players"]) >= 25:
        await update.message.reply_text(
            "❌ O‘yin 25 ta o‘yinchidan oshmaydi."
        )
        return

    game["players"][user_id] = {
        "name": name,
    }

    ACTIVE_GAMES[chat_id] = game

    try:
        await update.message.reply_text(
            "✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!"
        )
    except Exception:
        pass

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=game["message_id"],
            text=get_registration_text(game),
            reply_markup=get_join_button(chat_id),
            parse_mode="HTML",
        )
    except Exception:
        pass


# ============================================================
# O'YINNI BOSHLASH
# ============================================================

async def gamestart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.effective_chat.type not in (
        "group",
        "supergroup",
    ):
        return

    chat_id = update.effective_chat.id

    game = ACTIVE_GAMES.get(chat_id)

    if not game:
        await update.message.reply_text(
            "❌ Boshlash uchun faol o‘yin topilmadi."
        )
        return

    if game.get("started"):
        await update.message.reply_text(
            "❌ Bu o‘yin allaqachon boshlangan."
        )
        return

    players = game.get("players", {})

    if not players:
        await update.message.reply_text(
            "❌ O‘yinda hech kim ro‘yxatdan o‘tmagan."
        )
        return

    if len(players) > 25:
        await update.message.reply_text(
            "❌ O‘yinchilar soni 25 tadan oshmasligi kerak."
        )
        return

    game["started"] = True
    game["phase"] = "night"
    game["roles"] = {}

    role_keys = make_random_roles(len(players))

    player_items = list(players.items())

    for index, (player_id, player_data) in enumerate(
        player_items
    ):
        role_key = role_keys[index]

        role_name = next(
            name
            for name, key in ROLES
            if key == role_key
        )

        game["roles"][str(player_id)] = {
            "name": player_data["name"],
            "role_name": role_name,
            "role_key": role_key,
            "alive": True,
        }

    # ========================================================
    # 1-XABAR
    # ========================================================

    message1 = await context.bot.send_message(
        chat_id=chat_id,
        text="O‘yin boshlandi!",
        reply_markup=get_bot_button(chat_id),
    )

    # ========================================================
    # 2-XABAR — RASM BILAN
    # ========================================================

    message2 = await context.bot.send_photo(
        chat_id=chat_id,
        photo=NIGHT_IMAGE_URL,
        caption=(
            "🌙 Tun\n\n"
            "Shaharni qorong‘ulik qopladi. Ko‘chalarda sukunat "
            "hukm surmoqda.\n"
            "Bu tun har kim uchun xavfli bo‘lishi mumkin...\n\n"
            "Tong otgach, kimlar omon qolganini bilib olamiz."
        ),
        reply_markup=get_bot_button(chat_id),
    )

    # ========================================================
    # 3-XABAR — TIRIK O'YINCHILAR + 45 SEKUND
    # ========================================================

    message3 = await context.bot.send_message(
        chat_id=chat_id,
        text=get_alive_players_text(
            game,
            NIGHT_SECONDS,
        ),
        reply_markup=get_alive_players_keyboard(
            game,
            chat_id,
        ),
        parse_mode="HTML",
    )

    game["group_messages"] = [
        message1.message_id,
        message2.message_id,
        message3.message_id,
    ]

    game["timer_message_id"] = message3.message_id
    game["night_started"] = True

    ACTIVE_GAMES[chat_id] = game

    # ========================================================
    # SHAXSIY ROL XABARLARI
    # ========================================================

    for player_id, role_data in game["roles"].items():
        role_key = role_data["role_key"]
        role_name = role_data["role_name"]

        try:
            await context.bot.send_message(
                chat_id=int(player_id),
                text=get_role_message(
                    role_name,
                    role_key,
                ),
                reply_markup=get_group_button(chat_id),
            )
        except Exception:
            pass

    # ========================================================
    # SHERIKLAR XABARI
    # ========================================================

    for player_id in game["roles"]:
        partner_text = get_partner_text(
            game,
            player_id,
        )

        if not partner_text:
            continue

        try:
            await context.bot.send_message(
                chat_id=int(player_id),
                text=partner_text,
                parse_mode="HTML",
            )
        except Exception:
            pass

    # ========================================================
    # TUNGI HARAKAT XABARLARI
    # ========================================================

    for player_id, role_data in game["roles"].items():
        role_key = role_data["role_key"]

        if role_key not in NIGHT_ACTION_ROLES:
            continue

        try:
            if role_key == "komissar":
                action_message = await context.bot.send_message(
                    chat_id=int(player_id),
                    text="Nima qilasiz?",
                    reply_markup=get_commissioner_action_buttons(
                        chat_id,
                        player_id,
                    ),
                )
            else:
                action_message = await context.bot.send_message(
                    chat_id=int(player_id),
                    text=get_action_text(role_key),
                    reply_markup=get_alive_player_buttons(
                        game,
                        player_id,
                    ),
                )

            game["night_action_messages"][str(player_id)] = (
                action_message.message_id
            )

        except Exception:
            pass

    ACTIVE_GAMES[chat_id] = game

    # Taymerni alohida ishga tushiramiz.
    asyncio.create_task(
        night_timer(
            chat_id,
            context,
        )
    )


# ============================================================
# TIRIK O'YINCHILAR
# ============================================================

def get_alive_players_text(game, seconds):
    lines = [
        "Tirik o‘yinchilar:",
        "",
    ]

    number = 1

    for player_id, player in game["players"].items():
        role_data = game["roles"].get(
            str(player_id),
            {},
        )

        if role_data.get("alive", True):
            name = player.get(
                "name",
                "Noma’lum",
            )

            lines.append(
                f"{number}. "
                f'<a href="tg://user?id={player_id}">'
                f'{name}</a>'
            )

            number += 1

    lines.extend([
        "",
        f"Tonggacha ⏳ {seconds} sekund qoldi",
    ])

    return "\n".join(lines)


def get_alive_players_keyboard(game, chat_id):
    return get_bot_button(chat_id)


# ============================================================
# TAYMER
# ============================================================

async def night_timer(
    chat_id,
    context: ContextTypes.DEFAULT_TYPE,
):
    for seconds in range(
        NIGHT_SECONDS,
        0,
        -1,
    ):
        await asyncio.sleep(1)

        game = ACTIVE_GAMES.get(chat_id)

        if not game:
            return

        if not game.get("started"):
            return

        if game.get("phase") != "night":
            return

        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game["timer_message_id"],
                text=get_alive_players_text(
                    game,
                    seconds - 1,
                ),
                reply_markup=get_alive_players_keyboard(
                    game,
                    chat_id,
                ),
                parse_mode="HTML",
            )
        except Exception:
            pass

    game = ACTIVE_GAMES.get(chat_id)

    if not game:
        return

    if game.get("phase") != "night":
        return

    game["phase"] = "dawn"

    ACTIVE_GAMES[chat_id] = game

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=game["timer_message_id"],
            text=get_alive_players_text(
                game,
                0,
            ),
            reply_markup=get_alive_players_keyboard(
                game,
                chat_id,
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass


# ============================================================
# TUNGI HARAKATLAR
# ============================================================

async def night_target(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    parts = query.data.split("_")

    if len(parts) != 4:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    try:
        chat_id = int(parts[1])
        player_id = str(parts[2])
        target_id = str(parts[3])
    except ValueError:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    game = ACTIVE_GAMES.get(chat_id)

    if not game:
        await query.answer(
            "❌ O‘yin topilmadi.",
            show_alert=True,
        )
        return

    if game.get("phase") != "night":
        await query.answer(
            "❌ Tun tugagan.",
            show_alert=True,
        )
        return

    role_data = game["roles"].get(player_id)

    if not role_data:
        await query.answer(
            "❌ Rol topilmadi.",
            show_alert=True,
        )
        return

    if not role_data.get("alive", True):
        await query.answer(
            "❌ Siz o‘yinda emassiz.",
            show_alert=True,
        )
        return

    target_data = game["players"].get(target_id)

    if not target_data:
        await query.answer(
            "❌ O‘yinchi topilmadi.",
            show_alert=True,
        )
        return

    role_key = role_data["role_key"]

    await query.answer(
        "✅ Tanlandi!",
    )

    message_id = game.get(
        "night_action_messages",
        {},
    ).get(player_id)

    action_text = get_action_text(role_key)

    selected_name = target_data.get(
        "name",
        "Noma’lum",
    )

    if role_key in ("don", "mafia", "qotil"):
        result = (
            f"{action_text}\n\n"
            f"✅ Tanlandi: {selected_name}"
        )

    else:
        result = (
            f"{action_text}\n\n"
            f"✅ Tanlandi: {selected_name}"
        )

    if message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=int(player_id),
                message_id=message_id,
                text=result,
            )
        except Exception:
            pass


# ============================================================
# KOMISSAR
# ============================================================

async def commissioner_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    parts = query.data.split("_")

    if len(parts) != 3:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    try:
        chat_id = int(parts[1])
        player_id = str(parts[2])
    except ValueError:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    game = ACTIVE_GAMES.get(chat_id)

    if not game:
        await query.answer(
            "❌ O‘yin topilmadi.",
            show_alert=True,
        )
        return

    if game.get("phase") != "night":
        await query.answer(
            "❌ Tun tugagan.",
            show_alert=True,
        )
        return

    role_data = game["roles"].get(player_id)

    if not role_data or role_data.get("role_key") != "komissar":
        await query.answer(
            "❌ Bu amal faqat Komissar uchun.",
            show_alert=True,
        )
        return

    message_id = game.get(
        "night_action_messages",
        {},
    ).get(player_id)

    if not message_id:
        await query.answer(
            "❌ Xabar topilmadi.",
            show_alert=True,
        )
        return

    if query.data.startswith("commkill_"):
        text = "Kimni o‘ldirasiz?"

    else:
        text = "Kimni tekshirasiz?"

    await query.answer()

    try:
        await context.bot.edit_message_text(
            chat_id=int(player_id),
            message_id=message_id,
            text=text,
            reply_markup=get_alive_player_buttons(
                game,
                player_id,
            ),
        )
    except Exception:
        pass


# ============================================================
# ROLE TEKSHIRISH / O'LDIRISH
# ============================================================

async def commissioner_target(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    parts = query.data.split("_")

    if len(parts) != 4:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    try:
        chat_id = int(parts[1])
        player_id = str(parts[2])
        target_id = str(parts[3])
    except ValueError:
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
        return

    game = ACTIVE_GAMES.get(chat_id)

    if not game:
        await query.answer(
            "❌ O‘yin topilmadi.",
            show_alert=True,
        )
        return

    role_data = game["roles"].get(player_id)

    if not role_data:
        await query.answer(
            "❌ Komissar topilmadi.",
            show_alert=True,
        )
        return

    message_id = game.get(
        "night_action_messages",
        {},
    ).get(player_id)

    target_role = game["roles"].get(
        target_id
    )

    target_player = game["players"].get(
        target_id,
        {},
    )

    if not target_role:
        await query.answer(
            "❌ O‘yinchi topilmadi.",
            show_alert=True,
        )
        return

    target_name = target_player.get(
        "name",
        "Noma’lum",
    )

    if query.data.startswith("commkilltarget_"):
        target_role["alive"] = False

        text = (
            "Kimni o‘ldirasiz?\n\n"
            f"✅ Tanlandi: {target_name}"
        )

    else:
        role_name = target_role.get(
            "role_name",
            "Noma’lum",
        )

        text = (
            "Kimni tekshirasiz?\n\n"
            f"🔎 {target_name} — {role_name}"
        )

    game["roles"][target_id] = target_role
    ACTIVE_GAMES[chat_id] = game

    await query.answer(
        "✅ Tanlandi!"
    )

    if message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=int(player_id),
                message_id=message_id,
                text=text,
            )
        except Exception:
            pass


# ============================================================
# 25 TA ROL TUGMALARI
# ============================================================

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

    role_key = query.data.replace(
        "role_",
        "",
        1,
    )

    role_name = next(
        (
            name
            for name, key in ROLES
            if key == role_key
        ),
        None,
    )

    description = ROLE_DESCRIPTIONS.get(
        role_key,
        "Bu rol haqida ma’lumot topilmadi.",
    )

    if not role_name:
        await query.answer(
            "❌ Bu rol topilmadi.",
            show_alert=True,
        )
        return

    await query.answer(
        f"{role_name}\n\n{description}",
        show_alert=True,
    )


# ============================================================
# O'YIN TO'XTATISH / CHIQISH
# ============================================================

async def inactive_game_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    return


async def inactive_group_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    return


# ============================================================
# GROUP COMMANDS
# ============================================================

GROUP_VISIBLE_COMMANDS = [
    BotCommand(
        "gamecreate",
        "O‘yin yaratish",
    ),
    BotCommand(
        "gamestart",
        "O‘yinni boshlash",
    ),
    BotCommand(
        "gamestop",
        "O‘yinni to‘xtatish",
    ),
    BotCommand(
        "gameexit",
        "O‘yindan chiqish",
    ),
    BotCommand(
        "paragame",
        "Para o‘yini yaratish",
    ),
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


# ============================================================
# CALLBACK
# ============================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    data = query.data or ""

    if data.startswith("lang_"):
        await language_button(
            update,
            context,
        )

    elif data == "profile":
        await query.answer()

        await query.message.edit_text(
            get_profile_text(
                query.from_user
            ),
            reply_markup=get_profile_buttons(),
        )

    elif data == "dollar_exchange":
        await dollar_exchange(
            update,
            context,
        )

    elif data.startswith("exchange_"):
        await exchange_dollar(
            update,
            context,
        )

    elif data == "diamond_buy":
        await diamond_buy(
            update,
            context,
        )

    elif data == "shop":
        await shop(
            update,
            context,
        )

    elif data.startswith("buy_"):
        await buy_item(
            update,
            context,
        )

    elif data == "items_info":
        await items_info(
            update,
            context,
        )

    elif data == "item_control":
        await item_control(
            update,
            context,
        )

    elif data.startswith("toggle_"):
        await toggle_item(
            update,
            context,
        )

    elif data.startswith("noop_"):
        await query.answer()

    elif data == "hero":
        await hero(
            update,
            context,
        )

    elif data == "hero_levels":
        await hero_levels(
            update,
            context,
        )

    elif data == "hero_skills":
        await hero_skills(
            update,
            context,
        )

    elif data.startswith("role_"):
        await role_button(
            update,
            context,
        )

    elif data.startswith("commkill_"):
        await commissioner_action(
            update,
            context,
        )

    elif data.startswith("commcheck_"):
        await commissioner_action(
            update,
            context,
        )

    elif data.startswith("commkilltarget_"):
        await commissioner_target(
            update,
            context,
        )

    elif data.startswith("commchecktarget_"):
        await commissioner_target(
            update,
            context,
        )

    elif data.startswith("nighttarget_"):
        await night_target(
            update,
            context,
        )

    else:
        await query.answer()


# ============================================================
# MAIN
# ============================================================

def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN Secret topilmadi"
        )

    application = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "profile",
            profile,
        )
    )

    application.add_handler(
        CommandHandler(
            "roles",
            roles,
        )
    )

    application.add_handler(
        CommandHandler(
            "gamecreate",
            gamecreate,
        )
    )

    application.add_handler(
        CommandHandler(
            "gamestart",
            gamestart,
        )
    )

    application.add_handler(
        CommandHandler(
            "gamestop",
            inactive_game_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "gameexit",
            inactive_game_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "paragame",
            inactive_game_command,
        )
    )

    for command in GROUP_HIDDEN_COMMANDS:
        application.add_handler(
            CommandHandler(
                command,
                inactive_group_command,
            )
        )

    application.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
