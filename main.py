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
            "vip": user_id == OWNER_ID,
            "hero": 0,
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
        save_data(data)

    user = data[uid]

    user.setdefault("dollar", 0)
    user.setdefault("diamond", 0)
    user["vip"] = user_id == OWNER_ID
    user.setdefault("hero", 0)
    user.setdefault("active_role", 0)
    user.setdefault("items", {})
    user.setdefault("active_items", {})

    for key in ITEMS:
        if key not in ("hero", "active_role"):
            user["items"].setdefault(key, 0)
            user["active_items"].setdefault(key, False)

    save_data(data)
    return data, user


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

    vip_line = "\n👑 VIP: Ha" if u["vip"] else ""

    return f""" • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •

👤 Ism: {user.first_name or "Noma'lum"}
🆔 ID: {user.id}{vip_line}

💵 Dollar: {u["dollar"]}
💎 Olmos: {u["diamond"]}

🛡 Qora qalqon: {u["items"]["shield"]}
📜 Soxta hujjat: {u["items"]["document"]}
⚖️ Afv tamg‘asi: {u["items"]["forgiveness"]}
🩸 Qotil niqobi: {u["items"]["killer_mask"]}
🔫 Noir miltig‘i: {u["items"]["gun"]}
💊 Qora dori: {u["items"]["black_medicine"]}
🧪 Verbena ekstrakti: {u["items"]["verbena"]}
🥷 Sirli niqob: {u["items"]["mystery_mask"]}
🛡️ Geroydan himoya: {u["items"]["hero_protection"]}

⚔️ Geroy: {"Bor" if u["hero"] > 0 else "Yo‘q"}
🃏 Faol rol: {"Bor" if u["active_role"] > 0 else "Yo‘q"}

🎯 G‘alabalar: 0
🎲 Barcha o‘yinlar: 0
📊 G‘alaba foizi: 0"""


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
            callback_data="hero"
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
# DOLLAR OLISH
# =========================

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
    amount = int(query.data.split("_")[1])

    data, u = get_user_data(query.from_user.id)

    if u["diamond"] < amount:
        await query.answer(
            "❌ Olmos yetarli emas",
            show_alert=True
        )
        return

    u["diamond"] -= amount
    u["dollar"] += amount * 600

    save_data(data)

    await query.answer("✅ Savdo muvaffaqiyatli amalga oshirildi!")

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


# =========================
# DO‘KON
# =========================

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
        await query.answer()
        return

    name, price, currency = ITEMS[key]

    data, u = get_user_data(query.from_user.id)

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

    await query.answer("✅ Xarid muvaffaqiyatli amalga oshirildi!")

    await query.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "✅ Xarid muvaffaqiyatli amalga oshirildi.\n\n"
        "Yana buyum tanlang:",
        reply_markup=get_shop_buttons()
    )


# =========================
# BUYUMLAR HAQIDA
# =========================

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


# =========================
# ON / OFF
# =========================

def get_control_buttons(u):
    keyboard = []

    for key, (name, _, _) in ITEMS.items():
        if key in ("hero", "active_role"):
            continue

        count = u["items"][key]
        active = u["active_items"][key]

        status = "⚪ OFF | 🟢 ON" if active else "⚪ OFF | ON"

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

    data, u = get_user_data(query.from_user.id)

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


# =========================
# HERO — HOZIRCHA
# =========================

async def hero(update, context):
    query = update.callback_query
    await query.answer()

    _, u = get_user_data(query.from_user.id)

    await query.message.edit_text(
        "⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
        f"Geroylar: {u['hero']}\n\n"
        "Geroyning maxsus mexanizmi keyin qo‘shiladi.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Orqaga",
                    callback_data="profile"
                )
            ]
        ])
    )


# =========================
# ROLES
# =========================

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


async def roles(update, context):
    await update.message.reply_text(
        "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
        "Kerakli rolni tanlang:",
        reply_markup=get_roles_buttons()
    )


async def role_button(update, context):
    await update.callback_query.answer()


# =========================
# CALLBACK
# =========================

async def callback_handler(update, context):
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

    elif data.startswith("role_"):
        await role_button(update, context)

    else:
        await query.answer()


# =========================
# MAIN
# =========================

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("roles", roles))

    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
