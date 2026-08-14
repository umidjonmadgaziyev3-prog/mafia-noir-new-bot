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


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="olmos")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("🔻", callback_data="down")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items")],
    ])


# /profile komandasi
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        get_profile_text(user),
        reply_markup=get_profile_buttons()
    )


# Profil tugmasi bosilganda
async def profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    # Har bosilganda profilni qayta chiqaradi
    await query.message.reply_text(
        get_profile_text(user),
        reply_markup=get_profile_buttons()
    )


# Boshqa tugmalar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    app = Application.builder().token(TOKEN).build()

    # /profile komandasi
    app.add_handler(CommandHandler("profile", profile))

    # PROFILE tugmasi uchun
    app.add_handler(
        CallbackQueryHandler(profile_button, pattern="^profile$")
    )

    # Qolgan tugmalar
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
