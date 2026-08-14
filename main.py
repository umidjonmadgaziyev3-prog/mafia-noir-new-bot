import os
import requests

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

API = f"https://api.telegram.org/bot{TOKEN}"

LANGUAGES = {
    "uz": "🇺🇿 O‘zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "tr": "🇹🇷 Türkçe",
    "kk": "🇰🇿 Қазақша",
    "uk": "🇺🇦 Українська",
    "de": "🇩🇪 Deutsch"
}

TEXTS = {
    "uz": {
        "language": "Tilni tanlang:",
        "welcome": "Salom! Xush kelibsiz! 👋\n\nMen Mafia Noir botiman. Mafia o‘ynash uchun meni guruhingizga qo‘shing. 🎭",
        "add": "Guruhga qo‘shish ➕",
        "owner": "Savollar uchun Owner 👑"
    },
    "ru": {
        "language": "Выберите язык:",
        "welcome": "Привет! Добро пожаловать! 👋\n\nЯ бот Mafia Noir. Чтобы играть в Mafia, добавьте меня в свою группу. 🎭",
        "add": "Добавить в группу ➕",
        "owner": "Вопросы для Owner 👑"
    },
    "en": {
        "language": "Choose your language:",
        "welcome": "Hello! Welcome! 👋\n\nI am the Mafia Noir bot. Add me to your group to play Mafia. 🎭",
        "add": "Add to group ➕",
        "owner": "Questions for Owner 👑"
    },
    "tr": {
        "language": "Dil seçin:",
        "welcome": "Merhaba! Hoş geldiniz! 👋\n\nBen Mafia Noir botuyum. Mafia oynamak için beni grubunuza ekleyin. 🎭",
        "add": "Gruba ekle ➕",
        "owner": "Sorular için Owner 👑"
    },
    "kk": {
        "language": "Тілді таңдаңыз:",
        "welcome": "Сәлем! Қош келдіңіз! 👋\n\nМен Mafia Noir ботымын. Mafia ойнау үшін мені тобыңызға қосыңыз. 🎭",
        "add": "Топқа қосу ➕",
        "owner": "Сұрақтар үшін Owner 👑"
    },
    "uk": {
        "language": "Оберіть мову:",
        "welcome": "Привіт! Ласкаво просимо! 👋\n\nЯ бот Mafia Noir. Щоб грати в Mafia, додайте мене до своєї групи. 🎭",
        "add": "Додати в групу ➕",
        "owner": "Питання для Owner 👑"
    },
    "de": {
        "language": "Sprache auswählen:",
        "welcome": "Hallo! Willkommen! 👋\n\nIch bin der Mafia Noir Bot. Füge mich deiner Gruppe hinzu, um Mafia zu spielen. 🎭",
        "add": "Zur Gruppe hinzufügen ➕",
        "owner": "Fragen für Owner 👑"
    }
}


def telegram(method, data=None):
    response = requests.post(
        f"{API}/{method}",
        json=data or {},
        timeout=40
    )
    return response.json()


def language_keyboard():
    return {
        "inline_keyboard": [
            [{"text": LANGUAGES["uz"], "callback_data": "lang_uz"}],
            [{"text": LANGUAGES["ru"], "callback_data": "lang_ru"}],
            [{"text": LANGUAGES["en"], "callback_data": "lang_en"}],
            [{"text": LANGUAGES["tr"], "callback_data": "lang_tr"}],
            [{"text": LANGUAGES["kk"], "callback_data": "lang_kk"}],
            [{"text": LANGUAGES["uk"], "callback_data": "lang_uk"}],
            [{"text": LANGUAGES["de"], "callback_data": "lang_de"}]
        ]
    }


def main_keyboard(lang):
    return {
        "inline_keyboard": [
            [{
                "text": TEXTS[lang]["add"],
                "url": "https://t.me/Noiruzbot?startgroup=true"
            }],
            [{
                "text": TEXTS[lang]["owner"],
                "url": "https://t.me/Umarov_uuu"
            }]
        ]
    }


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    return telegram("sendMessage", data)


def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    return telegram("editMessageText", data)


def handle_update(update):

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/start"):
            send_message(
                chat_id,
                "🌍 Tilni tanlang:",
                language_keyboard()
            )

    elif "callback_query" in update:
        callback = update["callback_query"]
        data = callback["data"]
        callback_id = callback["id"]
        message = callback["message"]

        chat_id = message["chat"]["id"]
        message_id = message["message_id"]

        if data.startswith("lang_"):
            lang = data.replace("lang_", "")

            if lang in TEXTS:
                telegram(
                    "answerCallbackQuery",
                    {"callback_query_id": callback_id}
                )

                edit_message(
                    chat_id,
                    message_id,
                    TEXTS[lang]["welcome"],
                    main_keyboard(lang)
                )


def main():
    offset = 0

    print("Mafia Noir bot ishga tushdi...")

    while True:
        try:
            result = telegram(
                "getUpdates",
                {
                    "offset": offset,
                    "timeout": 30
                }
            )

            if not result.get("ok"):
                continue

            for update in result.get("result", []):
                offset = update["update_id"] + 1

                try:
                    handle_update(update)
                except Exception as e:
                    print("Update xatosi:", e)

        except Exception as e:
            print("Bot xatosi:", e)


if __name__ == "__main__":
    main()
