import os
import json
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
FILE = Path("data.json")

ITEMS = {
    "Qora qalqon": ("🛡️", 700),
    "Soxta hujjat": ("📜", 900),
    "Afv tamg'asi": ("⚖️", 1200),
    "Qotil niqobi": ("🩸", 1500),
    "Noir miltig'i": ("🔫", 1800),
    "Qora dori": ("💊", 1000),
    "Verbena ekstrakti": ("🧪", 1300),
    "Sirli niqob": ("🎭", 1600),
    "Geroydan himoya": ("🛡️", 2000),
}

try:
    DATA = json.loads(FILE.read_text(encoding="utf-8"))
except Exception:
    DATA = {"users": {}, "games": {}}


def save():
    FILE.write_text(
        json.dumps(DATA, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_user(tg_user):
    uid = str(tg_user.id)

    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "id": tg_user.id,
            "name": tg_user.first_name or "O'yinchi",
            "money": 1000,
            "gems": 10,
            "wins": 0,
            "games": 0,
            "hero": None,
            "hero_xp": 0,
            "role": None,
            "items": {name: 0 for name in ITEMS},
        }
        save()

    u = DATA["users"][uid]

    u.setdefault("name", tg_user.first_name or "O'yinchi")
    u.setdefault("money", 1000)
    u.setdefault("gems", 10)
    u.setdefault("wins", 0)
    u.setdefault("games", 0)
    u.setdefault("hero", None)
    u.setdefault("hero_xp", 0)
    u.setdefault("role", None)
    u.setdefault("items", {})

    for item in ITEMS:
        u["items"].setdefault(item, 0)

    return u


def main_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 Dollar olish", callback_data="money"),
            InlineKeyboardButton("💎 Olmos olish", callback_data="gems"),
        ],
        [
            InlineKeyboardButton("🦸 Mening Geroyim", callback_data="hero"),
            InlineKeyboardButton("🛒 Do'kon", callback_data="shop"),
        ],
        [
            InlineKeyboardButton("🔽 Pastga", callback_data="down"),
            InlineKeyboardButton("📖 Buyumlar haqida", callback_data="info"),
        ],
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="back")]
    ])


def profile_text(u):
    games = u["games"]
    winrate = round(u["wins"] / games * 100, 1) if games else 0

    text = (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {u['name']}\n"
        f"🆔 ID: {u['id']}\n\n"
        f"💵 Dollar: {u['money']}\n"
        f"💎 Olmos: {u['gems']}\n\n"
    )

    for name, item in ITEMS.items():
        text += f"{item[0]} {name}: {u['items'].get(name, 0)}\n"

    text += (
        f"\n🎯 G'alabalar: {u['wins']}\n"
        f"🎲 Barcha o'yinlar: {games}\n"
        f"📊 G'alaba foizi: {winrate}%\n\n"
        f"🃏 Faol rol: {u['role'] or 'Yo'q'}"
    )

    return text


def shop_text():
    text = "🛒 • 𝑫𝒐'𝒌𝒐𝒏 •\n\n"

    for name, (emoji, price) in ITEMS.items():
        text += f"{emoji} {name}\n"
        text += f"💵 Narxi: ${price}\n\n"

    return text + "👇 Sotib olish uchun buyumni tanlang:"


def shop_buttons():
    rows = []

    for name, (emoji, price) in ITEMS.items():
        rows.append([
            InlineKeyboardButton(
                f"{emoji} {name} — ${price}",
                callback_data=f"buy:{name}"
            )
        ])

    rows.append([
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back")
    ])

    return InlineKeyboardMarkup(rows)


def hero_text(u):
    if u["hero"]:
        return (
            "🦸 • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
            f"👤 Geroy: {u['hero']}\n"
            f"⭐ XP: {u['hero_xp']}\n"
        )

    return (
        "🦸 • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n"
        "❌ Sizda hozircha Geroy yo'q.\n\n"
        "🎯 O'yinlarda qatnashib Geroyingizni rivojlantiring."
    )


