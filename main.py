import telebot
import re
import time
import threading
import os
import json
from flask import Flask

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ================= FLASK =================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Alive 🔥"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ================= DATA =================
DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "stats": {"text": 0, "photo": 0, "video": 0}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# ================= PROMOTION FILTER =================
def is_promotion(text):
    if not text:
        return False

    text = text.lower()

    patterns = [

# 🌐 BASIC LINKS
r"http[s]?://", r"www\.", r"\.com", r"\.in", r"\.net", r"\.org", r"\.xyz",
r"\.info", r"\.biz", r"\.site", r"\.online", r"\.store", r"\.tech",

# 🌍 MORE DOMAINS
r"\.co", r"\.me", r"\.cc", r"\.tv", r"\.io", r"\.app", r"\.pro",
r"\.club", r"\.live", r"\.space", r"\.fun", r"\.top", r"\.link",

# 📱 TELEGRAM
r"t\.me", r"telegram\.me", r"telegram\.org", r"joinchat", r"tg://",
r"telegram\.dog", r"t\.dog",

# 📺 YOUTUBE
r"youtube\.com", r"youtu\.be", r"youtube\.in", r"youtube\.co",
r"yt\.be", r"ytimg\.com",

# 📸 INSTAGRAM
r"instagram\.com", r"instagr\.am", r"insta\.com",

# 📘 FACEBOOK
r"facebook\.com", r"fb\.com", r"fb\.me", r"m\.facebook\.com",

# 💬 WHATSAPP
r"wa\.me", r"whatsapp\.com", r"chat\.whatsapp\.com",

# 🎮 DISCORD
r"discord\.gg", r"discord\.com", r"discordapp\.com",

# 🐦 TWITTER / X
r"twitter\.com", r"x\.com", r"t\.co",

# 🎵 OTHER SOCIAL
r"snapchat\.com", r"linkedin\.com", r"pinterest\.com",
r"reddit\.com", r"threads\.net",

# 👤 USERNAMES / TAGS
r"@[\w_]+", r"#\w+",

# 💰 EARNING / SCAM
r"earn\s?money", r"make\s?money", r"free\s?money",
r"online\s?earning", r"earn\s?daily", r"passive\s?income",
r"work\s?from\s?home", r"easy\s?money", r"get\s?paid",

# 🎁 OFFERS
r"free\s?recharge", r"free\s?offer", r"bonus\s?code",
r"promo\s?code", r"discount\s?code", r"gift\s?card",
r"giveaway", r"contest", r"win\s?money", r"win\s?prize",

# 📢 PROMO ACTION WORDS
r"join\s?(now|fast|channel|group)",
r"subscribe\s?(now|fast)",
r"follow\s?(me|now)",
r"click\s?(here|link)",
r"visit\s?(my|site|link)",
r"check\s?(my|link)",
r"watch\s?(now|video)",

# 🔗 LINK TRICKS
r"link\s?(in\s?bio|below)",
r"bio\s?link", r"click\s?link",
r"tap\s?link", r"open\s?link",

# 📦 DOWNLOAD / APK
r"download\s?(app|apk)", r"install\s?(app|now)",
r"apk\s?download", r"mod\s?apk", r"crack\s?apk",

# 🛒 SHOP / SELL
r"buy\s?now", r"order\s?now", r"shop\s?now",
r"product\s?link", r"sale\s?now", r"limited\s?offer",

# 💳 CRYPTO / INVEST
r"crypto", r"bitcoin", r"usdt", r"trading",
r"forex", r"investment", r"double\s?money",

# 📱 APP PROMO
r"playstore", r"appstore", r"download\s?now",
r"install\s?now", r"app\s?link",

# 🔞 ADULT
r"xxx", r"adult\s?site", r"porn", r"nude",
r"onlyfans", r"premium\s?content",

# ⚠️ BYPASS (SPACED TEXT)
r"y\s?o\s?u\s?t\s?u\s?b\s?e",
r"i\s?n\s?s\s?t\s?a",
r"f\s?a\s?c\s?e\s?b\s?o\s?o\s?k",
r"t\s?e\s?l\s?e\s?g\s?r\s?a\s?m",

# 🔤 MIXED CASE TRICKS
r"Y[o0]u[t7]u[b8]e",
r"1nstagram", r"faceb00k",

# 🧠 EXTRA SMART
r"dm\s?me", r"inbox\s?me", r"message\s?me",
r"contact\s?me", r"reach\s?me",

# 📢 CHANNEL PROMO
r"my\s?channel", r"new\s?channel",
r"telegram\s?channel", r"join\s?group",

# 🔥 URGENCY
r"hurry\s?up", r"limited\s?time",
r"act\s?fast", r"offer\s?ending",

# 🧪 RANDOM SPAM WORDS
r"viral\s?video", r"latest\s?video",
r"check\s?this", r"must\s?watch",

# 🔗 URL SHORTENER
r"bit\.ly", r"tinyurl", r"shorturl",
r"goo\.gl", r"t\.ly", r"cutt\.ly",

# 🌍 FILE HOSTING
r"drive\.google\.com", r"mega\.nz",
r"mediafire\.com", r"dropbox\.com",

# 🎮 GAME / HACK
r"mod\s?menu", r"hack\s?apk",
r"unlimited\s?money", r"cheat\s?code",

# 💬 CHAT LINKS
r"chat\s?link", r"group\s?link",
r"invite\s?link", r"join\s?link",

# 📣 ADS
r"ads", r"advertise", r"advertisement",
r"sponsor", r"sponsored",

# 🧾 RANDOM PROMO TEXT
r"best\s?offer", r"cheap\s?price",
r"discount\s?available", r"limited\s?deal"
]

    promo_words = [

# 📢 BASIC PROMO
"subscribe","sub","subscribe now","subscribe fast",
"follow","follow me","follow now","follow fast",
"join","join now","join fast","join channel","join group",
"click","click here","click link","click now",
"visit","visit now","visit link","visit site",
"check","check this","check link","check out",
"link","link below","link in bio","bio link",

# 📺 SOCIAL MEDIA
"youtube","yt channel","subscribe yt","watch youtube",
"instagram","insta","follow insta","insta page",
"facebook","fb page","like page",
"telegram","telegram channel","tg channel","t.me",
"whatsapp","wa group","join whatsapp",
"discord","join discord",
"snapchat","snap id",
"twitter","x follow","tweet link",

# 📢 PROMOTION / ADS
"promotion","promote","promotion available",
"sponsor","sponsored","sponsorship",
"advertise","advertisement","ads","run ads",
"paid promotion","collab","brand deal",

# 💰 EARNING / MONEY
"earn","earn money","earn fast","earn daily",
"make money","online earning","passive income",
"work from home","easy money","quick money",
"double money","income source","side income",

# 🎁 OFFERS / GIVEAWAY
"free","free money","free recharge","free offer",
"giveaway","contest","lucky draw",
"win money","win prize","gift card",
"bonus","bonus code","signup bonus",
"promo code","discount code","referral code",

# 🛒 SHOP / SELL
"buy now","order now","shop now",
"product link","cheap price","best price",
"discount","big sale","flash sale",
"limited offer","special offer",

# 📦 DOWNLOAD / APK
"download","download app","download apk",
"install now","install app",
"apk","mod apk","hack apk","premium apk",

# 🎮 GAME / HACK
"hack","cheat","mod menu",
"unlimited money","free skins",
"game hack","unlock all",

# 💳 CRYPTO / INVEST
"crypto","bitcoin","usdt","trading",
"forex","investment","profit daily",
"double income","trading signal",

# 🔞 ADULT / SPAM
"adult","adult site","xxx","porn",
"nude","onlyfans","premium content",

# 📢 CHANNEL PROMO
"my channel","new channel","join my channel",
"best channel","growing channel",
"telegram group","join my group",

# 🔗 LINK TRICKS
"click link","tap link","open link",
"link here","link below","link bio",

# 🧠 CONTACT / DM
"dm me","dm for","message me",
"inbox me","contact me","reach me",

# 📣 URGENCY
"hurry up","act fast","limited time",
"offer ending","last chance",

# 🎥 VIDEO PROMO
"watch now","new video","latest video",
"must watch","viral video",
"watch full video","stream now",

# 🧪 RANDOM PROMO
"best offer","top deal","amazing offer",
"exclusive deal","premium access",
"unlock now","join fast","fast join",

# 🌍 WEBSITE PROMO
"website","visit website","my website",
"official site","check website",

# 🧾 REFERRAL / INVITE
"invite code","ref code","use code",
"signup link","register now",

# ⚠️ SPAM VARIATIONS
"sub pls","pls follow","plz subscribe",
"join pls","follow pls","check pls",
"click pls","visit pls"
]

    for p in patterns:
        if re.search(p, text):
            return True

    for w in promo_words:
        if w in text:
            return True

    return False

