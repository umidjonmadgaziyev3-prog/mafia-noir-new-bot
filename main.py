import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")


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
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="olmos")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        f"🕴️ Salom, {user.first_name or 'o‘yinchi'}!\n\n"
        "🌃 Mafia Noir'ga xush kelibsiz.\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=get_main_buttons()
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        get_profile_text(user),
        reply_markup=get_profile_buttons()
    )


async def profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    await query.message.edit_text(
        get_profile_text(user),
        reply_markup=get_profile_buttons()
    )


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


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))

    # 👤 PROFIL TUGMASI
    app.add_handler(
        CallbackQueryHandler(
            profile_button,
            pattern="^profile$"
        )
    )

    # Qolgan tugmalar
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