def info_text():
    return (
        "📖 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓 𝒉𝒂𝒒𝒊𝒅𝒂 •\n\n"
        "🛡️ Qora qalqon — himoya buyumi.\n"
        "📜 Soxta hujjat — maxsus topshiriq uchun.\n"
        "⚖️ Afv tamg'asi — jazodan qutulish uchun.\n"
        "🩸 Qotil niqobi — maxsus rol uchun.\n"
        "🔫 Noir miltig'i — kuchli qurol.\n"
        "💊 Qora dori — maxsus imkoniyat.\n"
        "🧪 Verbena ekstrakti — himoya vositasi.\n"
        "🎭 Sirli niqob — yashirin harakat uchun.\n"
        "🛡️ Geroydan himoya — Geroyga qarshi himoya.\n\n"
        "🛒 Buyumlarni Do'kondan sotib olishingiz mumkin."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user)

    await update.message.reply_text(
        profile_text(u),
        reply_markup=main_buttons()
    )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user)

    await update.message.reply_text(
        profile_text(u),
        reply_markup=main_buttons()
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    u = get_user(query.from_user)
    data = query.data

    if data == "back":
        await query.edit_message_text(
            profile_text(u),
            reply_markup=main_buttons()
        )
        return

    if data == "money":
        u["money"] += 100
        save()

        await query.edit_message_text(
            "💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\n"
            "✅ Sizga $100 berildi!\n\n"
            f"💰 Balansingiz: ${u['money']}",
            reply_markup=back_button()
        )
        return

    if data == "gems":
        u["gems"] += 1
        save()

        await query.edit_message_text(
            "💎 • 𝑶𝒍𝒎𝒐𝒔 𝒐𝒍𝒊𝒔𝒉 •\n\n"
            "✅ Sizga 1 💎 olmos berildi!\n\n"
            f"💎 Balansingiz: {u['gems']}",
            reply_markup=back_button()
        )
        return

    if data == "hero":
        await query.edit_message_text(
            hero_text(u),
            reply_markup=back_button()
        )
        return

    if data == "shop":
        await query.edit_message_text(
            shop_text(),
            reply_markup=shop_buttons()
        )
        return

    if data == "info":
        await query.edit_message_text(
            info_text(),
            reply_markup=back_button()
        )
        return

    if data == "down":
        await query.edit_message_text(
            "🔽 • 𝑺𝒕𝒂𝒕𝒊𝒔𝒕𝒊𝒌𝒂 •\n\n"
            f"🎯 G'alabalar: {u['wins']}\n"
            f"🎲 O'yinlar: {u['games']}\n"
            f"💵 Dollar: {u['money']}\n"
            f"💎 Olmos: {u['gems']}\n"
            f"🦸 Geroy: {u['hero'] or 'Yo'q'}",
            reply_markup=back_button()
        )
        return

    if data.startswith("buy:"):
        item_name = data[4:]

        if item_name not in ITEMS:
            await query.edit_message_text(
                "❌ Bunday buyum mavjud emas.",
                reply_markup=back_button()
            )
            return

        emoji, price = ITEMS[item_name]

        if u["money"] < price:
            await query.answer(
                "❌ Dollar yetarli emas!",
                show_alert=True
            )
            return

        u["money"] -= price
        u["items"][item_name] += 1
        save()

        await query.edit_message_text(
            "✅ • 𝑩𝒖𝒚𝒖𝒎 𝒔𝒐𝒕𝒊𝒃 𝒐𝒍𝒊𝒏𝒅𝒊 •\n\n"
            f"{emoji} {item_name}\n\n"
            f"💵 Sarflandi: ${price}\n"
            f"💰 Qolgan dollar: ${u['money']}\n"
            f"📦 Soni: {u['items'][item_name]}",
            reply_markup=shop_buttons()
        )
        return


async def error_handler(update, context):
    print("BOT ERROR:", context.error)


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.add_error_handler(error_handler)

    print("Mafia Noir Bot ishga tushdi...")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
