import os
import json
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
        "🌍 Tilni tanlang:",
        reply_markup=get_language_buttons()
    )


async def language_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "🖤 Salom! Xush kelibsiz!\n\n"
        "🌃 Men Mafia Noir botiman. Mafia o‘ynash uchun "
        "meni guruhingizga qo‘shing.",
        reply_markup=get_main_buttons()
    )


# =========================================================
# PROFILE
# =========================================================

def get_profile_text(user):
    _, u = get_user_data(user.id)

    vip_line = "\n👑 VIP: Ha" if u["vip"] else ""

    return (
        " • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {user.first_name or 'Noma’lum'}\n"
        f"🆔 ID: {user.id}{vip_line}\n\n"
        f"💵 Dollar: {u['dollar']}\n"
        f"💎 Olmos: {u['diamond']}\n\n"
        f"🛡 Qora qalqon: {u['items']['shield']}\n"
        f"📜 Soxta hujjat: {u['items']['document']}\n"
        f"⚖️ Afv tamg‘asi: {u['items']['forgiveness']}\n"
        f"🩸 Qotil niqobi: {u['items']['killer_mask']}\n"
        f"🔫 Noir miltig‘i: {u['items']['gun']}\n"
        f"💊 Qora dori: {u['items']['black_medicine']}\n"
        f"🧪 Verbena ekstrakti: {u['items']['verbena']}\n"
        f"🥷 Sirli niqob: {u['items']['mystery_mask']}\n"
        f"🛡️ Geroydan himoya: {u['items']['hero_protection']}\n\n"
        f"⚔️ Geroy: {'Bor' if u['hero'] > 0 else 'Yo‘q'}\n"
        f"🃏 Faol rol: {'Bor' if u['active_role'] > 0 else 'Yo‘q'}\n\n"
        "🎯 G‘alabalar: 0\n"
        "🎲 Barcha o‘yinlar: 0\n"
        "📊 G‘alaba foizi: 0"
    )


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💵 Dollar olish",
                callback_data="dollar_exchange"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Olmos olish",
                callback_data="diamond_buy"
            )
        ],
        [
            InlineKeyboardButton(
                "⚔️ Mening Geroyim",
                callback_data="hero"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Do‘kon",
                callback_data="shop"
            )
        ],
        [
            InlineKeyboardButton(
                "📖 Buyumlar haqida",
                callback_data="items_info"
            )
        ],
        [
            InlineKeyboardButton(
                "🔻",
                callback_data="item_control"
            )
        ],
    ])


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_profile_text(update.effective_user),
        reply_markup=get_profile_buttons()
    )


# =========================================================
# DOLLAR
# =========================================================

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

    for diamond, dollar in DOLLAR_PACKAGES:
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {diamond} → 💵 {dollar}",
                callback_data=f"exchange_{diamond}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def dollar_exchange(update, context):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Olmosni Dollarga almashtiring:",
        reply_markup=get_dollar_buttons()
    )


async def exchange_dollar(update, context):
    query = update.callback_query

    try:
        amount = int(query.data.split("_")[1])
    except (IndexError, ValueError):
        await query.answer(
            "❌ Xatolik",
            show_alert=True
        )
        return

    data, u = get_user_data(query.from_user.id)

    if query.from_user.id != OWNER_ID:
        if u["diamond"] < amount:
            await query.answer(
                "❌ Olmos yetarli emas",
                show_alert=True
            )
            return

        u["diamond"] -= amount

    u["dollar"] += amount * 600

    save_data(data)

    await query.answer(
        "✅ Savdo muvaffaqiyatli amalga oshirildi!"
    )

    await query.message.edit_text(
        get_profile_text(query.from_user),
        reply_markup=get_profile_buttons()
    )


