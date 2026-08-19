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

# ===================== VAQTLAR =====================
NIGHT_TIME = 60       # Tun — 1 daqiqa
DAY_TIME = 50         # Kun — 50 soniya
VOTE_TIME = 45        # Ovoz berish — 45 soniya
CONFIRM_TIME = 30     # Hukm tasdig'i — 30 soniya

ACTIVE_GAMES = {}
GAME_TASKS = {}


# ===================== DATA =====================

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


def default_user(user_id):
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
    if uid not in data or not isinstance(data[uid], dict):
        data[uid] = default_user(user_id)
    u = data[uid]
    u.setdefault("dollar", 0)
    u.setdefault("diamond", 0)
    u["vip"] = user_id == OWNER_ID
    u.setdefault("hero", 0)
    u.setdefault("hero_xp", 0)
    u.setdefault("hero_wins", 0)
    u.setdefault("active_role", 0)
    u.setdefault("games", 0)
    u.setdefault("wins", 0)
    u.setdefault("items", {})
    u.setdefault("active_items", {})
    for k in ITEMS:
        if k not in ("hero", "active_role"):
            u["items"].setdefault(k, 0)
            u["active_items"].setdefault(k, False)
    data[uid] = u
    save_data(data)
    return data, u


# ===================== PROFILE =====================

def profile_text(user):
    _, d = get_user_data(user.id)
    games = d["games"]
    wins = d["wins"]
    percent = int(wins / games * 100) if games else 0
    vip = "\n👑 VIP: Ha" if d["vip"] else ""
    return (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {user.first_name or 'Noma’lum'}\n"
        f"🆔 ID: {user.id}{vip}\n\n"
        f"💵 Dollar: {d['dollar']}\n"
        f"💎 Olmos: {d['diamond']}\n\n"
        + "\n".join(
            f"{ITEMS[k][0]}: {d['items'][k]}"
            for k in ITEMS if k not in ("hero", "active_role")
        )
        + "\n\n"
        f"⚔️ Geroy: {'Bor' if d['hero'] else 'Yo‘q'}\n"
        f"🃏 Faol rol: {'Bor' if d['active_role'] else 'Yo‘q'}\n\n"
        f"🎯 G‘alabalar: {wins}\n"
        f"🎲 Barcha o‘yinlar: {games}\n"
        f"📊 G‘alaba foizi: {percent}%"
    )


def profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="diamond")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items")],
        [InlineKeyboardButton("🔻", callback_data="noop")],
    ])


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            profile_text(update.effective_user),
            reply_markup=profile_buttons(),
        )


# ===================== START =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if context.args and context.args[0].startswith("join_"):
        await register_player(update, context)
        return
    await update.message.reply_text(
        "🖤 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        "Mafia Noir o‘yiniga xush kelibsiz.\n"
        "Meni guruhga qo‘shib, o‘yinni boshlang.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Owner 🎩", url=f"https://t.me/{OWNER_USERNAME}")],
            [InlineKeyboardButton("Guruhga qo‘shish ➕",
                                   url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        ]),
    )


# ===================== GAME =====================

def game_key(chat_id, message_id):
    return f"{chat_id}_{message_id}"


def game_text(players):
    if not players:
        return "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\nO‘yin ro‘yxatdan o‘tishi boshlandi."
    return "\n".join(
        "   ".join(players[i:i+4])
        for i in range(0, len(players), 4)
    )


def join_markup(chat_id, message_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Ro‘yxatdan o‘tish",
            url=f"https://t.me/{BOT_USERNAME}?start=join_{game_key(chat_id, message_id)}",
        )
    ]])


async def gamecreate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type not in ("group", "supergroup"):
        return
    m = await update.message.reply_text(
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        "O‘yin ro‘yxatdan o‘tishi boshlandi."
    )
    key = game_key(update.effective_chat.id, m.message_id)
    ACTIVE_GAMES[key] = {
        "chat_id": update.effective_chat.id,
        "message_id": m.message_id,
        "players": {},
        "started": False,
        "phase": "registration",
        "roles": {},
        "votes": {},
        "night_actions": {},
        "alive": {},
    }
    await m.edit_text(
        game_text([]),
        reply_markup=join_markup(update.effective_chat.id, m.message_id),
    )


