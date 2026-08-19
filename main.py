import os
import json
import random
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

ACTIVE_GAMES = {}


# ============================================================
# YORDAMCHI
# ============================================================

def get_game_key(chat_id, message_id):
    return f"{chat_id}_{message_id}"


def load_data():
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
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
        [
            InlineKeyboardButton(
                "🇺🇿 O‘zbekcha",
                callback_data="lang_uz",
            )
        ],
        [
            InlineKeyboardButton(
                "🇷🇺 Русский",
                callback_data="lang_ru",
            )
        ],
        [
            InlineKeyboardButton(
                "🇹🇷 Türkçe",
                callback_data="lang_tr",
            )
        ],
        [
            InlineKeyboardButton(
                "🇰🇿 Қазақша",
                callback_data="lang_kk",
            )
        ],
        [
            InlineKeyboardButton(
                "🇺🇦 Українська",
                callback_data="lang_uk",
            )
        ],
        [
            InlineKeyboardButton(
                "🇩🇪 Deutsch",
                callback_data="lang_de",
            )
        ],
        [
            InlineKeyboardButton(
                "🇬🇧 English",
                callback_data="lang_en",
            )
        ],
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

    if context.args and context.args[0].startswith("vote_"):
        await private_vote(update, context)
        return

    await update.message.reply_text(
        "🌍 Tilni tanlang:",
        reply_markup=get_language_buttons(),
    )


async def language_button(update, context):
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

    percent = int((wins / games) * 100) if games else 0

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
        [
            InlineKeyboardButton(
                "💵 Dollar olish",
                callback_data="dollar_exchange",
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Olmos olish",
                callback_data="diamond_buy",
            )
        ],
        [
            InlineKeyboardButton(
                "⚔️ Mening Geroyim",
                callback_data="hero",
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Do‘kon",
                callback_data="shop",
            )
        ],
        [
            InlineKeyboardButton(
                "📖 Buyumlar haqida",
                callback_data="items_info",
            )
        ],
        [
            InlineKeyboardButton(
                "🔻",
                callback_data="item_control",
            )
        ],
    ])


async def profile(update, context):
    if not update.message:
        return

    await update.message.reply_text(
        get_profile_text(update.effective_user),
        reply_markup=get_profile_buttons(),
    )


# ============================================================
# DOLLAR / OLMOS
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
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile",
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def dollar_exchange(update, context):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Olmosni Dollarga almashtiring:",
        reply_markup=get_dollar_buttons(),
    )


async def exchange_dollar(update, context):
    query = update.callback_query

    try:
        amount = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        await query.answer(
            "❌ Xatolik",
            show_alert=True,
        )
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


async def diamond_buy(update, context):
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


async def shop(update, context):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "Kerakli buyumni tanlang:",
        reply_markup=get_shop_buttons(),
    )


async def buy_item(update, context):
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


DESCRIPTIONS = {
    "shield": "bir marta hujumdan himoya qiladi.",
    "document": "tekshiruvda rolni yashirishga yordam beradi.",
    "forgiveness": "bir marta jazodan qutqaradi.",
    "killer_mask": "qotilni aniqlashni qiyinlashtiradi.",
    "gun": "bir marta hujum qilish imkonini beradi.",
    "black_medicine": "salbiy ta’sirni olib tashlaydi.",
    "verbena": "vampirdan himoya qiladi.",
    "mystery_mask": "rolni vaqtincha yashiradi.",
    "hero_protection": "geroy hujumidan himoya qiladi.",
    "hero": "sotib olingandan keyin Geroy beriladi.",
    "active_role": "1 ta o‘yin uchun faol rol beradi.",
}


async def items_info(update, context):
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
# BUYUM BOSHQARUVI
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


async def item_control(update, context):
    query = update.callback_query
    await query.answer()

    _, user = get_user_data(query.from_user.id)

    await query.message.edit_text(
        "🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\n"
        "Buyumni ON yoki OFF holatiga o‘tkazing.",
        reply_markup=get_control_buttons(user),
    )


async def toggle_item(update, context):
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

    next_xp = None if level >= 5 else HERO_LEVELS[level][1]

    return current[0], current[1], current[2], next_xp


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


