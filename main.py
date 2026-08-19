import os
import json
import asyncio
import random
import time
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    BotCommandScopeAllGroupChats,
)
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = Path("data.json")
OWNER_ID = 8402159260
OWNER_USERNAME = "Umarov_uuu"
BOT_USERNAME = "Noiruzbot"

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
            return json.load(f)
    except Exception:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_default_user(user_id):
    return {
        "dollar": 0, "diamond": 0, "vip": user_id == OWNER_ID,
        "hero": 0, "hero_xp": 0, "hero_wins": 0, "active_role": 0,
        "items": {k: 0 for k in ITEMS if k not in ("hero", "active_role")},
        "active_items": {k: False for k in ITEMS if k not in ("hero", "active_role")},
    }


def get_user_data(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = get_default_user(user_id)
    user = data[uid]
    user.setdefault("dollar", 0); user.setdefault("diamond", 0)
    user["vip"] = user_id == OWNER_ID
    user.setdefault("hero", 0); user.setdefault("hero_xp", 0); user.setdefault("hero_wins", 0)
    user.setdefault("active_role", 0); user.setdefault("items", {}); user.setdefault("active_items", {})
    for key in ITEMS:
        if key not in ("hero", "active_role"):
            user["items"].setdefault(key, 0); user["active_items"].setdefault(key, False)
    save_data(data)
    return data, user


def get_language_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kk")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ])


def get_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Owner 🎩", url="https://t.me/Umarov_uuu")],
        [InlineKeyboardButton("Asosiy guruh 👥", url="https://t.me/+0eXijyVhioY4ZDMy")],
        [InlineKeyboardButton("Guruhga qo‘shish ➕", url="https://t.me/Noiruzbot?startgroup=true")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args or []
    if args and args[0].startswith("vote_"):
        game_id = args[0][5:]
        game = GAMES.get(game_id)
        if not game or game.get("phase") != "voting":
            await update.message.reply_text("❌ Hozir ovoz berish mavjud emas.")
            return
        if update.effective_user.id not in game["players"]:
            await update.message.reply_text("❌ Siz bu o‘yinda qatnashmayapsiz.")
            return
        await send_vote_panel(update.effective_user.id, game_id, context)
        return
    await update.message.reply_text("🌍 Tilni tanlang:", reply_markup=get_language_buttons())


async def language_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "🖤 Salom! Xush kelibsiz!\n\n🌃 Men Mafia Noir botiman. Mafia o‘ynash uchun meni guruhingizga qo‘shing.",
        reply_markup=get_main_buttons(),
    )


def get_profile_text(user):
    _, u = get_user_data(user.id)
    vip_line = "\n👑 VIP: Ha" if u["vip"] else ""
    return (
        "🕴️ • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n"
        f"👤 Ism: {user.first_name or 'Noma’lum'}\n"
        f"🆔 ID: {user.id}{vip_line}\n\n"
        f"💵 Dollar: {u['dollar']}\n💎 Olmos: {u['diamond']}\n\n"
        f"🛡 Qora qalqon: {u['items']['shield']}\n📜 Soxta hujjat: {u['items']['document']}\n"
        f"⚖️ Afv tamg‘asi: {u['items']['forgiveness']}\n🩸 Qotil niqobi: {u['items']['killer_mask']}\n"
        f"🔫 Noir miltig‘i: {u['items']['gun']}\n💊 Qora dori: {u['items']['black_medicine']}\n"
        f"🧪 Verbena ekstrakti: {u['items']['verbena']}\n🥷 Sirli niqob: {u['items']['mystery_mask']}\n"
        f"🛡️ Geroydan himoya: {u['items']['hero_protection']}\n\n"
        f"⚔️ Geroy: {'Bor' if u['hero'] > 0 else 'Yo‘q'}\n"
        f"🃏 Faol rol: {'Bor' if u['active_role'] > 0 else 'Yo‘q'}\n\n"
        "🎯 G‘alabalar: 0\n🎲 Barcha o‘yinlar: 0\n📊 G‘alaba foizi: 0"
    )


def get_profile_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Dollar olish", callback_data="dollar_exchange")],
        [InlineKeyboardButton("💎 Olmos olish", callback_data="diamond_buy")],
        [InlineKeyboardButton("⚔️ Mening Geroyim", callback_data="hero")],
        [InlineKeyboardButton("💰 Do‘kon", callback_data="shop")],
        [InlineKeyboardButton("📖 Buyumlar haqida", callback_data="items_info")],
        [InlineKeyboardButton("🔻", callback_data="item_control")],
    ])


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_profile_text(update.effective_user), reply_markup=get_profile_buttons())

DOLLAR_PACKAGES = [(1, 600), (2, 1200), (3, 1800), (5, 3000), (10, 6000), (20, 12000)]