async def register_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not context.args:
        return
    payload = context.args[0]
    if not payload.startswith("join_"):
        return
    game = ACTIVE_GAMES.get(payload[5:])
    if not game:
        await update.message.reply_text("❌ Bu o‘yin mavjud emas yoki yopilgan.")
        return
    if game["started"]:
        await update.message.reply_text("❌ O‘yin allaqachon boshlangan.")
        return
    u = update.effective_user
    uid = str(u.id)
    if uid in game["players"]:
        await update.message.reply_text("Siz allaqachon ro‘yxatdan o‘tgansiz.")
        return
    name = u.first_name or u.username or "Noma’lum"
    game["players"][uid] = name
    await update.message.reply_text("✅ O‘yinga muvaffaqiyatli qo‘shildingiz.")
    try:
        await context.bot.edit_message_text(
            game["chat_id"], game["message_id"],
            game_text(list(game["players"].values())),
            reply_markup=join_markup(game["chat_id"], game["message_id"]),
        )
    except Exception:
        pass


def latest_game(chat_id):
    found = [
        (g["message_id"], k, g)
        for k, g in ACTIVE_GAMES.items()
        if g["chat_id"] == chat_id and not g["started"]
    ]
    if not found:
        return None
    found.sort(reverse=True)
    return found[0][1], found[0][2]


async def safe_group_edit(context, game, text, markup=None):
    try:
        await context.bot.edit_message_text(
            chat_id=game["chat_id"],
            message_id=game["message_id"],
            text=text,
            reply_markup=markup,
        )
    except Exception:
        try:
            await context.bot.send_message(game["chat_id"], text, reply_markup=markup)
        except Exception:
            pass


# ===================== ROL XABARLARI =====================

ROLE_MESSAGES = {
    "don": "🎩 • DON •\n\nSiz Don bo‘ldingiz.\n🌙 Tun boshlandi.\nMafiyaning boshlig‘i sifatida o‘ljangizni tanlang.",
    "mafia": "🥷 • MAFIA •\n\nSiz Mafia bo‘ldingiz.\n🌙 Tun boshlandi.\nTungi harakatga tayyor turing.",
    "qotil": "🔪 • QOTIL •\n\nSiz Qotil bo‘ldingiz.\n🌙 Tun boshlandi.\nNishoningizni tanlang.",
    "komissar": "👮 • KOMISSAR •\n\nSiz Komissar bo‘ldingiz.\n🌙 Tun boshlandi.\nTekshirish yoki o‘ldirish harakatini tanlang.",
    "doktor": "👨‍⚕️ • DOKTOR •\n\nSiz Doktor bo‘ldingiz.\n🌙 Tun boshlandi.\nBugun kimni qutqarishingizni tanlang.",
    "bodyguard": "🛡️ • BODYGUARD •\n\nSiz Bodyguard bo‘ldingiz.\n🌙 Tun boshlandi.\nKimni himoya qilishingizni tanlang.",
}

def role_keyboard(role):
    buttons = {
        "don": ("🔪 O‘lja tanlash", "night_don"),
        "mafia": ("🎯 Harakat", "night_mafia"),
        "qotil": ("🔪 Nishon tanlash", "night_killer"),
        "komissar": ("🔎 Tekshirish", "night_check"),
        "doktor": ("❤️ Davolash", "night_heal"),
        "bodyguard": ("🛡️ Himoya", "night_guard"),
    }
    if role not in buttons:
        return None
    text, data = buttons[role]
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)]])


async def send_role(context, pid, role_name, role_key):
    text = ROLE_MESSAGES.get(
        role_key,
        f"🎭 • {role_name.upper()} •\n\n"
        f"Siz {role_name} bo‘ldingiz.\n\n🌙 Tun boshlandi.",
    )
    try:
        await context.bot.send_message(
            chat_id=int(pid),
            text=text,
            reply_markup=role_keyboard(role_key),
        )
        return True
    except Exception:
        return False


# ===================== TUNGI HARAKATLAR =====================

def night_status(game):
    actions = game.get("night_actions", {})
    if not actions:
        return "🌙 Tungi harakatlar boshlandi."
    return "🌙 TUNGI HARAKATLAR\n\n" + "\n".join(
        f"• {text}" for text in actions.values()
    )


async def night_action(update, context, action_text):
    q = update.callback_query
    game = next(
        (g for g in ACTIVE_GAMES.values()
         if str(q.from_user.id) in g.get("roles", {}) and g.get("phase") == "night"),
        None,
    )
    if not game:
        await q.answer("❌ Hozir tun emas.", show_alert=True)
        return
    role = game["roles"][str(q.from_user.id)]
    game["night_actions"][str(q.from_user.id)] = (
        f"{role['name']} {action_text}"
    )
    await q.answer("✅ Harakatingiz qabul qilindi.")
    await safe_group_edit(context, game, night_status(game))


# ===================== KUN =====================