async def hero(update, context):
    query = update.callback_query
    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.message.edit_text(
            "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
            "❌ Sizda Geroy mavjud emas.",
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


async def hero_levels(update, context):
    query = update.callback_query
    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.answer(
            "❌ Sizda Geroy yo‘q",
            show_alert=True,
        )
        return

    current_level = get_hero_level(user.get("hero_xp", 0))

    text = (
        "🏆 • 𝑮𝒆𝒓𝒐𝒚 𝑫𝒂𝒓𝒂𝒋𝒂𝒍𝒂𝒓𝒊 •\n\n"
        "🥉 I — Bronze\n⚔️ Hujum\n🔓 0 XP\n\n"
        "🥈 II — Silver\n🛡️ Himoya\n🔓 100 XP\n\n"
        "🥇 III — Gold\n🪖 Zirh\n🔓 300 XP\n\n"
        "💎 IV — Diamond\n⚡ Maxsus qobiliyat\n🔓 700 XP\n\n"
        "🖤 V — Noir\n👑 Maxsus kuch\n🔓 1500 XP\n\n"
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


async def hero_skills(update, context):
    query = update.callback_query
    await query.answer()

    _, user = get_user_data(query.from_user.id)

    if user["hero"] <= 0:
        await query.answer(
            "❌ Sizda Geroy yo‘q",
            show_alert=True,
        )
        return

    level = get_hero_level(user.get("hero_xp", 0))

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
# 25 ROL
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


ROLE_MESSAGES = {
    "don": "🎩 • DON •\n\nSiz Don bo‘ldingiz.\n\n🌙 Tun boshlandi.\nMafiyaning boshlig‘i sifatida nishonni tanlang.",
    "mafia": "🥷 • MAFIA •\n\nSiz Mafia bo‘ldingiz.\n\n🌙 Tun boshlandi.\nTungi harakatlarda qatnashing.",
    "aferist": "🎭 • AFERIST •\n\nSiz Aferist bo‘ldingiz.\n\n🌙 Tun boshlandi.\nAldov va hiyla orqali omon qoling.",
    "qotil": "🔪 • QOTIL •\n\nSiz Qotil bo‘ldingiz.\n\n🌙 Tun boshlandi.\nNishonni tanlang.",
    "komissar": "👮 • KOMISSAR •\n\nSiz Komissar bo‘ldingiz.\n\n🌙 Tun boshlandi.\nTekshirish yoki o‘ldirishni tanlang.",
    "doktor": "👨‍⚕️ • DOKTOR •\n\nSiz Doktor bo‘ldingiz.\n\n🌙 Tun boshlandi.\nKimnidir davolang.",
    "serjant": "👮‍♂️ • SERJANT •\n\nSiz Serjant bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "kapitan": "🎖️ • KAPITAN •\n\nSiz Kapitan bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "fuqaro": "👤 • FUQARO •\n\nSiz Fuqaro bo‘ldingiz.\n\n🌙 Tun boshlandi.\nOmon qoling.",
    "daydi": "👣 • DAYDI •\n\nSiz Daydi bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "sudya": "⚖️ • SUDYA •\n\nSiz Sudya bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "advokat": "👨‍⚖️ • ADVOKAT •\n\nSiz Advokat bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "qasoskor": "💀 • QASOSKOR •\n\nSiz Qasoskor bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "buqalamun": "🦎 • BUQALAMUN •\n\nSiz Buqalamun bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "kuzatuvchi": "🕵️ • KUZATUVCHI •\n\nSiz Kuzatuvchi bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "bodyguard": "🛡️ • BODYGUARD •\n\nSiz Bodyguard bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "sehrgar": "🧙 • SEHRGAR •\n\nSiz Sehrgar bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "jurnalist": "📰 • JURNALIST •\n\nSiz Jurnalist bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "kimyogar": "🔬 • KIMYOGAR •\n\nSiz Kimyogar bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "minyor": "💣 • MINYOR •\n\nSiz Minyor bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "koldun": "⚡ • KOLDUN •\n\nSiz Koldun bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "agent": "🕶️ • MAXFIY AGENT •\n\nSiz Maxfiy agent bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "arvoh": "👻 • ARVOH •\n\nSiz Arvoh bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "joker": "🤡 • JOKER •\n\nSiz Joker bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    "vampir": "🧛 • VAMPIR •\n\nSiz Vampir bo‘ldingiz.\n\n🌙 Tun boshlandi.",
}


# ============================================================
# ROLE KOMANDASI
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


async def roles(update, context):
    if not update.message:
        return

    await update.message.reply_text(
        "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
        "Kerakli rolni tanlang:",
        reply_markup=get_roles_buttons(),
    )


async def role_button(update, context):
    query = update.callback_query

    role_key = query.data.replace("role_", "", 1)

    role_name = next(
        (
            name
            for name, key in ROLES
            if key == role_key
        ),
        None,
    )

    if role_name:
        await query.answer(
            f"{role_name}\n\n"
            "🎭 Mafia Noir o‘yinidagi maxsus rol.",
            show_alert=True,
        )
    else:
        await query.answer(
            "❌ Rol topilmadi.",
            show_alert=True,
        )


# ============================================================
# O'YIN RO'YXATI
# ============================================================

def get_game_text(players):
    if not players:
        return "🖤 O‘yin ro‘yxatdan o‘tishi boshlandi."

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
                "🎮 Ro‘yxatdan o‘tish",
                url=f"https://t.me/{BOT_USERNAME}?start=join_{game_key}",
            )
        ]
    ])


