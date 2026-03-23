import telebot
import re
import time
import threading
import os

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ================= DATA =================
users = {}
stats = {"text": 0, "photo": 0, "video": 0}

# ================= PROMOTION FILTER =================
def is_promotion(text):
    if not text:
        return False

    text = text.lower()

    patterns = [
        r"http[s]?://", r"www\.", r"\.com", r"\.in", r"\.net", r"\.org",
        r"t\.me", r"youtube", r"instagram", r"facebook", r"@[\w_]+"
    ]

    for p in patterns:
        if re.search(p, text):
            return True

    promo_words = [
        "subscribe","follow","join","click","link","promotion",
        "earn money","free","offer","buy now","join channel"
    ]

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
bot.infinity_polling()