async def start_day(context, game):
    game["phase"] = "day"
    game["votes"] = {}
    await safe_group_edit(
        context, game,
        "☀️ • 𝑲𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
        "🌅 Shahar uyg‘ondi.\n\n"
        "🌙 Tungi voqealar yakunlandi.\n"
        "Bugun shahar qaror qabul qiladi.\n\n"
        f"⏳ Kun {DAY_TIME} soniya davom etadi."
    )
    await asyncio.sleep(DAY_TIME)
    if game.get("phase") == "day":
        await start_vote(context, game)


async def start_vote(context, game):
    game["phase"] = "vote"
    game["votes"] = {}
    alive = [
        (pid, r["name"]) for pid, r in game["roles"].items()
        if r.get("alive")
    ]
    rows = []
    for pid, name in alive:
        rows.append([
            InlineKeyboardButton(
                name[:25],
                callback_data=f"vote_{pid}",
            )
        ])
    await safe_group_edit(
        context, game,
        "🗳️ • 𝑶𝑽𝑶𝒁 𝑩𝑬𝑹𝑰𝑺𝑯 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
        f"Kimni hukm qilasiz?\n\n"
        f"⏳ Ovoz berish uchun {VOTE_TIME} soniyangiz bor.",
        InlineKeyboardMarkup(rows) if rows else None,
    )
    await asyncio.sleep(VOTE_TIME)
    if game.get("phase") == "vote":
        await finish_vote(context, game)


async def finish_vote(context, game):
    game["phase"] = "confirm"
    counts = {}
    for target in game.get("votes", {}).values():
        counts[target] = counts.get(target, 0) + 1
    if counts:
        target, count = max(counts.items(), key=lambda x: x[1])
        game["pending_execution"] = target
        name = game["roles"][target]["name"]
        text = (
            "⚖️ • 𝑯𝑼𝑲𝑴 𝑻𝑨𝑺𝑫𝑰𝑸𝑰 •\n\n"
            f"Rostdan ham {name}ni osmoqchimisiz?\n\n"
            f"🔴 {count} ta ovoz"
        )
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔴 Tasdiqlash", callback_data="execute_yes"),
            InlineKeyboardButton("🟢 Bekor qilish", callback_data="execute_no"),
        ]])
    else:
        text = "⚖️ • 𝑯𝑼𝑲𝑴 •\n\nOvozlar yetarli bo‘lmadi."
        markup = None
    await safe_group_edit(context, game, text, markup)
    await asyncio.sleep(CONFIRM_TIME)
    if game.get("phase") == "confirm":
        await execute_verdict(context, game)


async def execute_verdict(context, game):
    target = game.get("pending_execution")
    game["phase"] = "day"
    if target and target in game["roles"] and game["roles"][target]["alive"]:
        game["roles"][target]["alive"] = False
        role = game["roles"][target]["role_name"]
        name = game["roles"][target]["name"]
        await safe_group_edit(
            context, game,
            "⚖️ • 𝑯𝑼𝑲𝑴 𝑰𝑱𝑹𝑶 𝑬𝑻𝑰𝑳𝑫𝑰 •\n\n"
            f"🔴 {name} o‘yindan chetlatildi.\n"
            f"🎭 U edi: {role}\n\n"
            "Hukm ijro etildi."
        )
    else:
        await safe_group_edit(
            context, game,
            "⚖️ • 𝑯𝑼𝑲𝑴 𝑰𝑱𝑹𝑶 𝑬𝑻𝑎𝑴𝑰 •\n\n"
            "Bu safar hech kim o‘yindan chetlatilmadi."
        )


# ===================== O‘YINNI BOSHLASH =====================

async def gamestart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type not in ("group", "supergroup"):
        return
    result = latest_game(update.effective_chat.id)
    if not result:
        await update.message.reply_text("❌ Faol ro‘yxatdan o‘tish topilmadi.")
        return
    key, game = result
    players = game["players"]
    if not players:
        await update.message.reply_text("❌ O‘yinda hech kim yo‘q.")
        return
    if len(players) > len(ROLES):
        await update.message.reply_text("❌ Eng ko‘pi bilan 25 ta o‘yinchi.")
        return

    game["started"] = True
    game["phase"] = "night"
    game["night_actions"] = {}
    selected = ROLES[:len(players)]
    random.shuffle(selected)

    for (pid, pname), (rname, rkey) in zip(players.items(), selected):
        game["roles"][pid] = {
            "name": pname,
            "role_name": rname,
            "role_key": rkey,
            "alive": True,
        }

    await safe_group_edit(
        context, game,
        "🌙 • 𝑻𝑼𝑵 𝑩𝑶𝑺𝑯𝑳𝑨𝑵𝑫𝑰 •\n\n"
        "🌃 Shahar uyquga ketdi.\n\n"
        "Har bir o‘yinchi o‘z roliga tegishli tungi harakatni bajaradi.\n\n"
        f"⏳ Tun {NIGHT_TIME} daqiqa emas, {NIGHT_TIME} soniya davom etadi."
    )

    for pid, r in game["roles"].items():
        await send_role(context, pid, r["role_name"], r["role_key"])

    await asyncio.sleep(NIGHT_TIME)
    if game.get("phase") == "night":
        await start_day(context, game)


