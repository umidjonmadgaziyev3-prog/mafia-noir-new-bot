import os
import json
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "dollar": 0,
            "diamond": 0,
            "hero": 0,
            "hero_level": 1,
            "hero_xp": 0,
            "hero_wins": 0,
            "hero_games": 0,
            "active_role": 0,
            "items": {},
            "active_items": {},
        }

    user = data[uid]

    user.setdefault("dollar", 0)
    user.setdefault("diamond", 0)
    user.setdefault("hero", 0)
    user.setdefault("hero_level", 1)
    user.setdefault("hero_xp", 0)
    user.setdefault("hero_wins", 0)
    user.setdefault("hero_games", 0)
    user.setdefault("active_role", 0)
    user.setdefault("items", {})
    user.setdefault("active_items", {})

    for key in ITEMS:
        if key not in ("hero", "active_role"):
            user["items"].setdefault(key, 0)
            user["active_items"].setdefault(key, False)

    save_data(data)
    return data, user


def is_owner(user_id):
    return user_id == OWNER_ID


# =========================
# START
# =========================

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


# =========================
# PROFILE
# =========================

def get_profile_text(user):
    _, u = get_user_data(user.id)

    if is_owner(user.id):
        dollar = "∞"
        diamond = "∞"
    else:
        dollar = str(u["dollar"])
        diamond = str(u["diamond"])

    return f""" • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •

👤 Ism: {user.first_name or "Noma'lum"}
🆔 ID: {user.id}

💵 Dollar: {dollar}
💎 Olmos: {diamond}

🛡 Qora qalqon: {u["items"]["shield"]}
📜 Soxta hujjat: {u["items"]["document"]}
⚖️ Afv tamg‘asi: {u["items"]["forgiveness"]}
🩸 Qotil niqobi: {u["items"]["killer_mask"]}
🔫 Noir miltig‘i: {u["items"]["gun"]}
💊 Qora dori: {u["items"]["black_medicine"]}
🧪 Verbena ekstrakti: {u["items"]["verbena"]}
🥷 Sirli niqob: {u["items"]["mystery_mask"]}
🛡️ Geroydan himoya: {u["items"]["hero_protection"]}

⚔️ Geroy: {"Bor" if u["hero"] else "Yo‘q"}
🃏 Faol rol: {"Bor" if u["active_role"] else "Yo‘q"}

🎯 G‘alabalar: 0
🎲 Barcha o‘yinlar: 0
📊 G‘alaba foizi: 0%"""


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "💵 Dollar olish",
            callback_data="dollar_exchange"
        )],
        [InlineKeyboardButton(
            "💎 Olmos olish",
            callback_data="diamond_buy"
        )],
        [InlineKeyboardButton(
            "⚔️ Mening Geroyim",
            callback_data="hero_profile"
        )],
        [InlineKeyboardButton(
            "💰 Do‘kon",
            callback_data="shop"
        )],
        [InlineKeyboardButton(
            "📖 Buyumlar haqida",
            callback_data="items_info"
        )],
        [InlineKeyboardButton(
            "🔻",
            callback_data="item_control"
        )],
    ])


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        get_profile_text(update.effective_user),
        reply_markup=get_profile_buttons()
    )


# =========================
# DOLLAR
# =========================

DOLLAR_PACKAGES = [
    (1, 600),
    (2, 1200),
    (3, 1800),
    (5, 3000),
    (10, 6000),
    (20, 12000),
]