# =========================================================
# OLMOS
# =========================================================

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
        keyboard.append([
            InlineKeyboardButton(
                f"💎 {amount} ta — {price:,} so‘m".replace(",", " "),
                url=f"https://t.me/{OWNER_USERNAME}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def diamond_buy(update, context):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "💎 • 𝑶𝒍𝒎𝒐𝒔 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Kerakli paketni tanlang:",
        reply_markup=get_diamond_buttons()
    )


# =========================================================
# DO‘KON
# =========================================================

def get_shop_buttons():
    keyboard = []

    for key, (name, price, currency) in ITEMS.items():
        emoji = "💵" if currency == "dollar" else "💎"

        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {emoji} {price}",
                callback_data=f"buy_{key}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def shop(update, context):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "Kerakli buyumni tanlang:",
        reply_markup=get_shop_buttons()
    )


async def buy_item(update, context):
    query = update.callback_query

    key = query.data.replace("buy_", "", 1)

    if key not in ITEMS:
        await query.answer("❌ Xatolik")
        return

    name, price, currency = ITEMS[key]

    data, u = get_user_data(query.from_user.id)

    if query.from_user.id != OWNER_ID:
        if currency == "dollar":
            if u["dollar"] < price:
                await query.answer(
                    "❌ Mablag‘ yetarli emas",
                    show_alert=True
                )
                return

            u["dollar"] -= price

        else:
            if u["diamond"] < price:
                await query.answer(
                    "❌ Mablag‘ yetarli emas",
                    show_alert=True
                )
                return

            u["diamond"] -= price

    if key == "hero":
        u["hero"] += 1

    elif key == "active_role":
        u["active_role"] += 1

    else:
        u["items"][key] += 1

    save_data(data)

    await query.answer(
        "✅ Xarid muvaffaqiyatli amalga oshirildi!"
    )

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "✅ Xarid muvaffaqiyatli amalga oshirildi.\n\n"
        "Yana buyum tanlang:",
        reply_markup=get_shop_buttons()
    )


# =========================================================
# BUYUMLAR HAQIDA
# =========================================================

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
                    callback_data="profile"
                )
            ]
        ])
    )


# =========================================================
# ON / OFF
# =========================================================

def get_control_buttons(u):
    keyboard = []

    for key, (name, _, _) in ITEMS.items():

        if key in ("hero", "active_role"):
            continue

        count = u["items"][key]
        active = u["active_items"][key]

        status = "🟢 ON" if active else "⚪ OFF"

        keyboard.append([
            InlineKeyboardButton(
                f"{name} — {count}",
                callback_data=f"noop_{key}"
            )
        ])

        keyboard.append([
            InlineKeyboardButton(
                status,
                callback_data=f"toggle_{key}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Orqaga",
            callback_data="profile"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def item_control(update, context):
    query = update.callback_query
    await query.answer()

    _, u = get_user_data(query.from_user.id)

    await query.message.edit_text(
        "🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\n"
        "Buyumni ON yoki OFF holatiga o‘tkazing.",
        reply_markup=get_control_buttons(u)
    )


async def toggle_item(update, context):
    query = update.callback_query

    key = query.data.replace("toggle_", "", 1)

    if key not in ITEMS:
        await query.answer("❌ Xatolik")
        return

    data, u = get_user_data(query.from_user.id)

    if key not in u["items"]:
        await query.answer("❌ Xatolik")
        return

    if u["items"][key] <= 0:
        await query.answer(
            "❌ Bu buyum sizda mavjud emas",
            show_alert=True
        )
        return

    u["active_items"][key] = not u["active_items"][key]

    save_data(data)

    await query.answer()

    await query.message.edit_text(
        "🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\n"
        "Buyumni ON yoki OFF holatiga o‘tkazing.",
        reply_markup=get_control_buttons(u)
    )


# =========================================================
# HERO
# =========================================================

HERO_LEVELS = [
    ("🥉 I — Bronze", 0, "⚔️ Hujum"),
    ("🥈 II — Silver", 100, "🛡️ Himoya"),
    ("🥇 III — Gold", 300, "🪖 Zirh"),
    ("💎 IV — Diamond", 700, "⚡ Maxsus qobiliyat"),
    ("🖤 V — Noir", 1500, "👑 Maxsus kuch"),
]


def get_hero_level(xp):
    level = 1

    for index, level_data in enumerate(HERO_LEVELS):
        required_xp = level_data[1]

        if xp >= required_xp:
            level = index + 1

    return level


def get_hero_progress(xp):
    level = get_hero_level(xp)

    current = HERO_LEVELS[level - 1]

    current_name = current[0]
    current_xp = current[1]
    current_power = current[2]

    if level >= 5:
        next_xp = None
    else:
        next_xp = HERO_LEVELS[level][1]

    return current_name, current_xp, current_power, next_xp


def get_hero_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Darajalar",
                callback_data="hero_levels"
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ Qobiliyatlar",
                callback_data="hero_skills"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Orqaga",
                callback_data="profile"
            )
        ],
    ])