def get_dollar_buttons():
    keyboard = [[InlineKeyboardButton(f"💎 {d} → 💵 {dol}", callback_data=f"exchange_{d}")] for d, dol in DOLLAR_PACKAGES]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    return InlineKeyboardMarkup(keyboard)


async def dollar_exchange(update, context):
    q = update.callback_query; await q.answer()
    await q.message.edit_text("💵 • 𝑫𝒐𝒍𝒍𝒂𝒓 𝒐𝒍𝒊𝒔𝒉 •\n\nOlmosni Dollarga almashtiring:", reply_markup=get_dollar_buttons())


async def exchange_dollar(update, context):
    q = update.callback_query
    try: amount = int(q.data.split("_")[1])
    except (IndexError, ValueError): await q.answer("❌ Xatolik", show_alert=True); return
    data, u = get_user_data(q.from_user.id)
    if q.from_user.id != OWNER_ID:
        if u["diamond"] < amount:
            await q.answer("❌ Olmos yetarli emas", show_alert=True); return
        u["diamond"] -= amount
    u["dollar"] += amount * 600; save_data(data)
    await q.answer("✅ Savdo muvaffaqiyatli amalga oshirildi!")
    await q.message.edit_text(get_profile_text(q.from_user), reply_markup=get_profile_buttons())

DIAMOND_PACKAGES = [(5, 4000), (10, 8000), (25, 20000), (50, 40000), (100, 80000), (250, 200000)]

def get_diamond_buttons():
    keyboard = [[InlineKeyboardButton(f"💎 {a} ta — {p:,} so‘m".replace(",", " "), url=f"https://t.me/{OWNER_USERNAME}")] for a,p in DIAMOND_PACKAGES]
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    return InlineKeyboardMarkup(keyboard)

async def diamond_buy(update, context):
    q=update.callback_query; await q.answer()
    await q.message.edit_text("💎 • 𝑶𝒍𝒎𝒐𝒔 𝒐𝒍𝒊𝒔𝒉 •\n\nKerakli paketni tanlang:", reply_markup=get_diamond_buttons())