async def gamecreate(update, context):
    if not update.message:
        return

    if update.effective_chat.type not in (
        "group",
        "supergroup",
    ):
        return

    message = await update.message.reply_text(
        "🖤 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        "🎮 O‘yin ro‘yxatdan o‘tishi boshlandi.\n\n"
        "Quyidagi tugma orqali o‘yinga qo‘shiling."
    )

    game_key = get_game_key(
        update.effective_chat.id,
        message.message_id,
    )

    ACTIVE_GAMES[game_key] = {
        "chat_id": update.effective_chat.id,
        "message_id": message.message_id,
        "players": {},
        "roles": {},
        "started": False,
        "phase": "registration",
        "night_actions": {},
        "night_required": [],
        "night_done": [],
        "night_kills": [],
        "night_heals": [],
        "votes": {},
        "vote_message_id": None,
        "vote_confirmed": False,
        "last_killed": None,
    }

    await message.edit_text(
        "🖤 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        "🎮 O‘yin ro‘yxatdan o‘tishi boshlandi.\n\n"
        "👥 O‘yinchilar:\n"
        "Hali hech kim qo‘shilmadi.",
        reply_markup=get_join_button(
            update.effective_chat.id,
            message.message_id,
        ),
    )


async def register_game_player(update, context):
    if not update.message:
        return

    if not context.args:
        return

    payload = context.args[0]

    if not payload.startswith("join_"):
        return

    game_key = payload[5:]
    game = ACTIVE_GAMES.get(game_key)

    if not game:
        await update.message.reply_text(
            "❌ Bu o‘yin mavjud emas yoki yopilgan."
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
            "⚠️ Siz allaqachon o‘yindasiz."
        )
        return

    if len(game["players"]) >= 25:
        await update.message.reply_text(
            "❌ O‘yinchilar soni 25 taga yetdi."
        )
        return

    game["players"][user_id] = name

    players = list(game["players"].values())

    try:
        await context.bot.edit_message_text(
            chat_id=game["chat_id"],
            message_id=game["message_id"],
            text=(
                "🖤 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
                "🎮 O‘yin ro‘yxatdan o‘tishi boshlandi.\n\n"
                f"👥 O‘yinchilar: {len(players)}/25\n\n"
                f"{get_game_text(players)}"
            ),
            reply_markup=get_join_button(
                game["chat_id"],
                game["message_id"],
            ),
        )
    except Exception:
        pass

    await update.message.reply_text(
        "✅ O‘yinga muvaffaqiyatli qo‘shildingiz!"
    )


# ============================================================
# ENG SO'NGGI O'YIN
# ============================================================

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


# ============================================================
# TUN
# ============================================================

def alive_players(game):
    return {
        uid: data
        for uid, data in game["roles"].items()
        if data.get("alive")
    }


def get_alive_target_buttons(game, prefix):
    buttons = []

    for uid, data in alive_players(game).items():
        buttons.append([
            InlineKeyboardButton(
                f"👤 {data['name']}",
                callback_data=f"{prefix}{uid}",
            )
        ])

    return InlineKeyboardMarkup(buttons)


def get_night_role_keyboard(role, game):
    if role in (
        "don",
        "qotil",
        "doktor",
        "bodyguard",
    ):
        if role == "don":
            prefix = "night_don_target_"
        elif role == "qotil":
            prefix = "night_killer_target_"
        elif role == "doktor":
            prefix = "night_heal_target_"
        else:
            prefix = "night_guard_target_"

        return get_alive_target_buttons(
            game,
            prefix,
        )

    if role == "komissar":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔎 Tekshirish",
                    callback_data="night_mode_check",
                ),
                InlineKeyboardButton(
                    "🔫 O‘ldirish",
                    callback_data="night_mode_kill",
                ),
            ]
        ])

    return None


