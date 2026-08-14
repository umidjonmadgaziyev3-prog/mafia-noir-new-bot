import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    profile_text = f"""🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •

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

    buttons = [
        [InlineKeyboardButton("💵 Dollar olish", callback_data="none")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="none")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="none")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="none")],
        [InlineKeyboardButton("🔻", callback_data="none")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="none")],
    ]

    await update.message.reply_text(
        profile_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("profile", profile))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