async def dollar_exchange(update, context):
    query = update.callback_query
    await query.answer()

    buttons = []

    for diamond, dollar in DOLLAR_PACKAGES:
        buttons.append([
            InlineKeyboardButton(
                f"💎 {diamond} → 💵 {dollar}",
                callback_data=f"exchange_{diamond}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    await query.message.edit_text(
        "💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Olmosni Dollarga almashtiring:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def exchange_dollar(update, context):
    query = update.callback_query
    amount = int(query.data.split("_")[1])

    data, u = get_user_data(query.from_user.id)

    if not is_owner(query.from_user.id):
        if u["diamond"] < amount:
            await query.answer(
                "❌ Olmos yetarli emas",
                show_alert=True
            )
            return

        u["diamond"] -= amount
        u["dollar"] += amount * 600

        save_data(data)

    await query.answer("✅ Muvaffaqiyatli!")

    await query.message.edit_text(
        get_profile_text(query.from_user),
        reply_markup=get_profile_buttons()
    )


# =========================
# OLMOS OLISH
# =========================

DIAMOND_PACKAGES = [
    (5, 4000),
    (10, 8000),
    (25, 20000),
    (50, 40000),
    (100, 80000),
    (250, 200000),
]


async def diamond_buy(update, context):
    query = update.callback_query
    await query.answer()

    buttons = []

    for amount, price in DIAMOND_PACKAGES:
        buttons.append([
            InlineKeyboardButton(
                f"💎 {amount} ta — {price:,} so‘m".replace(",", " "),
                url=f"https://t.me/{OWNER_USERNAME}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    await query.message.edit_text(
        "💎 • 𝑶𝒍𝒎𝒐𝒔 𝒐𝒍𝒊𝒔𝒉 •\n\n"
        "Kerakli paketni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================
# DO‘KON
# =========================

async def shop(update, context):
    query = update.callback_query
    await query.answer()

    buttons = []

    for key, (name, price, currency) in ITEMS.items():
        emoji = "💵" if currency == "dollar" else "💎"

        buttons.append([
            InlineKeyboardButton(
                f"{name} — {emoji} {price}",
                callback_data=f"buy_{key}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("🔙 Orqaga", callback_data="profile")
    ])

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "Kerakli buyumni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def buy_item(update, context):
    query = update.callback_query
    key = query.data.replace("buy_", "", 1)

    if key not in ITEMS:
        await query.answer()
        return

    name, price, currency = ITEMS[key]

    data, u = get_user_data(query.from_user.id)

    owner = is_owner(query.from_user.id)

    if not owner:
        if currency == "dollar":
            if u["dollar"] < price:
                await query.answer(
                    "❌ Dollar yetarli emas",
                    show_alert=True
                )
                return
            u["dollar"] -= price

        else:
            if u["diamond"] < price:
                await query.answer(
                    "❌ Olmos yetarli emas",
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

    await query.answer("✅ Xarid qilindi!")

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        f"✅ {name} olindi.\n\n"
        "Yana buyum tanlang:",
        reply_markup=InlineKeyboardMarkup([
            *[
                [InlineKeyboardButton(
                    f"{n} — {'💵' if c == 'dollar' else '💎'} {p}",
                    callback_data=f"buy_{k}"
                )]
                for k, (n, p, c) in ITEMS.items()
            ],
            [InlineKeyboardButton(
                "🔙 Orqaga",
                callback_data="profile"
            )]
        ])
    )


# =========================
# GEROY PROFILI
# =========================

XP_REQUIREMENTS = {
    1: 150,
    2: 300,
    3: 700,
    4: 1300,
}


def hero_profile_text(u):
    if not u["hero"]:
        return "⚔️ Sizda Geroy yo‘q."

    level = u["hero_level"]
    xp = u["hero_xp"]

    if level < 5:
        next_xp = XP_REQUIREMENTS[level]
        xp_text = f"{xp} / {next_xp}"
        next_text = f"{next_xp - xp} XP qoldi"
    else:
        xp_text = f"{xp} XP"
        next_text = "Maksimal daraja"

    abilities = [
        f"⚔️ Hujum: {'✅' if level >= 1 else '🔒'}",
        f"🛡️ Himoya: {'✅' if level >= 2 else '🔒'}",
        f"🪖 Zirh: {'✅' if level >= 3 else '🔒'}",
        f"🩸 Qasos: {'✅' if level >= 4 else '🔒'}",
        f"💀 O‘lmaslik: {'✅' if level >= 5 else '🔒'}",
    ]

    return f"""⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •
