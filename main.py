import os
import json
import random
import asyncio
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    BotCommandScopeAllGroupChats,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("data.json")

OWNER_ID = 8402159260
OWNER_USERNAME = "Umarov_uuu"
BOT_USERNAME = "Noiruzbot"

ACTIVE_GAMES = {}

NIGHT_SECONDS = 45
VOTE_SECONDS = 30
DAWN_DELAY = 12

NIGHT_IMAGE_URL = (
    "https://cdn.pixabay.com/photo/2016/11/29/03/53/"
    "architecture-1868667_1280.jpg"
)


# ============================================================
# DATA
# ============================================================

ITEMS = {
    "shield": ("🛡 Qora qalqon", 200, "dollar"),
    "document": ("📜 Soxta hujjat", 1, "diamond"),
    "forgiveness": ("⚖️ Afv tamg‘asi", 150, "dollar"),
    "killer_mask": ("🩸 Qotil niqobi", 150, "dollar"),
    "gun": ("🔫 Noir miltig‘i", 1, "diamond"),
    "black_medicine": ("💊 Qora dori", 250, "dollar"),
    "verbena": ("🧪 Verbena ekstrakti", 300, "dollar"),
    "mystery_mask": ("🥷 Sirli niqob", 2, "diamond"),
    "hero_protection": ("🛡️ Geroydan himoya", 6, "diamond"),
    "hero": ("⚔️ Geroy", 90, "diamond"),
    "active_role": ("🃏 Faol rol", 3, "diamond"),
}


def load_data():
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def get_default_user(user_id):
    return {
        "dollar": 0,
        "diamond": 0,
        "vip": user_id == OWNER_ID,
        "hero": 0,
        "hero_xp": 0,
        "hero_wins": 0,
        "active_role": 0,
        "games": 0,
        "wins": 0,
        "items": {
            k: 0 for k in ITEMS if k not in ("hero", "active_role")
        },
        "active_items": {
            k: False for k in ITEMS if k not in ("hero", "active_role")
        },
    }


def get_user_data(user_id):
    data = load_data()
    uid = str(user_id)

    if not isinstance(data.get(uid), dict):
        data[uid] = get_default_user(user_id)

    user = data[uid]
    user.setdefault("dollar", 0)
    user.setdefault("diamond", 0)
    user["vip"] = user_id == OWNER_ID
    user.setdefault("hero", 0)
    user.setdefault("hero_xp", 0)
    user.setdefault("hero_wins", 0)
    user.setdefault("active_role", 0)
    user.setdefault("games", 0)
    user.setdefault("wins", 0)

    if not isinstance(user.get("items"), dict):
        user["items"] = {}
    if not isinstance(user.get("active_items"), dict):
        user["active_items"] = {}

    for key in ITEMS:
        if key in ("hero", "active_role"):
            continue
        user["items"].setdefault(key, 0)
        user["active_items"].setdefault(key, False)

    data[uid] = user
    save_data(data)
    return data, user


# ============================================================
# ROLES
# ============================================================

ROLES = [
    ("🎩 Don", "don"),
    ("🥷 Mafia", "mafia"),
    ("🎭 Aferist", "aferist"),
    ("🔪 Qotil", "qotil"),
    ("👮 Komissar", "komissar"),
    ("👨‍⚕️ Doktor", "doktor"),
    ("👮‍♂️ Serjant", "serjant"),
    ("🎖️ Kapitan", "kapitan"),
    ("👤 Fuqaro", "fuqaro"),
    ("👣 Daydi", "daydi"),
    ("⚖️ Sudya", "sudya"),
    ("👨‍⚖️ Advokat", "advokat"),
    ("💀 Qasoskor", "qasoskor"),
    ("🦎 Buqalamun", "buqalamun"),
    ("🕵️ Kuzatuvchi", "kuzatuvchi"),
    ("🛡️ Bodyguard", "bodyguard"),
    ("🧙 Sehrgar", "sehrgar"),
    ("📰 Jurnalist", "jurnalist"),
    ("🔬 Kimyogar", "kimyogar"),
    ("💣 Minyor", "minyor"),
    ("⚡ Koldun", "koldun"),
    ("🕶️ Maxfiy agent", "agent"),
    ("👻 Arvoh", "arvoh"),
    ("🤡 Joker", "joker"),
    ("🧛 Vampir", "vampir"),
]

MAFIA_ROLES = {"don", "mafia"}

ROLE_DESCRIPTIONS = {
    "don": "Mafiya sardori. Tunda o‘z o‘ljangizni tanlaysiz.",
    "mafia": "Mafia jamoasi bilan tunda harakat qilasiz.",
    "aferist": "Aldov va hiyla orqali omon qolishga urinadi.",
    "qotil": "Mustaqil qotil. Tunda o‘z nishonini tanlaydi.",
    "komissar": "Tunda o‘ldirish yoki tekshirish imkoniga ega.",
    "doktor": "Tunda bir o‘yinchini himoya qiladi.",
    "serjant": "Komissar halok bo‘lsa, uning o‘rnini egallaydi.",
    "kapitan": "Tunda maxsus himoya harakatini bajaradi.",
    "fuqaro": "Tinch aholi jamoasi tarafida.",
    "daydi": "Tunda bir o‘yinchining oldiga boradi.",
    "sudya": "Kunduzgi ovoz berishda maxsus imkoniyatga ega.",
    "advokat": "Kunduzgi jarayonda himoya qilishga yordam beradi.",
    "qasoskor": "Tunda maxsus qasos harakatiga ega.",
    "buqalamun": "O‘z rolini yashirishga qodir.",
    "kuzatuvchi": "Tunda o‘yinchilar harakatini kuzatadi.",
    "bodyguard": "Tunda bir o‘yinchini himoya qiladi.",
    "sehrgar": "Tunda maxsus sehr ishlatadi.",
    "jurnalist": "Muhim ma’lumotlarni aniqlashga harakat qiladi.",
    "kimyogar": "Tunda maxsus moddalardan foydalanadi.",
    "minyor": "Tunda maxsus tuzoq qo‘yadi.",
    "koldun": "Sirli kuchlardan foydalanadi.",
    "agent": "Yashirin kuzatuv olib boradi.",
    "arvoh": "O‘lgandan keyin maxsus ta’sirga ega.",
    "joker": "O‘yinni chalkashtiruvchi mustaqil rol.",
    "vampir": "Tunda mustaqil ravishda nishon tanlaydi.",
}