def get_shop_buttons():
    keyboard=[]
    for key,(name,price,currency) in ITEMS.items():
        emoji="💵" if currency=="dollar" else "💎"
        keyboard.append([InlineKeyboardButton(f"{name} — {emoji} {price}", callback_data=f"buy_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="profile")])
    return InlineKeyboardMarkup(keyboard)

async def shop(update, context):
    q=update.callback_query; await q.answer()
    await q.message.edit_text("💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\nKerakli buyumni tanlang:", reply_markup=get_shop_buttons())

async def buy_item(update, context):
    q=update.callback_query; key=q.data.replace("buy_", "", 1)
    if key not in ITEMS: await q.answer("❌ Xatolik"); return
    name,price,currency=ITEMS[key]; data,u=get_user_data(q.from_user.id)
    if q.from_user.id != OWNER_ID:
        wallet=currency
        if u[wallet] < price: await q.answer("❌ Mablag‘ yetarli emas", show_alert=True); return
        u[wallet]-=price
    if key=="hero": u["hero"]+=1
    elif key=="active_role": u["active_role"]+=1
    else: u["items"][key]+=1
    save_data(data); await q.answer("✅ Xarid muvaffaqiyatli amalga oshirildi!")
    await q.message.edit_text("💰 • 𝑫𝒐‘𝒌𝒐𝒏 •\n\n✅ Xarid muvaffaqiyatli amalga oshirildi.\n\nYana buyum tanlang:", reply_markup=get_shop_buttons())

DESCRIPTIONS={
"shield":"bir marta hujumdan himoya qiladi.","document":"tekshiruvda rolni yashirishga yordam beradi.","forgiveness":"bir marta jazodan qutqaradi.","killer_mask":"qotilni aniqlashni qiyinlashtiradi.","gun":"bir marta hujum qilish imkonini beradi.","black_medicine":"salbiy ta’sirni olib tashlaydi.","verbena":"vampirdan himoya qiladi.","mystery_mask":"rolni vaqtincha yashiradi.","hero_protection":"geroy hujumidan bir marta himoya qiladi.","hero":"sotib olingandan keyin sizga Geroy beriladi.","active_role":"1 ta o‘yin uchun tasodifiy faol rol beradi.",}

async def items_info(update, context):
    q=update.callback_query; await q.answer()
    text="📖 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓 𝒉𝒂𝒒𝒊𝒅𝒂 •\n\n"+"".join(f"{name} — {DESCRIPTIONS[key]}\n" for key,(name,_,_) in ITEMS.items())
    await q.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga",callback_data="profile")]]))

def get_control_buttons(u):
    keyboard=[]
    for key,(name,_,_) in ITEMS.items():
        if key in ("hero","active_role"): continue
        keyboard.append([InlineKeyboardButton(f"{name} — {u['items'][key]}",callback_data=f"noop_{key}")])
        keyboard.append([InlineKeyboardButton("🟢 ON" if u["active_items"][key] else "⚪ OFF",callback_data=f"toggle_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga",callback_data="profile")]); return InlineKeyboardMarkup(keyboard)

async def item_control(update,context):
    q=update.callback_query; await q.answer(); _,u=get_user_data(q.from_user.id)
    await q.message.edit_text("🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\nBuyumni ON yoki OFF holatiga o‘tkazing.",reply_markup=get_control_buttons(u))

async def toggle_item(update,context):
    q=update.callback_query; key=q.data.replace("toggle_","")
    if key not in ITEMS: await q.answer("❌ Xatolik"); return
    data,u=get_user_data(q.from_user.id)
    if key not in u["items"]: await q.answer("❌ Xatolik"); return
    if u["items"][key]<=0: await q.answer("❌ Bu buyum sizda mavjud emas",show_alert=True); return
    u["active_items"][key]=not u["active_items"][key]; save_data(data); await q.answer()
    await q.message.edit_text("🔻 • 𝑩𝒖𝒚𝒖𝒎𝒍𝒂𝒓𝒏𝒊 𝒃𝒐𝒔𝒉𝒒𝒂𝒓𝒊𝒔𝒉 •\n\nBuyumni ON yoki OFF holatiga o‘tkazing.",reply_markup=get_control_buttons(u))

HERO_LEVELS=[("🥉 I — Bronze",0,"⚔️ Hujum"),("🥈 II — Silver",100,"🛡️ Himoya"),("🥇 III — Gold",300,"🪖 Zirh"),("💎 IV — Diamond",700,"⚡ Maxsus qobiliyat"),("🖤 V — Noir",1500,"👑 Maxsus kuch")]
def get_hero_level(xp):
    level=1
    for i,(_,need,_) in enumerate(HERO_LEVELS):
        if xp>=need: level=i+1
    return level

def get_hero_progress(xp):
    level=get_hero_level(xp); current=HERO_LEVELS[level-1]; return current[0],current[1],current[2],None if level>=5 else HERO_LEVELS[level][1]

def get_hero_buttons(): return InlineKeyboardMarkup([[InlineKeyboardButton("📊 Darajalar",callback_data="hero_levels")],[InlineKeyboardButton("⚡ Qobiliyatlar",callback_data="hero_skills")],[InlineKeyboardButton("🔙 Orqaga",callback_data="profile")]])

async def hero(update,context):
    q=update.callback_query; await q.answer(); _,u=get_user_data(q.from_user.id)
    if u["hero"]<=0:
        await q.message.edit_text("⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n❌ Sizda Geroy mavjud emas.\n\n💎 Do‘kondan Geroy sotib olishingiz mumkin.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 Do‘konga",callback_data="shop")],[InlineKeyboardButton("🔙 Orqaga",callback_data="profile")]])); return
    xp=u.get("hero_xp",0); wins=u.get("hero_wins",0); level=get_hero_level(xp); name,_,power,next_xp=get_hero_progress(xp)
    xp_line=f"⭐ XP: {xp} — MAX" if next_xp is None else f"⭐ XP: {xp} / {next_xp}"; next_line="👑 Maksimal daraja ochilgan" if next_xp is None else f"📈 Keyingi daraja: {next_xp} XP"
    shield="🛡️ Himoya: Faol" if level>=2 else "🛡️ Himoya: Hali ochilmagan"
    text=(f"⚔️ • 𝑴𝒆𝒏𝒊𝒏𝒈 𝑮𝒆𝒓𝒐𝒚𝒊𝒎 •\n\n👤 Egasi: {q.from_user.first_name or 'Noma’lum'}\n\n⚔️ Geroylar: {u['hero']} ta\n🏆 Daraja: {name}\n{xp_line}\n\n🎯 G‘alabalar: {wins}\n{shield}\n⚡ Qobiliyat: {power}\n\n{next_line}\n\n━━━━━━━━━━━━━━\n🥉 I — Bronze\n🥈 II — Silver\n🥇 III — Gold\n💎 IV — Diamond\n🖤 V — Noir")
    await q.message.edit_text(text,reply_markup=get_hero_buttons())