async def hero(update, context):
    query = update.callback_query
    await query.answer()

    _, u = get_user_data(query.from_user.id)

    if u["hero"] <= 0:
        text = (
            "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
            "❌ Sizda Geroy mavjud emas.\n\n"
            "💎 Do‘kondan Geroy sotib olishingiz mumkin."
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💰 Do‘konga",
                    callback_data="shop"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Orqaga",
                    callback_data="profile"
                )
            ],
        ])

        await query.message.edit_text(
            text,
            reply_markup=keyboard
        )

        return

    xp = u.get("hero_xp", 0)
    wins = u.get("hero_wins", 0)

    level = get_hero_level(xp)

    level_name, required_xp, power, next_xp = get_hero_progress(xp)

    if next_xp is None:
        xp_line = f"⭐ XP: {xp} — MAX"
        next_line = "👑 Maksimal daraja ochilgan"
    else:
        xp_line = f"⭐ XP: {xp} / {next_xp}"
        next_line = f"📈 Keyingi daraja: {next_xp} XP"

    if level >= 2:
        shield_status = "🛡️ Himoya: Faol"
    else:
        shield_status = "🛡️ Himoya: Hali ochilmagan"

    text = (
        "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
        f"👤 Egasi: {query.from_user.first_name or 'Noma’lum'}\n\n"
        f"⚔️ Geroylar: {u['hero']} ta\n"
        f"🏆 Daraja: {level_name}\n"
        f"{xp_line}\n\n"
        f"🎯 G‘alabalar: {wins}\n"
        f"{shield_status}\n"
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
        reply_markup=get_hero_buttons()
    )


async def hero_levels(update, context):
    query = update.callback_query
    await query.answer()

    _, u = get_user_data(query.from_user.id)

    if u["hero"] <= 0:
        await query.answer(
            "❌ Sizda Geroy yo‘q",
            show_alert=True
        )
        return

    xp = u.get("hero_xp", 0)
    current_level = get_hero_level(xp)

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
                    callback_data="hero"
                )
            ]
        ])
    )


async def hero_skills(update, context):
    query = update.callback_query
    await query.answer()

    _, u = get_user_data(query.from_user.id)

    if u["hero"] <= 0:
        await query.answer(
            "❌ Sizda Geroy yo‘q",
            show_alert=True
        )
        return

    xp = u.get("hero_xp", 0)
    level = get_hero_level(xp)

    skills = []

    if level >= 1:
        skills.append("⚔️ I — Hujum")

    if level >= 2:
        skills.append("🛡️ II — Himoya")

    if level >= 3:
        skills.append("🪖 III — Zirh")

    if level >= 4:
        skills.append("⚡ IV — Maxsus qobiliyat")

    if level >= 5:
        skills.append("👑 V — Maxsus kuch")

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
                    callback_data="hero"
                )
            ]
        ])
    )


# =========================================================
# ROLES
# =========================================================

ROLES = [
    ("🎩 Don", "role_don"),
    ("🥷 Mafia", "role_mafia"),
    ("🎭 Aferist", "role_aferist"),
    ("🔪 Qotil", "role_qotil"),
    ("👮 Komissar", "role_komissar"),
    ("👨‍⚕️ Doktor", "role_doktor"),
    ("👮‍♂️ Serjant", "role_serjant"),
    ("🎖️ Kapitan", "role_kapitan"),
    ("👤 Fuqaro", "role_fuqaro"),
    ("👣 Daydi", "role_daydi"),
    ("⚖️ Sudya", "role_sudya"),
    ("👨‍⚖️ Advokat", "role_advokat"),
    ("💀 Qasoskor", "role_qasoskor"),
    ("🦎 Buqalamun", "role_buqalamun"),
    ("🕵️ Kuzatuvchi", "role_kuzatuvchi"),
    ("🛡️ Bodyguard", "role_bodyguard"),
    ("🧙 Sehrgar", "role_sehrgar"),
    ("📰 Jurnalist", "role_jurnalist"),
    ("🔬 Kimyogar", "role_kimyogar"),
    ("💣 Minyor", "role_minyor"),
    ("⚡ Koldun", "role_koldun"),
    ("🕶️ Maxfiy agent", "role_agent"),
    ("👻 Arvoh", "role_arvoh"),
    ("🤡 Joker", "role_joker"),
    ("🧛 Vampir", "role_vampir"),
]


ROLE_DESCRIPTIONS = {
    "role_don":
        "🎩 DON\n\n"
        "Mafiya jamoasining boshlig‘i.\n\n"
        "🎯 Vazifasi: Mafiya bilan birga g‘alaba qozonish.",

    "role_mafia":
        "🥷 MAFIA\n\n"
        "Mafiya jamoasining asosiy a’zosi.\n\n"
        "🎯 Vazifasi: Tinchliksevarlarni yo‘q qilish.",

    "role_aferist":
        "🎭 AFERIST\n\n"
        "Aldov va hiylaga asoslangan mustaqil rol.\n\n"
        "🎯 Vazifasi: O‘z maqsadiga erishish.",

    "role_qotil":
        "🔪 QOTIL\n\n"
        "Mustaqil xavfli hujumchi.\n\n"
        "🎯 Vazifasi: Belgilangan nishonlarni yo‘q qilish.",

    "role_komissar":
        "👮 KOMISSAR\n\n"
        "Tinchliksevarlar tomonidagi tekshiruvchi.\n\n"
        "🎯 Vazifasi: Shubhali o‘yinchilarni aniqlash.",

    "role_doktor":
        "👨‍⚕️ DOKTOR\n\n"
        "O‘yinchilarni himoya qiluvchi rol.\n\n"
        "🎯 Vazifasi: Tunda bir o‘yinchini himoya qilish.",

    "role_serjant":
        "👮‍♂️ SERJANT\n\n"
        "Tartibni saqlashga yordam beruvchi rol.",

    "role_kapitan":
        "🎖️ KAPITAN\n\n"
        "Kuchli boshqaruv qobiliyatiga ega rol.",

    "role_fuqaro":
        "👤 FUQARO\n\n"
        "Oddiy tinchliksevar o‘yinchi.\n\n"
        "🎯 Vazifasi: Mafiyani aniqlash.",

    "role_daydi":
        "👣 DAYDI\n\n"
        "Mustaqil harakat qiluvchi sirli rol.",

    "role_sudya":
        "⚖️ SUDYA\n\n"
        "Sud va ovoz berishga ta’sir qiluvchi rol.",

    "role_advokat":
        "👨‍⚖️ ADVOKAT\n\n"
        "O‘yinchini himoya qilishga yordam beruvchi rol.",

    "role_qasoskor":
        "💀 QASOSKOR\n\n"
        "Qasos olish imkoniyatiga ega rol.",

    "role_buqalamun":
        "🦎 BUQALAMUN\n\n"
        "O‘zini boshqa rolga o‘xshatishi mumkin.",

    "role_kuzatuvchi":
        "🕵️ KUZATUVCHI\n\n"
        "O‘yinchilar harakatini kuzatuvchi rol.",

    "role_bodyguard":
        "🛡️ BODYGUARD\n\n"
        "Tanlangan o‘yinchini himoya qiladi.",

    "role_sehrgar":
        "🧙 SEHRGAR\n\n"
        "Maxsus sehrli qobiliyatlarga ega rol.",

    "role_jurnalist":
        "📰 JURNALIST\n\n"
        "Ma’lumot va sirlarni izlovchi rol.",

    "role_kimyogar":
        "🔬 KIMYOGAR\n\n"
        "Maxsus moddalar va ta’sirlardan foydalanadi.",

    "role_minyor":
        "💣 MINYOR\n\n"
        "Tuzoq va maxsus qobiliyatlarga ega rol.",

    "role_koldun":
        "⚡ KOLDUN\n\n"
        "Sirli kuchlardan foydalanadi.",

    "role_agent":
        "🕶️ MAXFIY AGENT\n\n"
        "Yashirin topshiriqlarni bajaruvchi rol.",

    "role_arvoh":
        "👻 ARVOH\n\n"
        "O‘yindan chiqqandan keyin ham maxsus imkoniyatlarga ega.",

    "role_joker":
        "🤡 JOKER\n\n"
        "O‘yinni chalkashtiruvchi mustaqil rol.",

    "role_vampir":
        "🧛 VAMPIR\n\n"
        "Tunda harakat qiluvchi maxsus rol.",
}


