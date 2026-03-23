import logging
import re
import asyncio
import time
import os

from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    filters, ContextTypes
)

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ===== FEATURE CONTROL =====
ALLOW_TEXT = True
ALLOW_PHOTO = True
ALLOW_VIDEO = True

ENABLE_PROMOTION_FILTER = True
ENABLE_ABUSE_FILTER = True

logging.basicConfig(level=logging.INFO)

# ================= DATA =================
media_groups = {}
users = {}
stats = {"text": 0, "photo": 0, "video": 0}

# ================= PROMOTION FILTER (FULL POWER) =================
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

# ================= ABUSE =================
def is_abusive(text):
    if not text:
        return False

    text = text.lower()

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
    return any(w in text for w in bad_words)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Admin Mode Active\n\n"
            "Commands:\n"
            "/stats\n/broadcast\n/schedule"
        )
        return

    await update.message.reply_text(
        "✨ Welcome!\n\n"
        "📩 Send message / image / video\n\n"
        "⚠️ No promotion allowed\n"
        "⚠️ No abusive content\n\n"
        "🚀 Your message will be sent to channel"
    )

# ================= STATS =================
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        f"📊 Stats\n\n"
        f"👥 Users: {len(users)}\n"
        f"📝 Text: {stats['text']}\n"
        f"🖼 Images: {stats['photo']}\n"
        f"🎥 Videos: {stats['video']}"
    )

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    msg = " ".join(context.args)
    if not msg:
        return await update.message.reply_text("Use: /broadcast message")

    for u in users:
        try:
            await context.bot.send_message(u, msg)
        except:
            pass

    await update.message.reply_text("✅ Broadcast Done")

# ================= SCHEDULE =================
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        return await update.message.reply_text("Use: /schedule seconds message")

    sec = int(context.args[0])
    msg = " ".join(context.args[1:])

    await update.message.reply_text(f"⏳ Scheduled in {sec} sec")

    await asyncio.sleep(sec)
    await context.bot.send_message(CHANNEL_ID, msg)

# ================= ALBUM =================
async def send_album(context, gid):
    await asyncio.sleep(2)

    if gid in media_groups:
        await context.bot.send_media_group(CHANNEL_ID, media_groups[gid])
        del media_groups[gid]

# ================= FORWARD =================
async def forward_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    msg = update.message
    text = msg.text or msg.caption or ""

    users[uid] = time.time()

    # ===== FILTER =====
    if uid != ADMIN_ID:
        if ENABLE_PROMOTION_FILTER and is_promotion(text):
            return await msg.reply_text("❌ Promotion not allowed")

        if ENABLE_ABUSE_FILTER and is_abusive(text):
            return await msg.reply_text("⚠️ Abuse not allowed")

    # ===== ALBUM =====
    if msg.media_group_id:
        gid = msg.media_group_id

        if gid not in media_groups:
            media_groups[gid] = []
            context.application.create_task(send_album(context, gid))

        if msg.photo:
            media_groups[gid].append(
                InputMediaPhoto(
                    msg.photo[-1].file_id,
                    caption=msg.caption if len(media_groups[gid]) == 0 else ""
                )
            )
            stats["photo"] += 1

        elif msg.video:
            media_groups[gid].append(
                InputMediaVideo(
                    msg.video.file_id,
                    caption=msg.caption if len(media_groups[gid]) == 0 else ""
                )
            )
            stats["video"] += 1

        return

    # ===== SINGLE =====
    if msg.text:
        await context.bot.send_message(CHANNEL_ID, msg.text)
        stats["text"] += 1

    elif msg.photo:
        await context.bot.send_photo(CHANNEL_ID, msg.photo[-1].file_id, caption=msg.caption or "")
        stats["photo"] += 1

    elif msg.video:
        await context.bot.send_video(CHANNEL_ID, msg.video.file_id, caption=msg.caption or "")
        stats["video"] += 1

    else:
        return await msg.reply_text("❌ Only allowed formats")

    await msg.reply_text("✅ Sent successfully")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats_cmd))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("schedule", schedule))

app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

print("🔥 Bot Running...")
app.run_polling()