# ================= ABUSE FILTER =================
def is_abusive(text):
    if not text:
        return False

    bad_words = [

# 🇮🇳 HINDI GAALI
"mc","bc","madarchod","behenchod","bhenchod","maderchod",
"gandu","gaand","gaandu","gand","gandmar","gaandmar",
"chutiya","chut","chutiyapa","chutmarika",
"lund","loda","lawda","lodu",
"bhosdike","bhosdi","bhosda",
"randi","rand","raand","randa",
"harami","kamina","kameena",
"kutta","kutte","kutti",
"saala","saali","sala",
"ullu","ullu ka pattha",
"jhantu","jhant","jhaant",
"tatti","tatti kha",
"gaand phaad","gand phaad",
"gand maar","gaand maar",
"chod","chodu","chudai","chudne","chudwana","chud gaya",
"chod de","chodna","chod diya",
"madar","behen","maa ki","behen ki",
"teri maa","teri behen",

# 🇬🇧 ENGLISH GAALI
"fuck","fucker","fucking",
"shit","bullshit",
"asshole","ass","asshole",
"bitch","bitches",
"bastard","slut","whore",
"dick","pussy",
"motherfucker","mf",
"sex","sexy",
"porn","xxx","nude",
"boobs","tits","breasts",
"dildo","condom",
"masturbate",

# ⚠️ VIOLENCE / THREATS
"rape","rapist",
"kill","kill you","die","die now",
"marja","mar ja","maro","mar dalega",

# 🧠 TOXIC WORDS
"bakchod","bakchodi","bakwas",
"faltu","bewakoof","bewkuf",
"pagal","pagle","pagli",
"chakka","hijra","napunsak",

# 🔤 VARIATIONS / BYPASS
"m@darchod","b#henchod","g@ndu",
"chut1ya","f*ck","sh!t",
"b!tch","a$$hole","p*ssy",

# ⚠️ MIXED SPELLING
"madar chod","behen chod","gaand maar",
"gand mar","lund le","lund kha",

# 🧪 RANDOM ABUSE
"stupid","idiot","moron",
"loser","noob","trash",
"dog","pig","donkey",

# 🔞 EXTRA
"sex chat","nude pic","send nudes",
"adult talk","dirty talk"
]
    return any(w in text.lower() for w in bad)

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "👑 Admin Mode\n/stats\n/broadcast\n/schedule")
    else:
        bot.reply_to(message,
            "✨ Welcome!\n\n📩 Send message/photo/video\n\n⚠️ No promotion\n⚠️ No abuse"
        )