# ===================== CALLBACK =====================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data or ""

    if data == "noop":
        await q.answer()
    elif data == "profile":
        await q.answer()
        await q.message.edit_text(profile_text(q.from_user), reply_markup=profile_buttons())
    elif data == "dollar":
        await q.answer("💵 Dollar olish bo‘limi.")
    elif data == "diamond":
        await q.answer("💎 Olmos olish uchun Owner bilan bog‘laning.", show_alert=True)
    elif data == "shop":
        await q.answer("💰 Do‘kon keyingi bo‘limda.")
    elif data == "items":
        await q.answer("📖 Buyumlar bo‘limi.")
    elif data.startswith("vote_"):
        target = data[5:]
        game = next(
            (g for g in ACTIVE_GAMES.values()
             if g.get("phase") == "vote" and str(q.from_user.id) in g.get("roles", {})),
            None,
        )
        if not game:
            await q.answer("❌ Ovoz berish yopilgan.", show_alert=True)
            return
        voter = str(q.from_user.id)
        if not game["roles"].get(voter, {}).get("alive"):
            await q.answer("❌ Siz o‘yindan chiqdingiz.", show_alert=True)
            return
        if not game["roles"].get(target, {}).get("alive"):
            await q.answer("❌ Bu o‘yinchi allaqachon o‘yindan chiqqan.", show_alert=True)
            return
        game["votes"][voter] = target
        counts = {}
        for t in game["votes"].values():
            counts[t] = counts.get(t, 0) + 1
        target_name = game["roles"][target]["name"]
        await q.answer(f"✅ Ovoz: {target_name}")
        await safe_group_edit(
            context, game,
            "🗳️ • 𝑶𝑽𝑶𝒁 𝑩𝑬𝑹𝑰𝑺𝑯 •\n\n"
            f"Eng ko‘p ovoz: {target_name}\n"
            f"🔴 {counts.get(target, 0)} ta ovoz\n\n"
            f"⏳ Ovoz berish uchun {VOTE_TIME} soniyangiz bor."
        )
    elif data == "execute_yes":
        game = next(
            (g for g in ACTIVE_GAMES.values()
             if g.get("phase") == "confirm"),
            None,
        )
        await q.answer()
        if game:
            await execute_verdict(context, game)
    elif data == "execute_no":
        game = next(
            (g for g in ACTIVE_GAMES.values()
             if g.get("phase") == "confirm"),
            None,
        )
        await q.answer("Hukm bekor qilindi.")
        if game:
            game["phase"] = "day"
            game["pending_execution"] = None
            await safe_group_edit(
                context, game,
                "⚖️ • 𝑯𝑼𝑲𝑴 𝑩𝑬KOR QILINDI •\n\n"
                "O‘yin davom etadi."
            )
    elif data.startswith("night_"):
        labels = {
            "night_don": "o‘z o‘ljasini tanladi",
            "night_mafia": "tungi harakatini bajardi",
            "night_killer": "nishonini tanladi",
            "night_check": "tekshiruvga ketdi",
            "night_heal": "navbatchilikka ketdi",
            "night_guard": "himoyaga ketdi",
        }
        await night_action(update, context, labels.get(data, "harakat qildi"))
    else:
        await q.answer()


# ===================== COMMANDS =====================

async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\n" +
            "\n".join(f"{e} — {k}" for e, k in ROLES)
        )


async def inactive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return


async def post_init(app):
    await app.bot.set_my_commands([
        BotCommand("gamecreate", "O‘yin yaratish"),
        BotCommand("gamestart", "O‘yinni boshlash"),
        BotCommand("gamestop", "O‘yinni to‘xtatish"),
        BotCommand("gameexit", "O‘yindan chiqish"),
        BotCommand("profile", "Profil"),
        BotCommand("roles", "Rollar"),
    ], scope=BotCommandScopeAllGroupChats())


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN Secret topilmadi")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("roles", roles))
    app.add_handler(CommandHandler("gamecreate", gamecreate))
    app.add_handler(CommandHandler("gamestart", gamestart))

    for cmd in ("gamestop", "gameexit", "paragame"):
        app.add_handler(CommandHandler(cmd, inactive))

    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