def get_night_text(role_key):
    messages = {
        "don": (
            "🎩 • DON •\n\n"
            "🌙 Tun boshlandi.\n"
            "Bugungi nishonni tanlang."
        ),
        "mafia": (
            "🥷 • MAFIA •\n\n"
            "🌙 Tun boshlandi.\n"
            "Mafiya harakatini kuting."
        ),
        "qotil": (
            "🔪 • QOTIL •\n\n"
            "🌙 Tun boshlandi.\n"
            "Kimni yo‘q qilmoqchisiz?"
        ),
        "komissar": (
            "👮 • KOMISSAR •\n\n"
            "🌙 Tun boshlandi.\n"
            "Harakatni tanlang."
        ),
        "doktor": (
            "👨‍⚕️ • DOKTOR •\n\n"
            "🌙 Tun boshlandi.\n"
            "Kimni qutqarasiz?"
        ),
        "bodyguard": (
            "🛡️ • BODYGUARD •\n\n"
            "🌙 Tun boshlandi.\n"
            "Kimni himoya qilasiz?"
        ),
    }

    return messages.get(
        role_key,
        "🌙 • TUN •\n\n"
        "Tun boshlandi.\n"
        "Hozircha hech qanday harakat qilishingiz shart emas.",
    )


async def send_role_to_player(
    context,
    player_id,
    role_data,
    game,
):
    role_key = role_data["role_key"]

    text = ROLE_MESSAGES.get(
        role_key,
        f"🎭 Siz {role_data['role_name']} bo‘ldingiz.\n\n"
        "🌙 Tun boshlandi.",
    )

    keyboard = get_night_role_keyboard(
        role_key,
        game,
    )

    if keyboard:
        text = get_night_text(role_key)

    try:
        await context.bot.send_message(
            chat_id=int(player_id),
            text=text,
            reply_markup=keyboard,
        )
        return True
    except Exception:
        return False


def prepare_night(game):
    game["phase"] = "night"
    game["night_actions"] = {}
    game["night_done"] = []
    game["night_kills"] = []
    game["night_heals"] = []
    game["night_required"] = []

    for uid, data in alive_players(game).items():
        role = data["role_key"]

        if role in (
            "don",
            "qotil",
            "doktor",
            "bodyguard",
        ):
            game["night_required"].append(uid)


async def start_night(game, context):
    prepare_night(game)

    try:
        await context.bot.send_message(
            chat_id=game["chat_id"],
            text=(
                "🌙 • 𝑻𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
                "🌃 Shahar uyquga ketdi.\n\n"
                "Har bir o‘yinchi shaxsiy chatidagi "
                "o‘z qobiliyatidan foydalanadi.\n\n"
                "⏳ Tungi harakatlar boshlandi..."
            ),
        )
    except Exception:
        pass

    for uid, role_data in game["roles"].items():
        if not role_data.get("alive"):
            continue

        await send_role_to_player(
            context,
            uid,
            role_data,
            game,
        )

    if not game["night_required"]:
        await finish_night(game, context)


# ============================================================
# TUNGI HARAKAT
# ============================================================

async def night_target(update, context):
    query = update.callback_query

    data = query.data

    if "_" not in data:
        await query.answer()
        return

    parts = data.split("_")
    target_id = parts[-1]

    user_id = str(query.from_user.id)

    game = find_game_by_player(
        query.from_user.id,
    )

    if not game:
        await query.answer(
            "❌ Faol o‘yin topilmadi.",
            show_alert=True,
        )
        return

    if game["phase"] != "night":
        await query.answer(
            "❌ Hozir tun emas.",
            show_alert=True,
        )
        return

    player = game["roles"].get(user_id)

    if not player or not player.get("alive"):
        await query.answer(
            "❌ Siz o‘yinda faol emassiz.",
            show_alert=True,
        )
        return

    target = game["roles"].get(target_id)

    if not target or not target.get("alive"):
        await query.answer(
            "❌ Bu o‘yinchi faol emas.",
            show_alert=True,
        )
        return

    role = player["role_key"]

    if role == "don":
        game["night_kills"] = [
            target_id
        ]

    elif role == "qotil":
        game["night_kills"].append(target_id)

    elif role == "doktor":
        game["night_heals"] = [
            target_id
        ]

    elif role == "bodyguard":
        game["night_actions"][user_id] = {
            "type": "guard",
            "target": target_id,
        }

    else:
        await query.answer()
        return

    if user_id not in game["night_done"]:
        game["night_done"].append(user_id)

    await query.answer(
        "✅ Tanlov qabul qilindi!"
    )

    try:
        await query.message.edit_text(
            "🌙 Tungi harakatingiz qabul qilindi.\n\n"
            f"🎯 Tanlangan: {target['name']}\n\n"
            "⏳ Boshqa tungi harakatlar kutilmoqda..."
        )
    except Exception:
        pass

    await check_night_finished(game, context)


async def check_night_finished(game, context):
    required = set(game.get("night_required", []))
    done = set(game.get("night_done", []))

    if required.issubset(done):
        await finish_night(game, context)