# ================= STATS =================
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    total_users = len(data["users"])

    now = time.time()
    active_users = sum(
        1 for u in data["users"].values()
        if now - u["last_active"] < 86400
    )

    stats = data["stats"]

    try:
        chat = bot.get_chat(CHANNEL_ID)
        bot_info = bot.get_me()
        channel_name = chat.title
        bot_name = bot_info.first_name
        bot_username = bot_info.username
    except:
        channel_name = CHANNEL_ID
        bot_name = "Bot"
        bot_username = "unknown"

    bot.reply_to(message,
        f"📊 BOT STATS\n\n"
        f"👥 Total Users: {total_users}\n"
        f"⚡ Active (24h): {active_users}\n\n"
        f"📝 Text: {stats['text']}\n"
        f"🖼 Image: {stats['photo']}\n"
        f"🎥 Video: {stats['video']}\n\n"
        f"📢 Channel: {channel_name}\n"
        f"🆔 ID: {CHANNEL_ID}\n"
        f"👑 Owner: {ADMIN_ID}\n"
        f"🤖 Bot: {bot_name} (@{bot_username})"
    )

# ================= BROADCAST =================
@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    bot.reply_to(message, "📢 Send message to broadcast")
    bot.register_next_step_handler(message, do_broadcast)

def do_broadcast(message):
    sent = 0

    for uid in data["users"]:
        try:
            uid = int(uid)
            if message.text:
                bot.send_message(uid, message.text)
            elif message.photo:
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                bot.send_video(uid, message.video.file_id, caption=message.caption or "")
            sent += 1
        except:
            pass

    bot.reply_to(message, f"✅ Broadcast sent to {sent} users")

# ================= SCHEDULE =================
@bot.message_handler(commands=['schedule'])
def schedule_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "Use: /schedule seconds")

    sec = int(args[1])
    bot.reply_to(message, f"⏳ Send content in {sec} sec")

    bot.register_next_step_handler(message, lambda m: do_schedule(m, sec))

def do_schedule(message, sec):
    def send_later():
        time.sleep(sec)
        try:
            if message.text:
                bot.send_message(CHANNEL_ID, message.text)
            elif message.photo:
                bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                bot.send_video(CHANNEL_ID, message.video.file_id, caption=message.caption or "")
        except:
            pass

    threading.Thread(target=send_later).start()

# ================= ALBUM =================
media_groups = {}

@bot.message_handler(content_types=['photo','video'], func=lambda m: m.media_group_id is not None)
def album_handler(message):
    gid = message.media_group_id

    if gid not in media_groups:
        media_groups[gid] = []
        threading.Timer(2, send_album, args=(gid,)).start()

    media_groups[gid].append(message)