# Kelishilgan asosiy tunda harakat qiluvchi rollar.
# Serjant oddiy tunlarda harakat qilmaydi.
NIGHT_ACTION_ROLES = {
    "don", "mafia", "qotil", "komissar", "doktor", "kapitan",
    "daydi", "qasoskor", "buqalamun", "kuzatuvchi", "bodyguard",
    "sehrgar", "kimyogar", "minyor", "koldun", "agent", "vampir"
}


def role_name(role_key):
    for name, key in ROLES:
        if key == role_key:
            return name
    return role_key


def get_roles_for_player_count(count):
    if count <= 6:
        return ["don", "mafia", "komissar", "doktor", "qotil", "fuqaro"]
    if count <= 10:
        return [
            "don", "mafia", "komissar", "doktor", "qotil",
            "serjant", "fuqaro", "daydi", "bodyguard", "fuqaro"
        ]
    if count <= 15:
        return [
            "don", "mafia", "aferist", "qotil", "komissar", "doktor",
            "serjant", "kapitan", "fuqaro", "daydi", "sudya",
            "advokat", "qasoskor", "buqalamun", "kuzatuvchi"
        ]
    if count <= 20:
        return [
            "don", "mafia", "aferist", "qotil", "komissar", "doktor",
            "serjant", "kapitan", "fuqaro", "daydi", "sudya",
            "advokat", "qasoskor", "buqalamun", "kuzatuvchi",
            "bodyguard", "sehrgar", "jurnalist", "kimyogar", "minyor"
        ]
    return [key for _, key in ROLES]


def make_random_roles(count):
    pool = get_roles_for_player_count(count)
    if len(pool) < count:
        result = pool[:]
        while len(result) < count:
            result.append(random.choice(pool))
        random.shuffle(result)
        return result

    result = random.sample(pool, count)

    # Kichik o‘yinda Komissar va Don tushishini ta’minlash.
    if count >= 5 and "komissar" not in result:
        replace_at = random.randrange(len(result))
        result[replace_at] = "komissar"
    if "don" not in result:
        replace_at = random.randrange(len(result))
        result[replace_at] = "don"

    random.shuffle(result)
    return result


# ============================================================
# COMMON BUTTONS / PROFILE
# ============================================================

def bot_button():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Botga o'tish", url=f"https://t.me/{BOT_USERNAME}")
    ]])


def group_button(chat_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Guruhga o'tish",
            url=f"https://t.me/{BOT_USERNAME}?start=group_{chat_id}"
        )
    ]])


def user_link(user_id, name):
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def get_profile_text(user):
    _, data = get_user_data(user.id)
    games = data["games"]
    wins = data["wins"]
    percent = int(wins * 100 / games) if games else 0

    return (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {user.first_name or 'Noma’lum'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💵 Dollar: {data['dollar']}\n"
        f"💎 Olmos: {data['diamond']}\n\n"
        f"🛡 Qora qalqon: {data['items']['shield']}\n"
        f"📜 Soxta hujjat: {data['items']['document']}\n"
        f"⚖️ Afv tamg‘asi: {data['items']['forgiveness']}\n"
        f"🩸 Qotil niqobi: {data['items']['killer_mask']}\n"
        f"🔫 Noir miltig‘i: {data['items']['gun']}\n"
        f"💊 Qora dori: {data['items']['black_medicine']}\n"
        f"🧪 Verbena ekstrakti: {data['items']['verbena']}\n"
        f"🥷 Sirli niqob: {data['items']['mystery_mask']}\n"
        f"🛡️ Geroydan himoya: {data['items']['hero_protection']}\n\n"
        f"⚔️ Geroy: {'Bor' if data['hero'] else 'Yo‘q'}\n"
        f"🃏 Faol rol: {'Bor' if data['active_role'] else 'Yo‘q'}\n\n"
        f"🎯 G‘alabalar: {wins}\n"
        f"🎲 Barcha o‘yinlar: {games}\n"
        f"📊 G‘alaba foizi: {percent}%\n"
        f"⭐ XP: {data['hero_xp']}"
    )


def profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar_exchange")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="diamond_buy")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items_info")],
        [InlineKeyboardButton("🔻", callback_data="item_control")],
    ])


async def profile(update, context):
    if not update.message:
        return
    await update.message.reply_text(
        get_profile_text(update.effective_user),
        reply_markup=profile_buttons()
    )


# ============================================================
# REGISTRATION
# ============================================================

def registration_text(game):
    players = game["players"]
    lines = ["Ro‘yxatdan o‘tish davom etmoqda!", "Ro‘yxatdan o‘tganlar:", ""]
    names = [
        user_link(uid, p.get("name", "Noma’lum"))
        for uid, p in players.items()
    ]
    for i in range(0, len(names), 4):
        lines.append(", ".join(names[i:i + 4]))
    lines += ["", f"Jami: {len(players)} ta"]
    return "\n".join(lines)


def join_button(chat_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "➕ Qo‘shilish",
            url=f"https://t.me/{BOT_USERNAME}?start=join_{chat_id}"
        )
    ]])