def get_roles_buttons():
    keyboard = []

    for i in range(0, len(ROLES), 2):
        row = [
            InlineKeyboardButton(
                ROLES[i][0],
                callback_data=ROLES[i][1]
            )
        ]

        if i + 1 < len(ROLES):
            row.append(
                InlineKeyboardButton(
                    ROLES[i + 1][0],
                    callback_data=ROLES[i + 1][1]
                )
            )

        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
        "Kerakli rolni tanlang:",
        reply_markup=get_roles_buttons()
    )


async def role_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    description = ROLE_DESCRIPTIONS.get(
        query.data,
        "❌ Bu rol haqida ma’lumot topilmadi."
    )

    await query.answer(
        description,
        show_alert=True
    )


# =========================================================
# GURUH KOMANDALARI
# =========================================================

# Bu komandalar hozircha ataylab HECH NIMA QILMAYDI.
# Keyinchalik har biriga alohida funksiya qo‘shamiz.


async def inactive_group_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    return


# =========================================================
# GURUHDA KO‘RINADIGAN KOMANDALAR
# =========================================================

GROUP_VISIBLE_COMMANDS = [
    BotCommand("gamecreate", "O‘yin yaratish"),
    BotCommand("gamestart", "O‘yinni boshlash"),
    BotCommand("gamestop", "O‘yinni to‘xtatish"),
    BotCommand("gameexit", "O‘yindan chiqish"),
    BotCommand("paragame", "Para o‘yini yaratish"),
]


# =========================================================
# GURUHDA KO‘RINMAYDIGAN KOMANDALAR
# =========================================================

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


# =========================================================
# KOMANDALARNI TELEGRAMGA O‘RNATISH
# =========================================================

async def post_init(application: Application):
    await application.bot.set_my_commands(
        GROUP_VISIBLE_COMMANDS,
        scope=BotCommandScopeAllGroupChats()
    )


# =========================================================
# CALLBACK
# =========================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    data = query.data

    if data.startswith("lang_"):
        await language_button(update, context)

    elif data == "profile":
        await query.answer()

        await query.message.edit_text(
            get_profile_text(query.from_user),
            reply_markup=get_profile_buttons()
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

    else:
        await query.answer()


# =========================================================
# MAIN
# =========================================================

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # -----------------------------------------------------
    # ASOSIY KOMANDALAR
    # -----------------------------------------------------

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("profile", profile)
    )

    app.add_handler(
        CommandHandler("roles", roles)
    )

    # -----------------------------------------------------
    # GURUHDA KO‘RINADIGAN KOMANDALAR
    # -----------------------------------------------------

    app.add_handler(
        CommandHandler("gamecreate", inactive_group_command)
    )

    app.add_handler(
        CommandHandler("gamestart", inactive_group_command)
    )

    app.add_handler(
        CommandHandler("gamestop", inactive_group_command)
    )

    app.add_handler(
        CommandHandler("gameexit", inactive_group_command)
    )

    app.add_handler(
        CommandHandler("paragame", inactive_group_command)
    )

    # -----------------------------------------------------
    # GURUHDA KO‘RINMAYDIGAN KOMANDALAR
    # -----------------------------------------------------

    for command in GROUP_HIDDEN_COMMANDS:
        app.add_handler(
            CommandHandler(command, inactive_group_command)
        )

    # -----------------------------------------------------
    # CALLBACK
    # -----------------------------------------------------

    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    # -----------------------------------------------------
    # BOTNI ISHLATISH
    # -----------------------------------------------------

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