async def finish_night(game, context):
    if game["phase"] != "night":
        return

    game["phase"] = "day"

    alive = alive_players(game)

    protected = set(game.get("night_heals", []))

    killed = None

    for target_id in game.get("night_kills", []):
        if target_id in protected:
            continue

        target = game["roles"].get(target_id)

        if target and target.get("alive"):
            killed = target_id
            break

    if killed:
        game["roles"][killed]["alive"] = False
        game["last_killed"] = killed

        target_name = game["roles"][killed]["name"]
        role_name = game["roles"][killed]["role_name"]

        text = (
            "☀️ • 𝑲𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
            f"Bu tun {target_name} uchun oxirgi tun edi.\n\n"
            f"🕯 U tungi hujum qurboniga aylandi.\n"
            f"🎭 U {role_name} edi."
        )
    else:
        text = (
            "☀️ • 𝑲𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
            "🌃 Tun ortda qoldi.\n\n"
            "Bu tun hech kim o‘yindan chiqarilmadi."
        )

    try:
        await context.bot.send_message(
            chat_id=game["chat_id"],
            text=text,
        )
    except Exception:
        pass

    if await check_game_end(game, context):
        return

    await start_day_vote(game, context)


# ============================================================
# KUNGI OVOZ
# ============================================================

def get_vote_group_keyboard(game):
    buttons = []

    for uid, data in alive_players(game).items():
        buttons.append([
            InlineKeyboardButton(
                f"🗳 {data['name']}",
                url=(
                    f"https://t.me/{BOT_USERNAME}"
                    f"?start=vote_{get_game_key(game['chat_id'], game['message_id'])}"
                ),
            )
        ])

    return InlineKeyboardMarkup(buttons)


async def start_day_vote(game, context):
    game["phase"] = "voting"
    game["votes"] = {}

    game_key = get_game_key(
        game["chat_id"],
        game["message_id"],
    )

    try:
        message = await context.bot.send_message(
            chat_id=game["chat_id"],
            text=(
                "⚖️ • 𝑶𝑽𝑶𝒁 𝑩𝑬𝑹𝑰𝑺𝑯 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
                "Shahar qaror kutmoqda.\n"
                "O‘yindan chiqarilishi kerak bo‘lgan "
                "o‘yinchini tanlang."
            ),
        )

        game["vote_message_id"] = message.message_id

        await message.edit_text(
            "⚖️ • 𝑶𝑽𝑶𝒁 𝑩𝑬𝑹𝑰𝑺𝑯 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
            "Shahar qaror kutmoqda.\n\n"
            "👇 Ovoz berish uchun tugmani bosing.\n"
            "Bot sizni shaxsiy chatga olib o‘tadi.",
            reply_markup=get_vote_group_keyboard(game),
        )

    except Exception:
        pass


def find_game_by_player(user_id):
    uid = str(user_id)

    for game in ACTIVE_GAMES.values():
        if uid in game.get("roles", {}):
            return game

    return None


def get_vote_buttons(game):
    keyboard = []

    for uid, data in alive_players(game).items():
        keyboard.append([
            InlineKeyboardButton(
                f"🗳 {data['name']}",
                callback_data=f"vote_target_{uid}",
            )
        ])

    return InlineKeyboardMarkup(keyboard)


async def private_vote(update, context):
    if not update.message:
        return

    payload = context.args[0]

    if not payload.startswith("vote_"):
        return

    game_key = payload[5:]
    game = ACTIVE_GAMES.get(game_key)

    if not game:
        await update.message.reply_text(
            "❌ Bu ovoz berish mavjud emas."
        )
        return

    user_id = str(update.effective_user.id)

    player = game["roles"].get(user_id)

    if not player or not player.get("alive"):
        await update.message.reply_text(
            "❌ Siz bu o‘yinda faol emassiz."
        )
        return

    if game["phase"] != "voting":
        await update.message.reply_text(
            "❌ Hozir ovoz berish vaqti emas."
        )
        return

    await update.message.reply_text(
        "⚖️ • 𝑶𝑽𝑶𝒁 𝑩𝑬𝑹𝑰𝑺𝑯 •\n\n"
        "Kim o‘yindan chiqarilishi kerak?",
        reply_markup=get_vote_buttons(game),
    )