async def start(update, context):
    if not update.message:
        return

    if context.args and context.args[0].startswith("join_"):
        await register_player(update, context)
        return

    await update.message.reply_text(
        "🌍 Tilni tanlang:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        ])
    )


async def language_button(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.edit_text(
        "🖤 Salom! Xush kelibsiz!\n\n"
        "🌃 Men Mafia Noir botiman. "
        "Mafia o‘ynash uchun meni guruhingizga qo‘shing.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Owner 🎩", url=f"https://t.me/{OWNER_USERNAME}")],
            [InlineKeyboardButton("Asosiy guruh 👥", url="https://t.me/+ABdv1H2Z2_llYWYy")],
            [InlineKeyboardButton("Guruhga qo‘shish ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        ])
    )


async def gamecreate(update, context):
    if not update.message or update.effective_chat.type not in ("group", "supergroup"):
        return

    chat_id = update.effective_chat.id
    old = ACTIVE_GAMES.get(chat_id)

    if old and old.get("message_id"):
        try:
            await context.bot.delete_message(chat_id, old["message_id"])
        except Exception:
            pass

    old_players = dict(old.get("players", {})) if old else {}

    game = {
        "chat_id": chat_id,
        "message_id": None,
        "players": old_players,
        "started": False,
        "phase": "registration",
        "roles": {},
        "night_actions": {},
        "night_results": {},
        "night_messages": {},
        "votes": {},
        "vote_message_id": None,
        "vote_started": False,
        "winner": None,
    }

    msg = await context.bot.send_message(
        chat_id,
        registration_text(game),
        reply_markup=join_button(chat_id),
        parse_mode="HTML"
    )
    game["message_id"] = msg.message_id
    ACTIVE_GAMES[chat_id] = game

    try:
        await context.bot.pin_chat_message(chat_id, msg.message_id, disable_notification=True)
    except Exception:
        pass


async def register_player(update, context):
    if not update.message or not context.args:
        return

    try:
        chat_id = int(context.args[0].replace("join_", "", 1))
    except ValueError:
        await update.message.reply_text("❌ O‘yin topilmadi.")
        return

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["started"]:
        await update.message.reply_text("❌ Bu o‘yinga qo‘shilish mumkin emas.")
        return

    if len(game["players"]) >= 25:
        await update.message.reply_text("❌ O‘yin 25 ta o‘yinchidan oshmaydi.")
        return

    uid = str(update.effective_user.id)
    if uid in game["players"]:
        await update.message.reply_text("ℹ️ Siz allaqachon ro‘yxatdan o‘tgansiz.")
        return

    name = update.effective_user.first_name or update.effective_user.username or "Noma’lum"
    game["players"][uid] = {"name": name}

    await update.message.reply_text("✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!")

    try:
        await context.bot.edit_message_text(
            chat_id,
            game["message_id"],
            registration_text(game),
            reply_markup=join_button(chat_id),
            parse_mode="HTML"
        )
    except Exception:
        pass


# ============================================================
# NIGHT
# ============================================================

def alive_ids(game):
    return [
        uid for uid in game["players"]
        if game["roles"].get(uid, {}).get("alive", False)
    ]


def alive_keyboard(game, actor_id, prefix="nighttarget"):
    rows = []
    for uid in alive_ids(game):
        if uid == str(actor_id):
            continue
        name = game["players"][uid].get("name", "Noma’lum")
        rows.append([InlineKeyboardButton(
            name,
            callback_data=f"{prefix}_{game['chat_id']}_{actor_id}_{uid}"
        )])
    return InlineKeyboardMarkup(rows)


def action_text(role):
    return {
        "don": "Kimni o‘ldirasiz?",
        "mafia": "Kimni o‘ldirasiz?",
        "qotil": "Kimni o‘ldirasiz?",
        "doktor": "Kimni davolaysiz?",
        "kapitan": "Kimni himoya qilasiz?",
        "daydi": "Kimning oldiga borasiz?",
        "qasoskor": "Kimdan qasos olasiz?",
        "buqalamun": "Kimning rolini yashirasiz?",
        "kuzatuvchi": "Kimni kuzatasiz?",
        "bodyguard": "Kimni himoya qilasiz?",
        "sehrgar": "Kimga sehr ishlatasiz?",
        "kimyogar": "Kimga dori ishlatasiz?",
        "minyor": "Kimga tuzoq qo‘yasiz?",
        "koldun": "Kimga sehr ishlatasiz?",
        "agent": "Kimni kuzatasiz?",
        "vampir": "Kimni tishlaysiz?",
    }.get(role, "Kimni tanlaysiz?")


def commissioner_buttons(chat_id, player_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("O‘ldirish", callback_data=f"commkill_{chat_id}_{player_id}"),
        InlineKeyboardButton("Tekshirish", callback_data=f"commcheck_{chat_id}_{player_id}")
    ]])


