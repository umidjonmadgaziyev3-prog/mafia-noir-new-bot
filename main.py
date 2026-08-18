import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")


# =========================
# START — TIL TANLASH
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


# =========================
# START — ASOSIY TUGMALAR
# =========================

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


# =========================
# PROFILE
# =========================

def get_profile_text(user):
    return f""" • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •

👤 Ism: {user.first_name or "Noma'lum"}
🆔 ID: {user.id}

💵 Dollar: 0
💎 Olmos: 0

🛡 Qora qalqon: 0
📜 Soxta hujjat: 0
⚖️ Afv tamg‘asi: 0
🩸 Qotil niqobi: 0
🔫 Noir miltig‘i: 0
💊 Qora dori: 0
🧪 Verbena ekstrakti: 0
🥷 Sirli niqob: 0
🛡️ Geroydan himoya: 0

🎯 G‘alabalar: 0
🎲 Barcha o‘yinlar: 0
📊 G‘alaba foizi: 0

🃏 Faol rol: Yo‘q"""


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="profile_noop")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="profile_noop")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="profile_noop")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="profile_noop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="profile_noop")],
        [InlineKeyboardButton("🔻", callback_data="profile_noop")],
    ])


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


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Tilni tanlang:",
        reply_markup=get_language_buttons()
    )


# =========================
# TIL TANLANGANDAN KEYIN
# =========================

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
# /ROLES
# =========================

async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
        "Kerakli rolni tanlang:",
        reply_markup=get_roles_buttons()
    )


# =========================
# /PROFILE
# =========================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        get_profile_text(user),
        reply_markup=get_profile_buttons()
    )


# =========================
# PROFILE BUTTON
# =========================

async def profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    await query.message.edit_text(
        get_profile_text(user),
        reply_markup=get_profile_buttons()
    )


# =========================
# PROFILE BUTTONS — NOOP
# =========================

async def profile_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# =========================
# ROLE BUTTONS — NOOP
# =========================

async def roles_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# =========================
# MAIN BUTTONS
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "profile":
        await query.message.edit_text(
            get_profile_text(user),
            reply_markup=get_profile_buttons()
        )

    elif data == "roles":
        await query.message.edit_text(
            "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
            "Kerakli rolni tanlang:",
            reply_markup=get_roles_buttons()
        )

    elif data == "dollar":
        await query.message.reply_text(
            "💵 Dollar bo‘limi\n\n"
            "Hozircha balans: 0 $"
        )

    elif data == "olmos":
        await query.message.reply_text(
            "💎 Olmos bo‘limi\n\n"
            "Hozircha balans: 0 💎"
        )

    elif data == "hero":
        await query.message.reply_text(
            "⚔️ Mening Geroyim\n\n"
            "Hozircha geroyingiz mavjud emas."
        )

    elif data == "shop":
        await query.message.reply_text(
            "💰 Do‘kon\n\n"
            "🛡 Qora qalqon\n"
            "📜 Soxta hujjat\n"
            "⚖️ Afv tamg‘asi\n"
            "🩸 Qotil niqobi\n"
            "🔫 Noir miltig‘i"
        )

    elif data == "items":
        await query.message.reply_text(
            "📖 Buyumlar haqida\n\n"
            "🛡 Qora qalqon — himoya buyumi\n"
            "📜 Soxta hujjat — maxsus buyum\n"
            "⚖️ Afv tamg‘asi — jazodan qutulish\n"
            "🩸 Qotil niqobi — maxsus rol buyumi\n"
            "🔫 Noir miltig‘i — maxsus qurol"
        )


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

    # 7 ta til
    app.add_handler(
        CallbackQueryHandler(
            language_button,
            pattern="^lang_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            profile_button,
            pattern="^profile$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            profile_noop,
            pattern="^profile_noop$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            roles_button,
            pattern="^role_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
