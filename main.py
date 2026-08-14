import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes


TOKEN = os.getenv("BOT_TOKEN")


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    name = user.first_name or "Noma'lum"
    user_id = user.id

    text = f"""🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •

👤 Ism: {name}
🆔 ID: {user_id}

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

🃏 Faol rol: Yo‘q
"""

    keyboard = [
        [
            InlineKeyboardButton("💵 Dollar olish", callback_data="unused"),
            InlineKeyboardButton("💎 Olmos olish", callback_data="unused"),
        ],
        [
            InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="unused"),
            InlineKeyboardButton("💰 Do‘kon", callback_data="unused"),
        ],
        [
            InlineKeyboardButton("🔻", callback_data="unused"),
            InlineKeyboardButton("📖 Buyumlar haqida", callback_data="unused"),
        ],
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN topilmadi!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("profile", profile))

    app.run_polling()


if __name__ == "__main__":
    main()