async def vote_target(update, context):
    query = update.callback_query

    if not query.data.startswith("vote_target_"):
        return

    game = find_game_by_player(
        query.from_user.id,
    )

    if not game or game["phase"] != "voting":
        await query.answer(
            "❌ Ovoz berish faol emas.",
            show_alert=True,
        )
        return

    voter_id = str(query.from_user.id)
    target_id = query.data.replace(
        "vote_target_",
        "",
        1,
    )

    if voter_id == target_id:
        await query.answer(
            "❌ O‘zingizga ovoz bera olmaysiz.",
            show_alert=True,
        )
        return

    target = game["roles"].get(target_id)

    if not target or not target.get("alive"):
        await query.answer(
            "❌ Bu o‘yinchi faol emas.",
            show_alert=True,
        )
        return

    game["votes"][voter_id] = target_id

    await query.answer(
        "✅ Ovozingiz qabul qilindi!"
    )

    try:
        await query.message.edit_text(
            "⚖️ Ovoz qabul qilindi.\n\n"
            f"🎯 Siz {target['name']} ga ovoz berdingiz.\n\n"
            "Guruhdagi natija ovozlar yakunlangach ko‘rsatiladi."
        )
    except Exception:
        pass

    await check_votes_finished(game, context)


async def check_votes_finished(game, context):
    alive = alive_players(game)

    if len(game["votes"]) < len(alive):
        return

    await finish_voting(game, context)


async def finish_voting(game, context):
    if game["phase"] != "voting":
        return

    game["phase"] = "vote_result"

    counts = {}

    for target_id in game["votes"].values():
        counts[target_id] = counts.get(target_id, 0) + 1

    if not counts:
        return

    max_votes = max(counts.values())

    winners = [
        uid
        for uid, count in counts.items()
        if count == max_votes
    ]

    if len(winners) != 1:
        names = [
            game["roles"][uid]["name"]
            for uid in winners
        ]

        try:
            await context.bot.send_message(
                chat_id=game["chat_id"],
                text=(
                    "⚖️ • 𝑶𝑽𝑶𝒁 𝑵𝑨𝑻𝑰𝑱𝑨𝑺𝑰 •\n\n"
                    "Ovozlar teng bo‘ldi.\n\n"
                    f"👥 {', '.join(names)}\n\n"
                    "Hukm chiqarilmadi."
                ),
            )
        except Exception:
            pass

        await start_night(game, context)
        return

    target_id = winners[0]
    target = game["roles"][target_id]

    red = counts.get(target_id, 0)
    green = len(game["votes"]) - red

    text = (
        "⚖️ • 𝑯𝑼𝑲𝑴 𝑻𝑨𝑺𝑫𝑰𝑸𝑳𝑨𝑺𝑯 •\n\n"
        f"👤 {target['name']}\n\n"
        f"🔴 {red}     🟢 {green}\n\n"
        f"Rostan ham {target['name']}ni "
        "osmoqchimisiz?"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"🔴 {red}",
                callback_data=f"execute_yes_{target_id}",
            ),
            InlineKeyboardButton(
                f"🟢 {green}",
                callback_data=f"execute_no_{target_id}",
            ),
        ]
    ])

    try:
        await context.bot.send_message(
            chat_id=game["chat_id"],
            text=text,
            reply_markup=keyboard,
        )
    except Exception:
        pass


# ============================================================
# HUKM
# ============================================================

async def execute_vote(update, context):
    query = update.callback_query

    parts = query.data.split("_")

    if len(parts) != 3:
        await query.answer()
        return

    decision = parts[1]
    target_id = parts[2]

    game = None

    for item in ACTIVE_GAMES.values():
        if item.get("chat_id") == query.message.chat_id:
            if item.get("phase") == "vote_result":
                game = item
                break

    if not game:
        await query.answer(
            "❌ Hukm allaqachon yakunlangan.",
            show_alert=True,
        )
        return

    target = game["roles"].get(target_id)

    if not target or not target.get("alive"):
        await query.answer(
            "❌ O‘yinchi allaqachon chiqarilgan.",
            show_alert=True,
        )
        return

    if decision == "no":
        await query.answer(
            "Hukm bekor qilindi."
        )

        try:
            await query.message.edit_text(
                "⚖️ • 𝑯𝑼𝑲𝑴 •\n\n"
                f"👤 {target['name']} chiqarilmadi.\n\n"
                "🌙 Keyingi tun boshlanadi..."
            )
        except Exception:
            pass

        await start_night(game, context)
        return

    await query.answer(
        "Hukm tasdiqlandi."
    )

    target["alive"] = False

    role_name = target["role_name"]
    target_name = target["name"]

    try:
        await query.message.edit_text(
            "⚖️ • 𝑯𝑼𝑲𝑴 𝑰𝑱𝑹𝑶 𝑬𝑻𝑰𝑳𝑫𝑰 •\n\n"
            f"👤 {target_name} o‘yindan chetlatildi.\n\n"
            f"🎭 U {role_name} edi.\n\n"
            "━━━━━━━━━━━━━━\n"
            "⚔️ Hukm ijro etildi."
        )
    except Exception:
        pass

    game["last_killed"] = target_id

    await update_player_stats_after_death(
        game,
        target_id,
    )

    if await check_game_end(game, context):
        return

    await start_night(game, context)