async def gamestart(update, context):
    if not update.message or update.effective_chat.type not in ("group", "supergroup"):
        return

    chat_id = update.effective_chat.id
    game = ACTIVE_GAMES.get(chat_id)

    if not game or game["started"]:
        await update.message.reply_text("❌ Faol boshlanmagan o‘yin topilmadi.")
        return

    if len(game["players"]) < 5:
        await update.message.reply_text("❌ O‘yin boshlanishi uchun kamida 5 ta o‘yinchi kerak.")
        return

    game["started"] = True
    game["phase"] = "night"

    selected_roles = make_random_roles(len(game["players"]))

    for uid, role_key in zip(game["players"], selected_roles):
        game["roles"][uid] = {
            "role_key": role_key,
            "role_name": role_name(role_key),
            "alive": True,
            "is_original_commissioner": role_key == "komissar",
        }

    await context.bot.send_message(
        chat_id,
        "O‘yin boshlandi!",
        reply_markup=bot_button()
    )

    await context.bot.send_photo(
        chat_id,
        NIGHT_IMAGE_URL,
        caption=(
            "🌙 Tun boshlandi.\n\n"
            "Shaharni qorong‘ulik qopladi. "
            "Ko‘chalarda sukunat hukm surmoqda...\n\n"
            "Kimdir bu tunda so‘nggi qadamini tashlashi mumkin."
        ),
        reply_markup=bot_button()
    )

    for uid, r in game["roles"].items():
        try:
            text = (
                f"Siz — {r['role_name']}!\n\n"
                f"{ROLE_DESCRIPTIONS.get(r['role_key'], '')}"
            )
            await context.bot.send_message(
                int(uid), text, reply_markup=group_button(chat_id)
            )
        except Exception:
            pass

    await start_night_actions(game, context)
    ACTIVE_GAMES[chat_id] = game

    asyncio.create_task(night_timer(chat_id, context))


async def start_night_actions(game, context):
    chat_id = game["chat_id"]

    # Don/Komissar/mafia va boshqa rollarga shaxsiy tanlov.
    # Serjant bu yerda ataylab chaqirilmaydi.
    for uid, r in game["roles"].items():
        if not r["alive"]:
            continue

        role = r["role_key"]
        if role not in NIGHT_ACTION_ROLES:
            continue

        try:
            if role == "komissar":
                msg = await context.bot.send_message(
                    int(uid),
                    "Nima qilasiz?",
                    reply_markup=commissioner_buttons(chat_id, uid)
                )
            else:
                msg = await context.bot.send_message(
                    int(uid),
                    action_text(role),
                    reply_markup=alive_keyboard(game, uid)
                )
            game["night_messages"][uid] = msg.message_id
        except Exception:
            pass


async def night_timer(chat_id, context):
    for _ in range(NIGHT_SECONDS):
        await asyncio.sleep(1)
        game = ACTIVE_GAMES.get(chat_id)
        if not game or game["phase"] != "night":
            return

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["phase"] != "night":
        return

    await resolve_night(game, context)
    ACTIVE_GAMES[chat_id] = game


async def resolve_night(game, context):
    chat_id = game["chat_id"]

    kills = []
    saves = set()

    for actor, action in game["night_actions"].items():
        role = game["roles"].get(actor, {}).get("role_key")
        target = action.get("target")
        if not target or target not in game["roles"]:
            continue

        if role in {"don", "mafia", "qotil", "vampir"}:
            if role == "vampir":
                # Vampir ham tunlik hujum qiladi.
                kills.append((target, "Vampir"))
            else:
                kills.append((target, role))

        elif role in {"doktor", "bodyguard", "kapitan"}:
            saves.add(target)

        elif role == "komissar" and action.get("kind") == "kill":
            kills.append((target, "Komissar"))

    # Birinchi navbatda himoyalar ishlaydi.
    deaths = []
    for target, source in kills:
        if target in saves:
            continue
        if target not in deaths:
            deaths.append(target)

    # O‘ldirilganlarning tirikligi yangilanadi.
    for uid in deaths:
        if uid in game["roles"]:
            game["roles"][uid]["alive"] = False

    # Komissar o‘lsa, Serjant uning o‘rnini egallaydi.
    commissioner_dead = any(
        r.get("role_key") == "komissar" and not r.get("alive", True)
        for r in game["roles"].values()
    )

    if commissioner_dead:
        for uid, r in game["roles"].items():
            if r.get("role_key") == "serjant" and r.get("alive", True):
                r["role_key"] = "komissar"
                r["role_name"] = "👮 Komissar"
                r["is_original_commissioner"] = False
                break

    await send_dawn(game, context, deaths)
    game["phase"] = "vote_wait"
    ACTIVE_GAMES[chat_id] = game

    asyncio.create_task(start_vote_after_delay(chat_id, context))


async def send_dawn(game, context, deaths):
    chat_id = game["chat_id"]

    await context.bot.send_message(
        chat_id,
        "🌝 Xayrli tong!\n"
        "🌄 Kun: 1\n\n"
        "Shamollar tundagi sirlarni butun shaharga yetkazmoqda..."
    )

    if deaths:
        lines = ["Tunda o‘ldirilganlar:", ""]
        for uid in deaths:
            name = game["players"][uid]["name"]
            killer = "Don"
            for actor, action in game["night_actions"].items():
                if action.get("target") == uid:
                    r = game["roles"].get(actor, {}).get("role_key")
                    if r in {"don", "mafia", "qotil", "vampir", "komissar"}:
                        killer = role_name(r)
                        break
            lines.append(
                f"Tunda {game['roles'][uid]['role_name']} "
                f"{user_link(uid, name)} vaxshiylarcha o‘ldirildi. "
                f"Aytishlaricha, unikiga {killer} kelgan."
            )
        await context.bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")
    else:
        await context.bot.send_message(
            chat_id,
            "Tunda o‘ldirilganlar:\n\n"
            "Bu tun hech kim halok bo‘lmadi."
        )

    alive = alive_ids(game)
    lines = ["Tirik o‘yinchilar:", ""]
    for i, uid in enumerate(alive, 1):
        lines.append(f"{i}. {user_link(uid, game['players'][uid]['name'])}")

    lines += [
        "",
        "— Tinchlar",
        "— Mafiyalar",
        "",
        f"Jami: {len(alive)} ta",
        "",
        "Endi kechaning natijalarini muhokama qilamiz..."
    ]

    await context.bot.send_message(
        chat_id,
        "\n".join(lines),
        parse_mode="HTML"
    )


# ============================================================
# NIGHT CALLBACKS
# ============================================================

