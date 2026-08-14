import os
import requests

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

API = f"https://api.telegram.org/bot{TOKEN}"


# =========================
# 7 TA TIL
# =========================

LANGUAGES = {
    "uz": "🇺🇿 O‘zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "tr": "🇹🇷 Türkçe",
    "kk": "🇰🇿 Қазақша",
    "uk": "🇺🇦 Українська",
    "de": "🇩🇪 Deutsch"
}


# =========================
# MATNLAR
# =========================

TEXTS = {
    "uz": {
        "welcome": "Salom! Xush kelibsiz! 👋\n\nMen Mafia Noir botiman. Mafia o‘ynash uchun meni guruhingizga qo‘shing. 🎭",
        "add": "Guruhga qo‘shish ➕",
        "owner": "Savollar uchun Owner 👑",
        "language": "Tilni tanlang:"
    },

    "ru": {
        "welcome": "Привет! Добро пожаловать! 👋\n\nЯ бот Mafia Noir. Чтобы играть в Mafia, добавьте меня в свою группу. 🎭",
        "add": "Добавить в группу ➕",
        "owner": "Вопросы — Owner 👑",
        "language": "Выберите язык:"
    },

    "en": {
        "welcome": "Hello! Welcome! 👋\n\nI am the Mafia Noir bot. Add me to your group to play Mafia. 🎭",
        "add": "Add to group ➕",
        "owner": "Questions — Owner 👑",
        "language": "Choose your language:"
    },

    "tr": {
        "welcome": "Merhaba! Hoş geldiniz! 👋\n\nBen Mafia Noir botuyum. Mafia oynamak için beni grubunuza ekleyin. 🎭",
        "add": "Gruba ekle ➕",
        "owner": "Sorular için Owner 👑",
        "language": "Dil seçin:"
    },

    "kk": {
        "welcome": "Сәлем! Қош келдіңіз! 👋\n\nМен Mafia Noir ботымын. Mafia ойнау үшін мені тобыңызға қосыңыз. 🎭",
        "add": "Топқа қосу ➕",
        "owner": "Сұрақтар үшін Owner 👑",
        "language": "Тілді таңдаңыз:"
    },

    "uk": {
        "welcome": "Привіт! Ласкаво просимо! 👋\n\nЯ бот Mafia Noir. Щоб грати в Mafia, додайте мене до своєї групи. 🎭",
        "add": "Додати в групу ➕",
        "owner": "Питання — Owner 👑",
        "language": "Оберіть мову:"
    },

    "de": {
        "welcome": "Hallo! Willkommen! 👋\n\nIch bin der Mafia Noir Bot. Füge mich deiner Gruppe hinzu, um Mafia zu spielen. 🎭",
        "add": "Zur Gruppe hinzufügen ➕",
        "owner": "Fragen — Owner 👑",
        "language": "Sprache auswählen:"
    }
}


# =========================
# TELEGRAM API
# =========================

def telegram(method, data=None):
    url = f"{API}/{method}"
    response = requests.post(url, json=data or {})
    return response.json()


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    return telegram("sendMessage", data)


# =========================
# TIL TANLASH
# =========================

def language_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": LANGUAGES["uz"], "callback_data": "lang_uz"},
                {"text": LANGUAGES["ru"], "callback_data": "lang_ru"}
            ],
            [
                {"text": LANGUAGES["en"], "callback_data": "lang_en"},
                {"text": LANGUAGES["tr"], "callback_data": "lang_tr"}
            ],
            [
                {"text": LANGUAGES["kk"], "callback_data": "lang_kk"},
                {"text": LANGUAGES["uk"], "callback_data": "lang_uk"}
            ],
            [
                {"text": LANGUAGES["de"], "callback_data": "lang_de"}
            ]
        ]
    }


# =========================
# ASOSIY TUGMALAR
# =========================

def main_keyboard(lang):
    return {
        "inline_keyboard": [
            [
                {
                    "text": TEXTS[lang]["add"],
                    "url": "https://t.me/Noiruzbot?startgroup=true"
                }
            ],
            [
                {
                    "text": TEXTS[lang]["owner"],
                    "url": "https://t.me/Umarov_uuu"
                }
            ]
        ]
    }


# =========================
# UPDATE ISHLASH
# =========================

def handle_update(update):

    # /start
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/start"):
            send_message(
                chat_id,
                "🌍 Tilni tanlang / Выберите язык / Choose your language:",
                language_keyboard()
            )

    # Tugma bosilganda
    elif "callback_query" in update:
        callback = update["callback_query"]
        data = callback["data"]
        callback_id = callback["id"]
        chat_id = callback["message"]["chat"]["id"]

        if data.startswith("lang_"):
            lang = data.replace("lang_", "")

            if lang in TEXTS:
                telegram(
                    "answerCallbackQuery",
                    {"callback_query_id": callback_id}
                )

                send_message(
                    chat_id,
                    TEXTS[lang]["welcome"],
                    main_keyboard(lang)
                )


# =========================
# BOT ISHLASHI
# =========================

def main():
    offset = 0

    print("Mafia Noir bot ishga tushdi...")

    while True:
        updates = telegram(
            "getUpdates",
            {
                "offset": offset,
                "timeout": 30
            }
        )

        if not updates.get("ok"):
            continue

        for update in updates.get("result", []):
            offset = update["update_id"] + 1

            try:
                handle_update(update)
            except Exception as e:
                print("Xatolik:", e)


if __name__ == "__main__":
    main()
