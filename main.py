import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")


def profile_text(user):
    name = user.first_name or "Noma'lum"

    return (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {name}\n"
        f"🆔 ID: {user.id}\n\n"
        "💵 Dollar: 0\n"
        "💎 Olmos: 0\n"
        "🛡 Qora qalqon: 0\n"
        "📜 Soxta hujjat: 0\n"
        "⚖️ Afv tamg‘asi: 0\n"
        "🩸 Qotil niqobi: 0\n"
        "🔫 Noir miltig‘i: 0\n"
        "💊 Qora dori: 0\n"
        "🧪 Verbena ekstrakti: 0\n"
        "🥷 Sirli niqob: 0\n"
        "🛡️ Geroydan himoya: 0\n\n"
        "🎯 G‘alabalar: 0\n"
        "🎲 Barcha o‘yinlar: 0\n"
        "📊 G‘alaba foizi: 0%\n\n"
        "🃏 Faol rol: Yo‘q"
    )


def profile_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💵 Dollar olish",
                callback_data="dollar"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Olmos olish",
                callback_data="olmos"
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
                "🔻 Profil",
                callback_data="profile"
            )
        ],
        [
            InlineKeyboardButton(
                "📖 Buyumlar haqida",
                callback_data="items"
            )
        ],
    ])


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not user:
        return

    await update.message.reply_text(
        profile_text(user),
        reply_markup=profile_keyboard()
    )


async def profile_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    user = query.from_user

    await query.message.edit_text(
        profile_text(user),
        reply_markup=profile_keyboard()
    )


async def other_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    # Hozircha tugmalar hech qanday amal bajarmaydi.
    # Keyin bittalab ishga tushiramiz.
    await query.answer()


def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. GitHub Secrets ichida "
            "BOT_TOKEN saqlanganini tekshiring."
        )

    app = Application.builder().token(TOKEN).build()

    # /profile
    app.add_handler(
        CommandHandler("profile", profile)
    )

    # Profil tugmasi
    app.add_handler(
        CallbackQueryHandler(
            profile_button,
            pattern=r"^profile$"
        )
    )

    # Qolgan tugmalar
    app.add_handler(
        CallbackQueryHandler(
            other_buttons
        )
    )

    print("🤖 Bot ishga tushdi...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