async def night_target(update, context):
    q = update.callback_query
    parts = q.data.split("_")
    if len(parts) != 4:
        await q.answer("❌ Xatolik", show_alert=True)
        return

    chat_id = int(parts[1])
    actor = str(parts[2])
    target = str(parts[3])

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["phase"] != "night":
        await q.answer("❌ Tun tugagan.", show_alert=True)
        return

    if actor != str(q.from_user.id):
        await q.answer("❌ Bu tanlov sizga tegishli emas.", show_alert=True)
        return

    if target not in alive_ids(game):
        await q.answer("❌ Bu o‘yinchi tirik emas.", show_alert=True)
        return

    role = game["roles"][actor]["role_key"]

    if role == "komissar":
        await q.answer("Avval o‘ldirish yoki tekshirishni tanlang.", show_alert=True)
        return

    game["night_actions"][actor] = {
        "target": target,
        "kind": "action"
    }

    await q.answer("Tanlov qabul qilindi.")

    mid = game["night_messages"].get(actor)
    if mid:
        try:
            await context.bot.edit_message_text(
                int(actor),
                mid,
                f"{action_text(role)}\n\n"
                f"Tanlov: {game['players'][target]['name']}"
            )
        except Exception:
            pass


async def commissioner_action(update, context):
    q = update.callback_query
    parts = q.data.split("_")
    if len(parts) != 3:
        await q.answer("❌ Xatolik", show_alert=True)
        return

    chat_id = int(parts[1])
    actor = str(parts[2])
    game = ACTIVE_GAMES.get(chat_id)

    if not game or game["phase"] != "night":
        await q.answer("❌ Tun tugagan.", show_alert=True)
        return

    if actor != str(q.from_user.id):
        await q.answer("❌ Bu tanlov sizga tegishli emas.", show_alert=True)
        return

    role = game["roles"].get(actor, {}).get("role_key")
    if role != "komissar":
        await q.answer("❌ Siz Komissar emassiz.", show_alert=True)
        return

    kind = "kill" if q.data.startswith("commkill_") else "check"
    game["commissioner_mode"] = {actor: kind}

    await q.answer("Tanlov qabul qilindi.")

    mid = game["night_messages"].get(actor)
    if mid:
        try:
            await context.bot.edit_message_text(
                int(actor),
                mid,
                "Kimni o‘ldirasiz?" if kind == "kill" else "Kimni tekshirasiz?",
                reply_markup=alive_keyboard(game, actor, "commtarget")
            )
        except Exception:
            pass


async def commissioner_target(update, context):
    q = update.callback_query
    parts = q.data.split("_")
    if len(parts) != 4:
        await q.answer("❌ Xatolik", show_alert=True)
        return

    chat_id = int(parts[1])
    actor = str(parts[2])
    target = str(parts[3])

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["phase"] != "night":
        await q.answer("❌ Tun tugagan.", show_alert=True)
        return

    if actor != str(q.from_user.id) or target not in alive_ids(game):
        await q.answer("❌ Tanlov mumkin emas.", show_alert=True)
        return

    kind = game.get("commissioner_mode", {}).get(actor)
    if kind not in {"kill", "check"}:
        await q.answer("Avval amalni tanlang.", show_alert=True)
        return

    game["night_actions"][actor] = {
        "target": target,
        "kind": kind
    }

    await q.answer("Tanlov qabul qilindi.")

    mid = game["night_messages"].get(actor)

    if kind == "check":
        target_role = game["roles"][target]["role_name"]
        text = (
            "Kimni tekshirasiz?\n\n"
            f"{user_link(target, game['players'][target]['name'])} — {target_role}"
        )
        if mid:
            try:
                await context.bot.edit_message_text(
                    int(actor), mid, text, parse_mode="HTML"
                )
            except Exception:
                pass
    else:
        text = (
            "Kimni o‘ldirasiz?\n\n"
            f"Tanlandi: {game['players'][target]['name']}"
        )
        if mid:
            try:
                await context.bot.edit_message_text(int(actor), mid, text)
            except Exception:
                pass


# ============================================================
# VOTING
# ============================================================

async def start_vote_after_delay(chat_id, context):
    await asyncio.sleep(DAWN_DELAY)

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["phase"] != "vote_wait":
        return

    game["phase"] = "voting"
    game["votes"] = {}

    msg = await context.bot.send_message(
        chat_id,
        "Aybdorlarni aniqlash va jazolash vaqti keldi.\n\n"
        "Ovoz berish boshlandi.\n"
        "Ovoz berish uchun 30 sekund",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Botga o'tish", url=f"https://t.me/{BOT_USERNAME}")
        ]])
    )

    game["vote_message_id"] = msg.message_id
    ACTIVE_GAMES[chat_id] = game

    # Botga o'tish tugmasi orqali shaxsiy ovoz berish.
    for uid in alive_ids(game):
        try:
            await context.bot.send_message(
                int(uid),
                "Kimga ovoz berasiz?",
                reply_markup=vote_keyboard(game, uid)
            )
        except Exception:
            pass

    asyncio.create_task(vote_timer(chat_id, context))


def vote_keyboard(game, voter_id):
    rows = []
    for uid in alive_ids(game):
        if uid == str(voter_id):
            continue
        rows.append([InlineKeyboardButton(
            game["players"][uid]["name"],
            callback_data=f"vote_{game['chat_id']}_{voter_id}_{uid}"
        )])
    return InlineKeyboardMarkup(rows)


async def vote_timer(chat_id, context):
    await asyncio.sleep(VOTE_SECONDS)

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["phase"] != "voting":
        return

    await finish_voting(game, context)