def send_album(gid):
    msgs = media_groups.get(gid, [])
    if not msgs:
        return

    media = []
    for i, m in enumerate(msgs):
        if m.photo:
            media.append(telebot.types.InputMediaPhoto(
                m.photo[-1].file_id,
                caption=m.caption if i == 0 else ""
            ))
        elif m.video:
            media.append(telebot.types.InputMediaVideo(
                m.video.file_id,
                caption=m.caption if i == 0 else ""
            ))

    bot.send_media_group(CHANNEL_ID, media)
    del media_groups[gid]

# ================= FORWARD =================
@bot.message_handler(content_types=['text','photo','video'])
def forward(message):
    uid = message.from_user.id

    data["users"][str(uid)] = {"last_active": time.time()}

    text = message.text or message.caption or ""

    if uid != ADMIN_ID:
        if is_promotion(text):
            return bot.reply_to(message, "❌ Promotion not allowed")
        if is_abusive(text):
            return bot.reply_to(message, "⚠️ Abuse not allowed")

    try:
        if message.text:
            bot.send_message(CHANNEL_ID, message.text)
            data["stats"]["text"] += 1

        elif message.photo:
            bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=message.caption or "")
            data["stats"]["photo"] += 1

        elif message.video:
            bot.send_video(CHANNEL_ID, message.video.file_id, caption=message.caption or "")
            data["stats"]["video"] += 1

        save_data()
        bot.reply_to(message, "✅ Sent")

    except:
        bot.reply_to(message, "❌ Error")

# ================= RUN =================
print("🔥 Bot Running...")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)    ]

    for w in promo_words:
        if w in text:
            return True

    return False

# ================= ABUSE FILTER =================
def is_abusive(text):
    if not text:
        return False

    text = text.lower()

    bad_words = ["mc","bc","madarchod","behenchod","gandu","chutiya","fuck","shit","bitch"]
    return any(w in text for w in bad_words)

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id

    if user_id == ADMIN_ID:
        bot.reply_to(msg,
            "👑 Admin Mode Active\n\n"
            "Commands:\n"
            "/stats\n/broadcast\n/schedule"
        )
    else:
        bot.reply_to(msg,
            "✨ Welcome!\n\n"
            "📩 Send message / image / video\n\n"
            "⚠️ No promotion allowed\n"
            "⚠️ No abusive content\n\n"
            "🚀 Your message will be sent to channel"
        )

# ================= STATS =================
@bot.message_handler(commands=['stats'])
def stats_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.reply_to(msg,
        f"📊 Stats\n\n"
        f"👥 Users: {len(users)}\n"
        f"📝 Text: {stats['text']}\n"
        f"🖼 Images: {stats['photo']}\n"
        f"🎥 Videos: {stats['video']}"
    )

# ================= BROADCAST =================
@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    text = msg.text.replace("/broadcast ", "")
    if not text:
        return bot.reply_to(msg, "Use: /broadcast message")

    for u in users:
        try:
            bot.send_message(u, text)
        except:
            pass

    bot.reply_to(msg, "✅ Broadcast Done")

# ================= SCHEDULE =================
def send_later(sec, message):
    time.sleep(sec)
    bot.send_message(CHANNEL_ID, message)

@bot.message_handler(commands=['schedule'])
def schedule(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    args = msg.text.split()

    if len(args) < 3:
        return bot.reply_to(msg, "Use: /schedule seconds message")

    sec = int(args[1])
    message = " ".join(args[2:])

    bot.reply_to(msg, f"⏳ Scheduled in {sec} sec")

    threading.Thread(target=send_later, args=(sec, message)).start()

# ================= MAIN HANDLER =================
@bot.message_handler(content_types=['text','photo','video'])
def handle(msg):
    user_id = msg.from_user.id
    users[user_id] = time.time()

    text = msg.text if msg.content_type == 'text' else msg.caption

    # ===== FILTER =====
    if user_id != ADMIN_ID:
        if is_promotion(text):
            return bot.reply_to(msg, "❌ Promotion not allowed")

        if is_abusive(text):
            return bot.reply_to(msg, "⚠️ Abuse not allowed")

    # ===== TEXT =====
    if msg.content_type == 'text':
        bot.send_message(CHANNEL_ID, msg.text)
        stats["text"] += 1

    # ===== PHOTO =====
    elif msg.content_type == 'photo':
        bot.send_photo(
            CHANNEL_ID,
            msg.photo[-1].file_id,
            caption=msg.caption or ""
        )
        stats["photo"] += 1

    # ===== VIDEO =====
    elif msg.content_type == 'video':
        bot.send_video(
            CHANNEL_ID,
            msg.video.file_id,
            caption=msg.caption or ""
        )
        stats["video"] += 1

    bot.reply_to(msg, "✅ Sent successfully")

# ================= RUN =================
print("🔥 Bot Running...")

while True:
    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60
        )
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