async def update_player_stats_after_death(game, target_id):
    data = load_data()

    for uid in game["roles"]:
        if uid not in data:
            data[uid] = get_default_user(int(uid))

        data[uid]["games"] = data[uid].get("games", 0)

    save_data(data)


# ============================================================
# O'YIN YAKUNI
# ============================================================

def get_team(role_key):
    mafia_roles = {
        "don",
        "mafia",
        "qotil",
        "aferist",
    }

    if role_key in mafia_roles:
        return "mafia"

    if role_key == "vampir":
        return "vampir"

    return "town"


async def check_game_end(game, context):
    alive = alive_players(game)

    mafia = sum(
        1
        for data in alive.values()
        if get_team(data["role_key"]) == "mafia"
    )

    town = sum(
        1
        for data in alive.values()
        if get_team(data["role_key"]) == "town"
    )

    vampir = sum(
        1
        for data in alive.values()
        if get_team(data["role_key"]) == "vampir"
    )

    winner = None

    if mafia == 0 and vampir == 0:
        winner = "👥 Tinchliksevarlar"
    elif mafia >= town + vampir:
        winner = "🥷 Mafia"
    elif vampir > 0 and vampir >= mafia + town:
        winner = "🧛 Vampir"

    if not winner:
        return False

    game["phase"] = "finished"

    for uid, data in game["roles"].items():
        user_data, user = get_user_data(int(uid))

        user["games"] = user.get("games", 0) + 1

        if (
            winner == "🥷 Mafia"
            and get_team(data["role_key"]) == "mafia"
        ):
            user["wins"] = user.get("wins", 0) + 1

        elif (
            winner == "👥 Tinchliksevarlar"
            and get_team(data["role_key"]) == "town"
        ):
            user["wins"] = user.get("wins", 0) + 1

        elif (
            winner == "🧛 Vampir"
            and get_team(data["role_key"]) == "vampir"
        ):
            user["wins"] = user.get("wins", 0) + 1

        save_data(user_data)

    try:
        await context.bot.send_message(
            chat_id=game["chat_id"],
            text=(
                "🏆 • 𝑶‘𝒀𝑰𝑵 𝑻𝑼𝑮𝑨𝑫𝑰 •\n\n"
                f"👑 G‘oliblar: {winner}\n\n"
                "🖤 Mafia Noir"
            ),
        )
    except Exception:
        pass

    return True


# ============================================================
# GAMSTART
# ============================================================

async def gamestart(update, context):
    if not update.message:
        return

    if update.effective_chat.type not in (
        "group",
        "supergroup",
    ):
        return

    result = get_latest_game(
        update.effective_chat.id
    )

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

    if len(players) < 3:
        await update.message.reply_text(
            "❌ O‘yinni boshlash uchun kamida 3 o‘yinchi kerak."
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

    selected_roles = ROLES[:len(players)]
    random.shuffle(selected_roles)

    player_items = list(players.items())

    for index, (player_id, player_name) in enumerate(
        player_items
    ):
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
            text=(
                "🌙 • 𝑻𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
                "🌃 Shahar uyquga ketdi.\n\n"
                "🎭 Rollar shaxsiy chatga yuborildi.\n"
                "⏳ Tungi harakatlar boshlandi..."
            ),
        )
    except Exception:
        pass

    await start_night(game, context)

    await update.message.reply_text(
        f"🌙 O‘yin boshlandi.\n"
        f"👥 O‘yinchilar: {len(players)}\n"
        "🎭 Rollar tarqatildi."
    )


# ============================================================
# TUNGI REJIM CALLBACKLARI
# ============================================================

async def night_mode(update, context):
    query = update.callback_query

    game = find_game_by_player(
        query.from_user.id,
    )

    if not game or game["phase"] != "night":
        await query.answer(
            "❌ Hozir bu harakat mumkin emas.",
            show_alert=True,
        )
        return

    role_data = game["roles"].get(
        str(query.from_user.id)
    )

    if not role_data:
        await query.answer()
        return

    if role_data["role_key"] != "komissar":
        await query.answer(
            "❌ Siz Komissar emassiz.",
            show_alert=True,
        )
        return

    if query.data == "night_mode_check":
        keyboard = get_alive_target_buttons(
            game,
            "check_target_",
        )

        await query.answer()

        await query.message.edit_text(
            "🔎 • TEKSHIRISH •\n\n"
            "Kimning rolini tekshirmoqchisiz?",
            reply_markup=keyboard,
        )

    elif query.data == "night_mode_kill":
        keyboard = get_alive_target_buttons(
            game,
            "commissioner_kill_target_",
        )

        await query.answer()

        await query.message.edit_text(
            "🔫 • O‘LDIRISH •\n\n"
            "Kimni yo‘q qilmoqchisiz?",
            reply_markup=keyboard,
        )