async def vote_callback(update, context):
    q = update.callback_query
    parts = q.data.split("_")
    if len(parts) != 4:
        await q.answer("❌ Xatolik", show_alert=True)
        return

    chat_id = int(parts[1])
    voter = str(parts[2])
    target = str(parts[3])

    game = ACTIVE_GAMES.get(chat_id)

    if not game or game["phase"] != "voting":
        await q.answer("❌ Ovoz berish tugagan.", show_alert=True)
        return

    if voter != str(q.from_user.id):
        await q.answer("❌ Bu ovoz sizniki emas.", show_alert=True)
        return

    if voter not in alive_ids(game) or target not in alive_ids(game):
        await q.answer("❌ Ovoz berish mumkin emas.", show_alert=True)
        return

    game["votes"][voter] = target
    await q.answer("Ovozingiz qabul qilindi.")

    try:
        await q.message.edit_text(
            f"Kimga ovoz berasiz?\n\n"
            f"Tanlovingiz: {game['players'][target]['name']}"
        )
    except Exception:
        pass


async def finish_voting(game, context):
    chat_id = game["chat_id"]
    game["phase"] = "vote_result"

    counts = {}
    for target in game["votes"].values():
        counts[target] = counts.get(target, 0) + 1

    if not counts:
        await context.bot.send_message(
            chat_id,
            "Ovozlar yetarli bo‘lmadi.\n\n"
            "Hech kim kunduzgi yig‘ilishda hukm qilinmadi."
        )
        await next_round_or_end(game, context)
        return

    highest = max(counts.values())
    leaders = [uid for uid, n in counts.items() if n == highest]

    if len(leaders) != 1:
        await context.bot.send_message(
            chat_id,
            "Ovozlar yakunlandi.\n\n"
            "Bir nechta o‘yinchi bir xil ovoz oldi. "
            "Bu safar hech kim hukm qilinmadi."
        )
        await next_round_or_end(game, context)
        return

    target = leaders[0]
    target_name = game["players"][target]["name"]

    confirm = await context.bot.send_message(
        chat_id,
        f"⚖️ {user_link(target, target_name)} bo‘yicha "
        f"kunduzgi hukm tayyor.\n\n"
        "Hukmni tasdiqlang.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✓", callback_data=f"confirm_{chat_id}_{target}"),
            InlineKeyboardButton("X", callback_data=f"cancel_{chat_id}_{target}")
        ]])
    )
    game["confirm_message_id"] = confirm.message_id
    ACTIVE_GAMES[chat_id] = game

    asyncio.create_task(confirm_timer(chat_id, context))


async def confirm_timer(chat_id, context):
    await asyncio.sleep(VOTE_SECONDS)

    game = ACTIVE_GAMES.get(chat_id)
    if not game or game["phase"] != "vote_result":
        return

    # Ulgurilmasa ham keyingi bosqichga o‘tadi.
    await apply_execution(game, context)


async def confirm_callback(update, context):
    q = update.callback_query
    parts = q.data.split("_")
    if len(parts) != 3:
        await q.answer("❌ Xatolik", show_alert=True)
        return

    chat_id = int(parts[1])
    target = str(parts[2])
    game = ACTIVE_GAMES.get(chat_id)

    if not game or game["phase"] != "vote_result":
        await q.answer("❌ Hukm vaqti tugagan.", show_alert=True)
        return

    if q.data.startswith("cancel_"):
        await q.answer("Hukm bekor qilindi.")
        game["phase"] = "vote_wait"
        ACTIVE_GAMES[chat_id] = game
        try:
            await q.message.edit_text("Hukm bekor qilindi. O‘yin davom etadi.")
        except Exception:
            pass
        await next_round_or_end(game, context)
        return

    await q.answer("Hukm tasdiqlandi.")
    await apply_execution(game, context, target)


async def apply_execution(game, context, target=None):
    chat_id = game["chat_id"]

    if target is None:
        target = game.get("last_execution_target")
        if target is None:
            # Confirm xabaridagi targetni topish uchun message matni yetarli emas.
            # Agar mavjud bo‘lsa, ovozlar ichidan yagona lider olinadi.
            counts = {}
            for uid in game["votes"].values():
                counts[uid] = counts.get(uid, 0) + 1
            if counts:
                highest = max(counts.values())
                leaders = [u for u, n in counts.items() if n == highest]
                if len(leaders) == 1:
                    target = leaders[0]

    if not target or target not in game["roles"]:
        await next_round_or_end(game, context)
        return

    game["last_execution_target"] = target
    game["roles"][target]["alive"] = False

    target_name = game["players"][target]["name"]
    target_role = game["roles"][target]["role_name"]

    total = sum(1 for v in game["votes"].values() if v == target)
    abstain = max(0, len(alive_ids(game)) - 1 - len(game["votes"]))

    await context.bot.send_message(
        chat_id,
        "Ovoz berish natijalari:\n"
        f"✓ {total} ta ovoz  X {abstain} ta ovoz\n\n"
        f"{user_link(target, target_name)} kunduzgi yig‘ilishda osildi!\n"
        f"U edi — {target_role}.",
        parse_mode="HTML"
    )

    await next_round_or_end(game, context)


# ============================================================
# WIN / END / REWARD
# ============================================================

def winner_for(game):
    alive = alive_ids(game)
    mafia = [
        uid for uid in alive
        if game["roles"][uid]["role_key"] in MAFIA_ROLES
    ]
    non_mafia = [
        uid for uid in alive
        if game["roles"][uid]["role_key"] not in MAFIA_ROLES
    ]

    if not mafia:
        return "town"
    if len(mafia) >= len(non_mafia):
        return "mafia"
    return None


def calculate_xp(game, uid, winner):
    role = game["roles"][uid]["role_key"]
    alive = game["roles"][uid]["alive"]

    # Maksimum 30. 30 faqat juda yaxshi natija uchun.
    score = 4

    if alive:
        score += 3
    if winner == "mafia" and role in MAFIA_ROLES:
        score += 8
    elif winner == "town" and role not in MAFIA_ROLES:
        score += 8

    actions = game.get("night_actions", {})
    if uid in actions:
        score += 3

    # Komissarning to‘g‘ri harakati, Donning hujumi kabi foydali harakatlar.
    if role == "komissar" and uid in actions:
        score += 5

    if score > 30:
        score = 30
    return score


