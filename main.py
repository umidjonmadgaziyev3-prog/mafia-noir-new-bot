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
# PROFILE
# =========================

def get_profile_text(user):
    return f"""🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •

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
📊 G‘alaba foizi: 0%
🃏 Faol rol: Yo‘q"""


def get_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profil", callback_data="profile")],
        [InlineKeyboardButton("💵 Dollar", callback_data="dollar")],
        [InlineKeyboardButton("💎 Olmos", callback_data="olmos")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items")],
    ])


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="profile_noop")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="profile_noop")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="profile_noop")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="profile_noop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="profile_noop")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="profile_noop")],
    ])


# =========================
# ROLES
# =========================

def get_roles_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🕵️ Detektiv", callback_data="role_detective")],
        [InlineKeyboardButton("🔫 Mafia", callback_data="role_mafia")],
        [InlineKeyboardButton("👨‍⚕️ Doktor", callback_data="role_doctor")],
        [InlineKeyboardButton("👤 Fuqaro", callback_data="role_citizen")],
        [InlineKeyboardButton("🎯 Vazifa", callback_data="role_task")],
        [InlineKeyboardButton("👥 Jamoa", callback_data="role_team")],
        [InlineKeyboardButton("🏆 G‘alaba", callback_data="role_win")],
    ])


async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
        "Quyidagi roldan birini tanlang:",
        reply_markup=get_roles_buttons()
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        f"🕴️ Salom, {user.first_name or 'o‘yinchi'}!\n\n"
        "🌃 Mafia Noir'ga xush kelibsiz.\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=get_main_buttons()
    )


# =========================
# PROFILE COMMAND
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
# PROFILE ICHIDAGI TUGMALAR
# HECH NIMA QILMAYDI
# =========================

async def profile_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Faqat loadingni yopadi.
    # Hech qanday xabar, oyna yoki amal qilmaydi.
    await query.answer()


# =========================
# ROLES BUTTONLARI
# =========================

async def roles_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "role_detective":
        text = (
            "🕵️ DETEKTIV\n\n"
            "🔎 Vazifasi: shubhali o‘yinchilarni aniqlash.\n"
            "👥 Jamoasi: Tinch aholi.\n"
            "🏆 G‘alabasi: Mafia yo‘q qilinganda."
        )

    elif data == "role_mafia":
        text = (
            "🔫 MAFIA\n\n"
            "🎯 Vazifasi: tinch aholini yo‘q qilish.\n"
            "👥 Jamoasi: Mafia.\n"
            "🏆 G‘alabasi: Mafia soni ustun kelganda."
        )

    elif data == "role_doctor":
        text = (
            "👨‍⚕️ DOKTOR\n\n"
            "🩺 Vazifasi: o‘yinchilarni himoya qilish.\n"
            "👥 Jamoasi: Tinch aholi.\n"
            "🏆 G‘alabasi: Tinch aholi g‘alaba qilganda."
        )

    elif data == "role_citizen":
        text = (
            "👤 FUQARO\n\n"
            "🎯 Vazifasi: Mafia kimligini aniqlash.\n"
            "👥 Jamoasi: Tinch aholi.\n"
            "🏆 G‘alabasi: Mafia yo‘q qilinganda."
        )

    elif data == "role_task":
        text = (
            "🎯 VAZIFA\n\n"
            "Har bir rolning o‘ziga xos vazifasi mavjud."
        )

    elif data == "role_team":
        text = (
            "👥 JAMOA\n\n"
            "Tinch aholi va Mafia o‘z jamoasi bilan g‘alaba "
            "qozonishga harakat qiladi."
        )

    elif data == "role_win":
        text = (
            "🏆 G‘ALABA\n\n"
            "Har bir rol o‘z jamoasi bilan belgilangan shartni "
            "bajarganda g‘alaba qozonadi."
        )

    else:
        return

    await query.message.edit_text(
        text,
        reply_markup=get_roles_buttons()
    )


# =========================
# MAIN BUTTONS
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "back":
        await query.message.edit_text(
            f"🕴️ Salom, {user.first_name or 'o‘yinchi'}!\n\n"
            "🌃 Mafia Noir menyusi:",
            reply_markup=get_main_buttons()
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

    # Profile ochish
    app.add_handler(
        CallbackQueryHandler(
            profile_button,
            pattern="^profile$"
        )
    )

    # Profile ichidagi tugmalar — HECH NIMA QILMAYDI
    app.add_handler(
        CallbackQueryHandler(
            profile_noop,
            pattern="^profile_noop$"
        )
    )

    # Roles tugmalari
    app.add_handler(
        CallbackQueryHandler(
            roles_button,
            pattern="^role_"
        )
    )

    # Qolgan asosiy tugmalar
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