async def hero_levels(update,context):
    q=update.callback_query; await q.answer(); _,u=get_user_data(q.from_user.id)
    if u["hero"]<=0: await q.answer("❌ Sizda Geroy yo‘q",show_alert=True); return
    text=("🏆 • 𝑮𝒆𝒓𝒐𝒚 𝑫𝒂𝒓𝒂𝒋𝒂𝒍𝒂𝒓𝒊 •\n\n🥉 I — Bronze\n⚔️ Hujum\n🔓 0 XP\n\n🥈 II — Silver\n🛡️ Himoya\n🔓 100 XP\n\n🥇 III — Gold\n🪖 Zirh\n🔓 300 XP\n\n💎 IV — Diamond\n⚡ Maxsus qobiliyat\n🔓 700 XP\n\n🖤 V — Noir\n👑 Maxsus kuch\n🔓 1500 XP\n\n📍 Hozirgi daraja: {get_hero_level(u.get('hero_xp',0))}/5")
    await q.message.edit_text(text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geroy profiliga",callback_data="hero")]]))

async def hero_skills(update,context):
    q=update.callback_query; await q.answer(); _,u=get_user_data(q.from_user.id)
    if u["hero"]<=0: await q.answer("❌ Sizda Geroy yo‘q",show_alert=True); return
    level=get_hero_level(u.get("hero_xp",0)); skills=[x[2] for x in HERO_LEVELS[:level]]
    await q.message.edit_text(f"⚡ • 𝑮𝒆𝒓𝒐𝒚 𝑸𝒐𝒃𝒊𝒍𝒊𝒚𝒂𝒕𝒍𝒂𝒓𝒊 •\n\n🏆 Daraja: {level}/5\n\n"+"\n".join(skills),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geroy profiliga",callback_data="hero")]]))

ROLES=[("🎩 Don","role_don"),("🥷 Mafia","role_mafia"),("🎭 Aferist","role_aferist"),("🔪 Qotil","role_qotil"),("👮 Komissar","role_komissar"),("👨‍⚕️ Doktor","role_doktor"),("👮‍♂️ Serjant","role_serjant"),("🎖️ Kapitan","role_kapitan"),("👤 Fuqaro","role_fuqaro"),("👣 Daydi","role_daydi"),("⚖️ Sudya","role_sudya"),("👨‍⚖️ Advokat","role_advokat"),("💀 Qasoskor","role_qasoskor"),("🦎 Buqalamun","role_buqalamun"),("🕵️ Kuzatuvchi","role_kuzatuvchi"),("🛡️ Bodyguard","role_bodyguard"),("🧙 Sehrgar","role_sehrgar"),("📰 Jurnalist","role_jurnalist"),("🔬 Kimyogar","role_kimyogar"),("💣 Minyor","role_minyor"),("⚡ Koldun","role_koldun"),("🕶️ Maxfiy agent","role_agent"),("👻 Arvoh","role_arvoh"),("🤡 Joker","role_joker"),("🧛 Vampir","role_vampir")]
ROLE_DESCRIPTIONS={
"role_don":"🎩 DON\n\nMafiya jamoasining boshlig‘i.\n\n🎯 Vazifasi: Mafiya bilan birga g‘alaba qozonish.","role_mafia":"🥷 MAFIA\n\nMafiya jamoasining asosiy a’zosi.\n\n🎯 Vazifasi: Tinchliksevarlarni yo‘q qilish.","role_aferist":"🎭 AFERIST\n\nAldov va hiylaga asoslangan mustaqil rol.","role_qotil":"🔪 QOTIL\n\nMustaqil xavfli hujumchi.","role_komissar":"👮 KOMISSAR\n\nTinchliksevarlar tomonidagi tekshiruvchi.","role_doktor":"👨‍⚕️ DOKTOR\n\nO‘yinchilarni himoya qiluvchi rol.","role_serjant":"👮‍♂️ SERJANT\n\nTartibni saqlashga yordam beruvchi rol.","role_kapitan":"🎖️ KAPITAN\n\nKuchli boshqaruv qobiliyatiga ega rol.","role_fuqaro":"👤 FUQARO\n\nOddiy tinchliksevar o‘yinchi.","role_daydi":"👣 DAYDI\n\nMustaqil harakat qiluvchi sirli rol.","role_sudya":"⚖️ SUDYA\n\nSud va ovoz berishga ta’sir qiluvchi rol.","role_advokat":"👨‍⚖️ ADVOKAT\n\nO‘yinchini himoya qilishga yordam beruvchi rol.","role_qasoskor":"💀 QASOSKOR\n\nQasos olish imkoniyatiga ega rol.","role_buqalamun":"🦎 BUQALAMUN\n\nO‘zini boshqa rolga o‘xshatishi mumkin.","role_kuzatuvchi":"🕵️ KUZATUVCHI\n\nO‘yinchilar harakatini kuzatuvchi rol.","role_bodyguard":"🛡️ BODYGUARD\n\nTanlangan o‘yinchini himoya qiladi.","role_sehrgar":"🧙 SEHRGAR\n\nMaxsus sehrli qobiliyatlarga ega rol.","role_jurnalist":"📰 JURNALIST\n\nMa’lumot va sirlarni izlovchi rol.","role_kimyogar":"🔬 KIMYOGAR\n\nMaxsus moddalar va ta’sirlardan foydalanadi.","role_minyor":"💣 MINYOR\n\nTuzoq va maxsus qobiliyatlarga ega rol.","role_koldun":"⚡ KOLDUN\n\nSirli kuchlardan foydalanadi.","role_agent":"🕶️ MAXFIY AGENT\n\nYashirin topshiriqlarni bajaruvchi rol.","role_arvoh":"👻 ARVOH\n\nO‘yindan chiqqandan keyin maxsus imkoniyatlarga ega.","role_joker":"🤡 JOKER\n\nO‘yinni chalkashtiruvchi mustaqil rol.","role_vampir":"🧛 VAMPIR\n\nTunda harakat qiluvchi maxsus rol."}

def get_roles_buttons():
    return InlineKeyboardMarkup([[InlineKeyboardButton(ROLES[i][0],callback_data=ROLES[i][1]),InlineKeyboardButton(ROLES[i+1][0],callback_data=ROLES[i+1][1]) if i+1<len(ROLES) else InlineKeyboardButton(" ",callback_data="noop")] for i in range(0,len(ROLES),2)])

async def roles(update,context): await update.message.reply_text("🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 𝑹𝒐𝒍𝒍𝒂𝒓 •\n\nKerakli rolni tanlang:",reply_markup=get_roles_buttons())
async def role_button(update,context):
    q=update.callback_query; await q.answer(ROLE_DESCRIPTIONS.get(q.data,"❌ Bu rol haqida ma’lumot topilmadi."),show_alert=True)

# ======================= O‘YIN =======================
GAMES = {}

GAME_ROLES = ["don", "mafia", "doctor", "citizen"]
ROLE_NAMES = {"don":"🎩 Don", "mafia":"🥷 Mafia", "doctor":"👨‍⚕️ Doktor", "citizen":"👤 Fuqaro"}


def new_game(chat_id):
    game_id=f"{chat_id}_{int(time.time()*1000)}"
    GAMES[game_id]={"id":game_id,"chat_id":chat_id,"players":{},"phase":"registration","registration_message_id":None,"night":0,"attack":None,"doctor_save":None,"votes":{},"confirmed_votes":{},"confirmation":{}}
    return GAMES[game_id]


def active_game(chat_id):
    for game in GAMES.values():
        if game["chat_id"]==chat_id and game["phase"] not in ("finished","cancelled"):
            return game
    return None


def player_name(player): return player.get("name") or "Noma’lum"

def registration_keyboard(game):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎮 O‘yinga qo‘shilish",callback_data=f"join_{game['id']}")],[InlineKeyboardButton("❌ O‘yinni bekor qilish",callback_data=f"cancel_{game['id']}")]])

async def gamecreate(update,context):
    if not update.effective_chat or update.effective_chat.type not in ("group","supergroup"):
        return
    if active_game(update.effective_chat.id): return
    game=new_game(update.effective_chat.id)
    msg=await update.message.reply_text("🎭 • 𝑴𝒂𝒇𝒊𝒂 𝑵𝒐𝒊𝒓 •\n\n🎮 O‘yinga ro‘yxatdan o‘tish boshlandi!\n\nO‘yinga qo‘shilish uchun tugmani bosing.",reply_markup=registration_keyboard(game))
    game["registration_message_id"]=msg.message_id
    try: await context.bot.pin_chat_message(update.effective_chat.id,msg.message_id,disable_notification=True)
    except Exception: pass

async def join_game(update,context):
    q=update.callback_query; await q.answer(); game=GAMES.get(q.data[5:])
    if not game or game["phase"]!="registration": await q.answer("❌ Ro‘yxatdan o‘tish yopilgan",show_alert=True); return
    uid=q.from_user.id
    if uid not in game["players"]: game["players"][uid]={"name":q.from_user.first_name or "Noma’lum","role":None,"alive":True}
    await q.answer("✅ O‘yinga qo‘shildingiz!")
    try: await q.message.edit_reply_markup(reply_markup=registration_keyboard(game))
    except Exception: pass

async def cancel_game(update,context):
    q=update.callback_query; await q.answer(); game=GAMES.get(q.data[7:])
    if not game or game["phase"]!="registration": return
    game["phase"]="cancelled"
    try: await q.message.delete()
    except Exception: pass
    await context.bot.send_message(game["chat_id"],"❌ O‘yin bekor qilindi.")

async def gameexit(update,context):
    if update.effective_chat.type not in ("group","supergroup"): return
    game=active_game(update.effective_chat.id)
    if not game: return
    uid=update.effective_user.id
    if uid in game["players"] and game["phase"]=="registration":
        del game["players"][uid]
        try: await context.bot.send_message(uid,"🚪 Siz o‘yindan chiqdingiz.")
        except Exception: pass

async def gamestart(update,context):
    if update.effective_chat.type not in ("group","supergroup"): return
    game=active_game(update.effective_chat.id)
    if not game or game["phase"]!="registration": return
    if len(game["players"])<4:
        await update.message.reply_text("❌ O‘yinni boshlash uchun kamida 4 o‘yinchi kerak."); return
    game["phase"]="night"; game["night"]=1
    assign_roles(game)
    try: await context.bot.delete_message(game["chat_id"],game["registration_message_id"])
    except Exception: pass
    for uid,p in game["players"].items():
        try: await send_role(uid,p["role"],game,context)
        except Exception: pass
    await update.message.reply_text("🌙 • 𝑻𝒖𝒏 •\n\n🌙 Tun boshlandi.")
    asyncio.create_task(night_timer(game["id"],context))


def assign_roles(game):
    ids=list(game["players"]); random.shuffle(ids)
    roles=[]
    roles.append("don")
    if len(ids)>=5: roles.append("mafia")
    roles.append("doctor")
    roles += ["citizen"]*max(0,len(ids)-len(roles))
    random.shuffle(roles)
    for uid,role in zip(ids,roles): game["players"][uid]["role"]=role

async def send_role(uid,role,game,context):
    text=f"🎭 Sizning rolingiz: {ROLE_NAMES[role]}\n\n"
    if role=="don": text+="🌙 Tunda bitta o‘yinchini nishonlaysiz."
    elif role=="mafia": text+="🌙 Siz Mafiya jamoasidasiz."
    elif role=="doctor": text+="🌙 Tunda bitta o‘yinchini davolaysiz."
    else: text+="🌙 Siz tinchliksevar o‘yinchisiz."
    await context.bot.send_message(uid,text,reply_markup=night_buttons(game,role,uid))


def night_buttons(game,role,uid):
    if role not in ("don","doctor"): return None
    buttons=[]
    for target,p in game["players"].items():
        if target!=uid and p["alive"]: buttons.append([InlineKeyboardButton(f"👤 {player_name(p)}",callback_data=f"night_{game['id']}_{role}_{target}")])
    return InlineKeyboardMarkup(buttons)

async def night_action(update,context):
    q=update.callback_query; parts=q.data.split("_")
    if len(parts)!=4: await q.answer(); return
    _,gid,role,target_s=parts; game=GAMES.get(gid)
    if not game or game["phase"]!="night": await q.answer("❌ Tun tugagan",show_alert=True); return
    uid=q.from_user.id; target=int(target_s)
    if uid not in game["players"] or game["players"][uid]["role"]!=role or not game["players"][uid]["alive"]: await q.answer("❌ Ruxsat yo‘q",show_alert=True); return
    if target not in game["players"] or not game["players"][target]["alive"]: await q.answer("❌ Bu o‘yinchi mavjud emas",show_alert=True); return
    if role=="don": game["attack"]=target
    else: game["doctor_save"]=target
    await q.answer("✅ Tanlov qabul qilindi")

async def night_timer(gid,context):
    await asyncio.sleep(60)
    game=GAMES.get(gid)
    if not game or game["phase"]!="night": return
    attack=game.get("attack"); save=game.get("doctor_save")
    if attack:
        target=game["players"].get(attack); doctor=game.get("doctor_save")
        if save==attack:
            try: await context.bot.send_message(save,"🩺 Siz Ali ni davoladingiz. Uning mehmoni Don edi.")
            except Exception: pass
            try: await context.bot.send_message(attack,"🛡️ Sizga Don hujum qildi, lekin doktor sizni davoladi.")
            except Exception: pass
        elif target and target["alive"]:
            target["alive"]=False
            try: await context.bot.send_message(attack,"💀 Siz o‘yindan chiqdingiz. Don sizga hujum qildi.")
            except Exception: pass
    game["phase"]="day"
    await context.bot.send_message(game["chat_id"],"☀️ • 𝑲𝒖𝒏 •\n\n☀️ Kun e’lon qilindi.")
    asyncio.create_task(day_to_vote(gid,context))

async def day_to_vote(gid,context):
    await asyncio.sleep(30)
    game=GAMES.get(gid)
    if not game or game["phase"]!="day": return
    game["phase"]="voting"; game["votes"]={}; game["confirmed_votes"]={}; game["confirmation"]={}
    url=f"https://t.me/{BOT_USERNAME}?start=vote_{gid}"
    msg=("🗳️ • 𝑶𝒗𝒐𝒛 𝒃𝒆𝒓𝒊𝒔𝒉 𝒃𝒐𝒔𝒉𝒍𝒂𝒏𝒅𝒊 •\n\n⏳ Ovoz berish davom etmoqda...")
    await context.bot.send_message(game["chat_id"],msg,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗳️ Ovoz berish",url=url)]]))
    asyncio.create_task(vote_timer(gid,context))

async def send_vote_panel(uid,gid,context):
    game=GAMES.get(gid)
    if not game or game["phase"]!="voting":
        await context.bot.send_message(uid,"❌ Ovoz berish mavjud emas."); return
    if uid in game["confirmed_votes"]:
        await context.bot.send_message(uid,"✅ Siz allaqachon ovoz bergansiz."); return
    buttons=[]
    for target,p in game["players"].items():
        if target!=uid and p["alive"]: buttons.append([InlineKeyboardButton(f"👤 {player_name(p)}",callback_data=f"vote_{gid}_{target}")])
    await context.bot.send_message(uid,"🗳️ Kimga ovoz berasiz?",reply_markup=InlineKeyboardMarkup(buttons))

async def vote_choose(update,context):
    q=update.callback_query; parts=q.data.split("_")
    if len(parts)!=3: await q.answer(); return
    _,gid,target_s=parts; game=GAMES.get(gid); uid=q.from_user.id; target=int(target_s)
    if not game or game["phase"]!="voting": await q.answer("❌ Ovoz berish tugagan",show_alert=True); return
    if uid not in game["players"] or not game["players"][uid]["alive"] or uid in game["confirmed_votes"]: await q.answer("❌ Ovoz berish mumkin emas",show_alert=True); return
    if target not in game["players"] or not game["players"][target]["alive"]: await q.answer("❌ Bu o‘yinchi mavjud emas",show_alert=True); return
    game["confirmation"][uid]=target
    buttons=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Ha",callback_data=f"confirm_{gid}_{target}"),InlineKeyboardButton("❌ Yo‘q",callback_data=f"reject_{gid}")]])
    await q.message.edit_text(f"❓ Rostan ham {player_name(game['players'][target])}ni osmoqchimisiz?",reply_markup=buttons)
    await q.answer()

async def vote_confirm(update,context):
    q=update.callback_query; parts=q.data.split("_"); gid=parts[1]; target=int(parts[2]); game=GAMES.get(gid); uid=q.from_user.id
    if not game or game["phase"]!="voting" or game["confirmation"].get(uid)!=target: await q.answer("❌ So‘rov eskirgan",show_alert=True); return
    game["confirmed_votes"][uid]=target; del game["confirmation"][uid]
    await q.answer("✅ Ovoz qabul qilindi")
    voter=player_name(game["players"][uid]); target_name=player_name(game["players"][target])
    await context.bot.send_message(game["chat_id"],f"🗳️ {voter} → {target_name}")
    await q.message.edit_text(f"✅ Ovoz qabul qilindi: {target_name}")

async def vote_reject(update,context):
    q=update.callback_query; gid=q.data.split("_")[1]; game=GAMES.get(gid); uid=q.from_user.id
    if game: game["confirmation"].pop(uid,None)
    await q.answer("❌ Bekor qilindi"); await send_vote_panel(uid,gid,context)

async def vote_timer(gid,context):
    await asyncio.sleep(45)
    game=GAMES.get(gid)
    if not game or game["phase"]!="voting": return
    game["phase"]="confirmation"
    # Ovozlar allaqachon tasdiqlangan; qolgan 30 soniya tasdiqlash bosqichi uchun beriladi.
    await context.bot.send_message(game["chat_id"],"⏳ Ovoz berish yakunlandi. Tasdiqlash bosqichi boshlandi.")
    asyncio.create_task(finish_vote(gid,context))

async def finish_vote(gid,context):
    await asyncio.sleep(30)
    game=GAMES.get(gid)
    if not game or game["phase"] not in ("confirmation","voting"): return
    game["phase"]="day"
    counts={}
    for target in game["confirmed_votes"].values(): counts[target]=counts.get(target,0)+1
    if counts:
        max_votes=max(counts.values()); winners=[uid for uid,n in counts.items() if n==max_votes]
        if len(winners)==1:
            target=winners[0]; game["players"][target]["alive"]=False
            await context.bot.send_message(game["chat_id"],f"⚖️ {player_name(game['players'][target])} ovoz bilan o‘yindan chiqarildi.")
    if await check_game_end(gid,context): return
    game["phase"]="night"; game["night"]+=1; game["attack"]=None; game["doctor_save"]=None
    await context.bot.send_message(game["chat_id"],"🌙 • 𝑻𝒖𝒏 •\n\n🌙 Tun boshlandi.")
    for uid,p in game["players"].items():
        if p["alive"] and p["role"] in ("don","doctor"):
            try: await context.bot.send_message(uid,"🌙 Tun boshlandi.",reply_markup=night_buttons(game,p["role"],uid))
            except Exception: pass
    asyncio.create_task(night_timer(gid,context))

async def check_game_end(gid,context):
    game=GAMES.get(gid); alive=[p for p in game["players"].values() if p["alive"]]
    mafia=sum(1 for p in alive if p["role"] in ("don","mafia")); citizens=len(alive)-mafia
    if mafia==0: winning=[uid for uid,p in game["players"].items() if p["role"] not in ("don","mafia") and p["alive"]]; await finish_game(game,winning,context); return True
    if mafia>=citizens: winning=[uid for uid,p in game["players"].items() if p["role"] in ("don","mafia") and p["alive"]]; await finish_game(game,winning,context); return True
    return False

async def finish_game(game,winners,context):
    game["phase"]="finished"
    data=load_data()
    winner_set=set(winners)
    for uid,p in game["players"].items():
        d,u=get_user_data(uid)
        if uid in winner_set:
            u["dollar"]+=60; u["hero_xp"]+=10; u["hero_wins"]+=1
            text=("🏆 • 𝑮‘𝒂𝒍𝒂𝒃𝒂 •\n\n" "🎉 Tabriklaymiz, g‘alaba qozondingiz!\n\n" "💵 Mukofot: +60 Dollar\n⭐ XP: +10")
        else:
            u["dollar"]+=20
            text="🎮 O‘yin yakunlandi. Sizga 20 Dollar berildi."
        save_data(d)
        try: await context.bot.send_message(uid,text)
        except Exception: pass
    await context.bot.send_message(game["chat_id"],"🏁 O‘yin yakunlandi.")

async def inactive_group_command(update,context): return

GROUP_VISIBLE_COMMANDS=[BotCommand("gamecreate","O‘yin yaratish"),BotCommand("gamestart","O‘yinni boshlash"),BotCommand("gamestop","O‘yinni to‘xtatish"),BotCommand("gameexit","O‘yindan chiqish"),BotCommand("paragame","Para o‘yini yaratish")]
GROUP_HIDDEN_COMMANDS=["para","mypara","dpara","money","give","gift","contest","dcontest","contesters","top","today","groups","richdiamond","richdollar"]

async def gamestop(update,context):
    if update.effective_chat.type not in ("group","supergroup"): return
    game=active_game(update.effective_chat.id)
    if not game: return
    game["phase"]="cancelled"
    if game.get("registration_message_id"):
        try: await context.bot.delete_message(game["chat_id"],game["registration_message_id"])
        except Exception: pass
    await update.message.reply_text("❌ O‘yin bekor qilindi.")

async def post_init(application): await application.bot.set_my_commands(GROUP_VISIBLE_COMMANDS,scope=BotCommandScopeAllGroupChats())

async def callback_handler(update,context):
    q=update.callback_query; data=q.data
    if data.startswith("lang_"): await language_button(update,context)
    elif data=="profile": await q.answer(); await q.message.edit_text(get_profile_text(q.from_user),reply_markup=get_profile_buttons())
    elif data=="dollar_exchange": await dollar_exchange(update,context)
    elif data.startswith("exchange_"): await exchange_dollar(update,context)
    elif data=="diamond_buy": await diamond_buy(update,context)
    elif data=="shop": await shop(update,context)
    elif data.startswith("buy_"): await buy_item(update,context)
    elif data=="items_info": await items_info(update,context)
    elif data=="item_control": await item_control(update,context)
    elif data.startswith("toggle_"): await toggle_item(update,context)
    elif data.startswith("noop_") or data=="noop": await q.answer()
    elif data=="hero": await hero(update,context)
    elif data=="hero_levels": await hero_levels(update,context)
    elif data=="hero_skills": await hero_skills(update,context)
    elif data.startswith("role_"): await role_button(update,context)
    elif data.startswith("join_"): await join_game(update,context)
    elif data.startswith("cancel_"): await cancel_game(update,context)
    elif data.startswith("night_"): await night_action(update,context)
    elif data.startswith("vote_"): await vote_choose(update,context)
    elif data.startswith("confirm_"): await vote_confirm(update,context)
    elif data.startswith("reject_"): await vote_reject(update,context)
    else: await q.answer()

def main():
    if not TOKEN: raise RuntimeError("BOT_TOKEN Secret topilmadi")
    app=Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("profile",profile)); app.add_handler(CommandHandler("roles",roles))
    app.add_handler(CommandHandler("gamecreate",gamecreate)); app.add_handler(CommandHandler("gamestart",gamestart)); app.add_handler(CommandHandler("gamestop",gamestop)); app.add_handler(CommandHandler("gameexit",gameexit)); app.add_handler(CommandHandler("paragame",inactive_group_command))
    for command in GROUP_HIDDEN_COMMANDS: app.add_handler(CommandHandler(command,inactive_group_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.run_polling(drop_pending_updates=True,allowed_updates=Update.ALL_TYPES)

if __name__=="__main__": main()
