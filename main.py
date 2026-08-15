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
# ROLLAR
# =========================

ROLES = {
    "don": {
        "name": "🎩 Don",
        "team": "🎩 Mafia",
        "task": "Mafia jamoasini boshqaradi va hujum nishonini tanlaydi.",
        "win": "Mafia ustunlikka erishsa."
    },
    "mafia": {
        "name": "🥷 Mafia",
        "team": "🎩 Mafia",
        "task": "Don bilan birga kechasi hujum qiladi.",
        "win": "Mafia ustunlikka erishsa."
    },
    "killer": {
        "name": "🔪 Qotil",
        "team": "🏘️ Shahar",
        "task": "Kechasi bir o‘yinchiga hujum qiladi.",
        "win": "Barcha dushmanlar yo‘q qilinsa."
    },
    "commissioner": {
        "name": "👮 Komissar",
        "team": "🏘️ Shahar",
        "task": "Kechasi bir o‘yinchini tekshiradi.",
        "win": "Mafia yo‘q qilinsa."
    },
    "doctor": {
        "name": "👨‍⚕️ Doktor",
        "team": "🏘️ Shahar",
        "task": "Kechasi bir o‘yinchini o‘limdan saqlaydi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "sergeant": {
        "name": "👮‍♂️ Serjant",
        "team": "🏘️ Shahar",
        "task": "Komissarga yordam beradi va u o‘lsa, ishini davom ettiradi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "captain": {
        "name": "🎖️ Kapitan",
        "team": "🏘️ Shahar",
        "task": "Ovoz berishda kuchliroq ovozga ega.",
        "win": "Shahar g‘alaba qilsa."
    },
    "citizen": {
        "name": "👤 Fuqaro",
        "team": "🏘️ Shahar",
        "task": "Kunduz ovoz beradi va Mafia'ni topishga yordam beradi.",
        "win": "Barcha Mafia yo‘q qilinsa."
    },
    "vagabond": {
        "name": "👣 Daydi",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchini kuzatib, u kimning oldiga borganini biladi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "judge": {
        "name": "⚖️ Sudya",
        "team": "🏘️ Shahar",
        "task": "Bir marta ovoz berishni bekor qilib, qayta ovoz beradi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "lawyer": {
        "name": "👨‍⚖️ Advokat",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchini himoya qiladi va tekshiruvni chalg‘itadi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "avenger": {
        "name": "💀 Qasoskor",
        "team": "🏘️ Shahar",
        "task": "O‘ldirilsa, hujum qilgan odamdan qasos oladi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "chameleon": {
        "name": "🦎 Buqalamun",
        "team": "🏘️ Shahar",
        "task": "Bir marta tekshiruvda boshqa rol sifatida ko‘rinadi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "observer": {
        "name": "🕵️ Kuzatuvchi",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchining kechasi nima qilganini kuzatadi.",
        "win": "Mafia yo‘q qilinsa."
    },
    "bodyguard": {
        "name": "🛡️ Bodyguard",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchini himoya qiladi va hujumni o‘ziga oladi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "wizard": {
        "name": "🧙 Sehrgar",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchining qobiliyatini vaqtincha to‘xtatadi.",
        "win": "Mafia yo‘q qilinsa."
    },
    "journalist": {
        "name": "📰 Jurnalist",
        "team": "🏘️ Shahar",
        "task": "Ikki o‘yinchining bir jamoaga tegishli ekanini tekshiradi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "chemist": {
        "name": "🔬 Kimyogar",
        "team": "🏘️ Shahar",
        "task": "Bir marta davolaydi va bir marta zaharlaydi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "miner": {
        "name": "💣 Minyor",
        "team": "🏘️ Shahar",
        "task": "O‘ldirilsa, hujum qilgan odamni ham yo‘q qiladi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "warlock": {
        "name": "⚡ Koldun",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchining tungi harakatini boshqa nishonga yo‘naltiradi.",
        "win": "Shahar g‘alaba qilsa."
    },
    "secret_agent": {
        "name": "🕶️ Maxfiy agent",
        "team": "🏘️ Shahar",
        "task": "Bir o‘yinchining jamoasini yashirincha aniqlaydi.",
        "win": "Mafia yo‘q qilinsa."
    },
    "ghost": {
        "name": "👻 Arvoh",
        "team": "🕊️ Neutral",
        "task": "O‘lgandan keyin bir marta yashirincha yordam beradi.",
        "win": "Maxsus shartini bajarsa."
    },
    "joker": {
        "name": "🤡 Joker",
        "team": "🕊️ Neutral",
        "task": "Kunduzgi ovozda o‘zini o‘ldirtirishga harakat qiladi.",
        "win": "Ovoz berib o‘ldirilsa."
    },
    "vampire": {
        "name": "🧛 Vampir",
        "team": "🕊️ Neutral",
        "task": "Kechasi o‘yinchilarni vampir tomoniga o‘tkazadi.",
        "win": "Vampirlar ustunlikka erishsa."
    },
}


# =========================
# PROFIL
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
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="olmos")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back")],
    ])


# =========================
# ROLES TUGMALARI
# =========================

def get_roles_buttons():
    keys = list(ROLES.keys())
    rows = []

    for i in range(0, len(keys), 2):
        row = [
            InlineKeyboardButton(
                ROLES[keys[i]]["name"],
                callback_data=f"role_{keys[i]}"
            )
        ]

        if i + 1 < len(keys):
            row.append(
                InlineKeyboardButton(
                    ROLES[keys[i + 1]]["name"],
                    callback_data=f"role_{keys[i + 1]}"
                )
            )

        rows.append(row)

    return InlineKeyboardMarkup(rows)


async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 **Mafia Noir — Rollar**\n\n"
        "Kerakli rolni tanlang:",
        reply_markup=get_roles_buttons(),
        parse_mode="Markdown"
    )


# =========================
# ROLE POPUP
# =========================

async def role_popup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    role_key = query.data.replace("role_", "", 1)
    role = ROLES.get(role_key)

    if not role:
        await query.answer("Rol topilmadi.")
        return

    text = (
        f"{role['name']}\n\n"
        f"📌 Vazifasi:\n{role['task']}\n\n"
        f"👥 Jamoasi: {role['team']}\n\n"
        f"🏆 G‘alaba siri:\n{role['win']}"
    )

    # Yangi xabar kelmaydi.
    # Ma'lumot Telegram popupida chiqadi.
    await query.answer(text, show_alert=True)


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


# =========================
# ASOSIY TUGMALAR
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

    app.add_handler(
        CallbackQueryHandler(
            profile_button,
            pattern="^profile$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            role_popup,
            pattern="^role_"
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.run_polling(drop_pending_updates=True)
