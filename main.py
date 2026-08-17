# 1. importlar
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 2. TOKEN
TOKEN = os.getenv("BOT_TOKEN")

# 3. ROLLAR
ROLES = [
    ("🎩 Don", "role_don"),
    ("🥷 Mafia", "role_mafia"),
    ("🎭 Aferist", "role_aferist"),
    # ... qolgan 22 ta rol
]

# 4. /roles funksiyasi
async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for i in range(0, len(ROLES), 2):
        row = [
            InlineKeyboardButton(ROLES[i][0], callback_data=ROLES[i][1])
        ]

        if i + 1 < len(ROLES):
            row.append(
                InlineKeyboardButton(
                    ROLES[i + 1][0],
                    callback_data=ROLES[i + 1][1]
                )
            )

        keyboard.append(row)

    await update.message.reply_text(
        "🎭 **Mafia Noir — Rollar**\n\nKerakli rolni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# 5. main()
def main():
    app = Application.builder().token(TOKEN).build()

    # boshqa handlerlaring
    app.add_handler(CommandHandler("roles", roles))

    app.run_polling()

# 6. ishga tushirish
if __name__ == "__main__":
    main()