async def next_round_or_end(game, context):
    result = winner_for(game)

    if result:
        await finish_game(game, context, result)
        return

    # Keyingi tun.
    game["phase"] = "night"
    game["night_actions"] = {}
    game["night_messages"] = {}
    game["commissioner_mode"] = {}
    game["votes"] = {}

    await context.bot.send_message(
        game["chat_id"],
        "🌙 Tun yana shaharni qopladi..."
    )

    await start_night_actions(game, context)
    ACTIVE_GAMES[game["chat_id"]] = game
    asyncio.create_task(night_timer(game["chat_id"], context))


async def finish_game(game, context, winner):
    chat_id = game["chat_id"]
    game["phase"] = "finished"
    game["winner"] = winner
    ACTIVE_GAMES[chat_id] = game

    winner_text = "Tinch aholi g‘alaba qozondi!" if winner == "town" else "Mafia g‘alaba qozondi!"

    await context.bot.send_message(
        chat_id,
        f"🏁 O‘yin tugadi.\n\n{winner_text}"
    )

    data = load_data()

    for uid, p in game["players"].items():
        user_data = data.get(uid, get_default_user(int(uid)))
        user_data.setdefault("dollar", 0)
        user_data.setdefault("diamond", 0)
        user_data.setdefault("games", 0)
        user_data.setdefault("wins", 0)
        user_data.setdefault("hero_xp", 0)

        user_data["games"] += 1

        role = game["roles"][uid]["role_key"]
        player_won = (
            winner == "mafia" and role in MAFIA_ROLES
        ) or (
            winner == "town" and role not in MAFIA_ROLES
        )

        dollar_reward = 70 if player_won else 20
        xp_reward = calculate_xp(game, uid, winner)

        user_data["dollar"] += dollar_reward

        if player_won:
            user_data["wins"] += 1
            user_data["hero_wins"] = user_data.get("hero_wins", 0) + 1

        user_data["hero_xp"] = min(
            user_data.get("hero_xp", 0) + xp_reward,
            1500
        )

        data[uid] = user_data

        # O‘yin tugagach aynan bizning profilimiz.
        try:
            await context.bot.send_message(
                int(uid),
                (
                    "🏁 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
                    f"👤 {p['name']}\n\n"
                    f"🎭 Rol: {game['roles'][uid]['role_name']}\n"
                    f"{'🏆 G‘alaba' if player_won else '❌ Mag‘lubiyat'}\n\n"
                    f"💵 O‘yin mukofoti: +{dollar_reward}\n"
                    f"⭐ XP: +{xp_reward}\n\n"
                    f"💵 Dollar: {user_data['dollar']}\n"
                    f"💎 Olmos: {user_data['diamond']}\n"
                    f"🎯 G‘alabalar: {user_data['wins']}\n"
                    f"🎲 Barcha o‘yinlar: {user_data['games']}\n"
                    f"⭐ XP: {user_data['hero_xp']}"
                ),
                reply_markup=profile_buttons()
            )
        except Exception:
            pass

    save_data(data)


# ============================================================
# ROLES COMMAND
# ============================================================

def roles_buttons():
    rows = []
    for i in range(0, len(ROLES), 2):
        row = [InlineKeyboardButton(ROLES[i][0], callback_data=f"role_{ROLES[i][1]}")]
        if i + 1 < len(ROLES):
            row.append(InlineKeyboardButton(ROLES[i + 1][0], callback_data=f"role_{ROLES[i + 1][1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)


async def roles(update, context):
    if update.message:
        await update.message.reply_text(
            "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n"
            "Kerakli rolni tanlang:",
            reply_markup=roles_buttons()
        )


async def role_button(update, context):
    q = update.callback_query
    key = q.data.replace("role_", "", 1)
    if key not in {k for _, k in ROLES}:
        await q.answer("❌ Rol topilmadi.", show_alert=True)
        return
    await q.answer(
        f"{role_name(key)}\n\n{ROLE_DESCRIPTIONS.get(key, '')}",
        show_alert=True
    )


# ============================================================
# SIMPLE SHOP / PROFILE CALLBACKS
# ============================================================

DOLLAR_PACKAGES = [(1, 600), (2, 1200), (3, 1800), (5, 3000), (10, 6000), (20, 12000)]
DIAMOND_PACKAGES = [(5, 4000), (10, 8000), (25, 20000), (50, 40000), (100, 80000)]


async def dollar_exchange(update, context):
    q = update.callback_query
    await q.answer()
    rows = [
        [InlineKeyboardButton(f"💎 {d} → 💵 {money}", callback_data=f"exchange_{d}")]
        for d, money in DOLLAR_PACKAGES
    ]
    rows.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    await q.message.edit_text(
        "💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\nOlmosni Dollarga almashtiring:",
        reply_markup=InlineKeyboardMarkup(rows)
    )


async def exchange_dollar(update, context):
    q = update.callback_query
    amount = int(q.data.split("_")[1])
    data, user = get_user_data(q.from_user.id)

    if q.from_user.id != OWNER_ID:
        if user["diamond"] < amount:
            await q.answer("❌ Olmos yetarli emas.", show_alert=True)
            return
        user["diamond"] -= amount

    user["dollar"] += amount * 600
    save_data(data)
    await q.answer("✅ Amal bajarildi.")
    await q.message.edit_text(get_profile_text(q.from_user), reply_markup=profile_buttons())


async def diamond_buy(update, context):
    q = update.callback_query
    await q.answer()
    rows = []
    for amount, price in DIAMOND_PACKAGES:
        rows.append([InlineKeyboardButton(
            f"💎 {amount} ta — {price:,} so‘m".replace(",", " "),
            url=f"https://t.me/{OWNER_USERNAME}"
        )])
    rows.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    await q.message.edit_text(
        "💎 • 𝑶𝒍𝒎𝒐𝒔 𝒐𝒍𝒊𝒔𝒉 •\n\nKerakli paketni tanlang:",
        reply_markup=InlineKeyboardMarkup(rows)
    )


async def shop(update, context):
    q = update.callback_query
    await q.answer()
    rows = []
    for key, (name, price, currency) in ITEMS.items():
        icon = "💵" if currency == "dollar" else "💎"
        rows.append([InlineKeyboardButton(
            f"{name} — {icon} {price}", callback_data=f"buy_{key}"
        )])
    rows.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    await q.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\nKerakli buyumni tanlang:",
        reply_markup=InlineKeyboardMarkup(rows)
    )


async def buy_item(update, context):
    q = update.callback_query
    key = q.data.replace("buy_", "", 1)
    if key not in ITEMS:
        await q.answer("❌ Xatolik.", show_alert=True)
        return

    name, price, currency = ITEMS[key]
    data, user = get_user_data(q.from_user.id)

    if q.from_user.id != OWNER_ID:
        if user[currency] < price:
            await q.answer("❌ Mablag‘ yetarli emas.", show_alert=True)
            return
        user[currency] -= price

    if key == "hero":
        user["hero"] += 1
    elif key == "active_role":
        user["active_role"] += 1
    else:
        user["items"][key] += 1

    save_data(data)
    await q.answer("✅ Xarid muvaffaqiyatli.")
    await q.message.edit_text(
        "💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n"
        "✅ Xarid muvaffaqiyatli amalga oshirildi.\n\n"
        "Yana buyum tanlang:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
            [InlineKeyboardButton("🔙 Profil", callback_data="profile")]
        ])
    )