async def commissioner_action(update, context):
    query = update.callback_query

    game = find_game_by_player(
        query.from_user.id,
    )

    if not game or game["phase"] != "night":
        await query.answer(
            "❌ Hozir tun emas.",
            show_alert=True,
        )
        return

    target_id = query.data.split("_")[-1]
    target = game["roles"].get(target_id)

    if not target or not target.get("alive"):
        await query.answer(
            "❌ O‘yinchi faol emas.",
            show_alert=True,
        )
        return

    if query.data.startswith("check_target_"):
        role_name = target["role_name"]

        await query.answer(
            f"{target['name']} — {role_name}",
            show_alert=True,
        )

    elif query.data.startswith(
        "commissioner_kill_target_"
    ):
        game["night_kills"].append(target_id)

        uid = str(query.from_user.id)

        if uid not in game["night_done"]:
            game["night_done"].append(uid)

        await query.answer(
            "🔫 Nishon tanlandi."
        )

        await query.message.edit_text(
            f"🔫 Nishon: {target['name']}\n\n"
            "✅ Tungi harakat qabul qilindi."
        )

        await check_night_finished(
            game,
            context,
        )


# ============================================================
# CALLBACK HANDLER
# ============================================================

async def callback_handler(update, context):
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

    elif data.startswith("night_don_target_"):
        await night_target(update, context)

    elif data.startswith("night_killer_target_"):
        await night_target(update, context)

    elif data.startswith("night_heal_target_"):
        await night_target(update, context)

    elif data.startswith("night_guard_target_"):
        await night_target(update, context)

    elif data in (
        "night_mode_check",
        "night_mode_kill",
    ):
        await night_mode(update, context)

    elif data.startswith("check_target_"):
        await commissioner_action(update, context)

    elif data.startswith("commissioner_kill_target_"):
        await commissioner_action(update, context)

    elif data.startswith("vote_target_"):
        await vote_target(update, context)

    elif data.startswith("execute_yes_"):
        await execute_vote(update, context)

    elif data.startswith("execute_no_"):
        await execute_vote(update, context)

    else:
        await query.answer()


# ============================================================
# O'YINNI TO'XTATISH / CHIQISH
# ============================================================

async def gamestop(update, context):
    if not update.message:
        return

    chat_id = update.effective_chat.id

    found = None

    for key, game in ACTIVE_GAMES.items():
        if game.get("chat_id") == chat_id:
            found = key
            break

    if not found:
        await update.message.reply_text(
            "❌ Faol o‘yin topilmadi."
        )
        return

    del ACTIVE_GAMES[found]

    await update.message.reply_text(
        "🛑 • O‘YIN TO‘XTATILDI •\n\n"
        "Mafia Noir o‘yini to‘xtatildi."
    )


async def gameexit(update, context):
    await update.message.reply_text(
        "ℹ️ O‘yindan chiqish funksiyasi "
        "keyingi bosqichda to‘liq ulanadi."
    )


async def paragame(update, context):
    await update.message.reply_text(
        "💰 Para o‘yini hozircha mavjud emas."
    )


# ============================================================
# COMMANDLAR
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


async def inactive_group_command(update, context):
    return


async def post_init(application):
    await application.bot.set_my_commands(
        GROUP_VISIBLE_COMMANDS,
        scope=BotCommandScopeAllGroupChats(),
    )


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

    # START
    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    # PROFILE
    application.add_handler(
        CommandHandler(
            "profile",
            profile,
        )
    )

    # ROLES
    application.add_handler(
        CommandHandler(
            "roles",
            roles,
        )
    )

    # O'YIN
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
            gamestop,
        )
    )

    application.add_handler(
        CommandHandler(
            "gameexit",
            gameexit,
        )
    )

    application.add_handler(
        CommandHandler(
            "paragame",
            paragame,
        )
    )

    # YASHIRIN COMMANDLAR
    for command in GROUP_HIDDEN_COMMANDS:
        application.add_handler(
            CommandHandler(
                command,
                inactive_group_command,
            )
        )

    # CALLBACK
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