async def items_info(update, context):
    q = update.callback_query
    await q.answer()
    text = "📖 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓 𝒉𝒂𝒒𝒊𝒅𝒂 •\n\n"
    for key, (name, _, _) in ITEMS.items():
        text += f"{name} — mavjud buyum.\n"
    await q.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Orqaga", callback_data="profile")]
        ])
    )


async def item_control(update, context):
    q = update.callback_query
    await q.answer()
    _, user = get_user_data(q.from_user.id)
    rows = []
    for key, (name, _, _) in ITEMS.items():
        if key in ("hero", "active_role"):
            continue
        status = "🟢 ON" if user["active_items"][key] else "⚪ OFF"
        rows.append([InlineKeyboardButton(
            f"{name} — {user['items'][key]} | {status}",
            callback_data=f"toggle_{key}"
        )])
    rows.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    await q.message.edit_text(
        "🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •",
        reply_markup=InlineKeyboardMarkup(rows)
    )


async def toggle_item(update, context):
    q = update.callback_query
    key = q.data.replace("toggle_", "", 1)
    data, user = get_user_data(q.from_user.id)

    if user["items"].get(key, 0) <= 0:
        await q.answer("❌ Bu buyum sizda mavjud emas.", show_alert=True)
        return

    user["active_items"][key] = not user["active_items"][key]
    save_data(data)
    await q.answer("Holat o‘zgartirildi.")
    await item_control(update, context)


# ============================================================
# CALLBACK ROUTER
# ============================================================

async def callback_handler(update, context):
    q = update.callback_query
    data = q.data or ""

    if data.startswith("lang_"):
        await language_button(update, context)
    elif data == "profile":
        await q.answer()
        await q.message.edit_text(get_profile_text(q.from_user), reply_markup=profile_buttons())
    elif data == "dollar_exchange":
        await dollar_exchange(update, context)
    elif data.startswith("exchange_"):
        await exchange_dollar(update, context)
    elif data == "diamond_buy":
        await diamond_buy(update, context)
    elif data == "shop":
        await shop(update, context)
    elif data.startswith("buy_"):
        await buy_item(update, context)
    elif data == "items_info":
        await items_info(update, context)
    elif data == "item_control":
        await item_control(update, context)
    elif data.startswith("toggle_"):
        await toggle_item(update, context)
    elif data.startswith("nighttarget_"):
        await night_target(update, context)
    elif data.startswith("commkill_") or data.startswith("commcheck_"):
        await commissioner_action(update, context)
    elif data.startswith("commtarget_"):
        await commissioner_target(update, context)
    elif data.startswith("vote_"):
        await vote_callback(update, context)
    elif data.startswith("confirm_") or data.startswith("cancel_"):
        await confirm_callback(update, context)
    elif data.startswith("role_"):
        await role_button(update, context)
    else:
        await q.answer()


# ============================================================
# COMMANDS / MAIN
# ============================================================

async def inactive_command(update, context):
    return


GROUP_COMMANDS = [
    BotCommand("gamecreate", "O‘yin yaratish"),
    BotCommand("gamestart", "O‘yinni boshlash"),
    BotCommand("gamestop", "O‘yinni to‘xtatish"),
    BotCommand("gameexit", "O‘yindan chiqish"),
]


async def post_init(application):
    await application.bot.set_my_commands(
        GROUP_COMMANDS,
        scope=BotCommandScopeAllGroupChats()
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("roles", roles))
    application.add_handler(CommandHandler("gamecreate", gamecreate))
    application.add_handler(CommandHandler("gamestart", gamestart))
    application.add_handler(CommandHandler("gamestop", inactive_command))
    application.add_handler(CommandHandler("gameexit", inactive_command))
    application.add_handler(CallbackQueryHandler(callback_handler))

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
