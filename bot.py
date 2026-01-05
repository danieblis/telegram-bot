import requests
import telebot
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "@aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ذخیره هش‌ها برای هر کاربر
user_last_hashes = {}
# ذخیره وضعیت Pending برای نوتیفیکیشن
pending_transactions = {}

# تشخیص هش TRX
def is_tx_hash(text):
    return bool(re.fullmatch(r"[a-fA-F0-9]{64}", text))

# بررسی تراکنش از Tronscan
def check_trx(tx_hash):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None

    data = r.json()
    if "contractData" not in data:
        return None

    sender = data.get("ownerAddress", "نامشخص")
    receiver = data.get("toAddress", "نامشخص")
    amount = data.get("contractData", {}).get("amount", 0) / 1_000_000
    token = data.get("tokenInfo", {}).get("tokenAbbr", "TRX")
    status = "✅ موفق" if data.get("confirmed") else "⏳ در انتظار تأیید"

    tx_link = f"https://tronscan.org/#/transaction/{tx_hash}"

    # هش بزرگ
    big_tx = "💥 تراکنش بزرگ!" if amount >= 1000 else ""

    # دکمه‌های inline
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("نمایش در Tronscan", url=tx_link),
        InlineKeyboardButton("کانال ما", url=f"https://t.me/{CHANNEL[1:]}")
    )

    return {
        "text": (
            "💎━━━━━━━━━━━━━━━━💎\n"
            "*اطلاعات تراکنش TRON*\n"
            "💎━━━━━━━━━━━━━━━━💎\n\n"
            f"🔗 *Hash:*\n`{tx_hash}`\n\n"
            f"👤 *From:*\n`{sender}`\n\n"
            f"🎯 *To:*\n`{receiver}`\n\n"
            f"💰 *Amount:*\n`{amount} {token}` {big_tx}\n\n"
            f"📌 *Status:* {status}\n"
            "💠━━━━━━━━━━━━━━━━💠"
        ),
        "keyboard": keyboard,
        "status": status
    }

# نوتیفیکیشن خودکار برای Pending
def pending_checker():
    while True:
        time.sleep(60)  # هر 60 ثانیه بررسی کن
        for chat_id, tx_list in list(pending_transactions.items()):
            for tx_hash in tx_list:
                res = check_trx(tx_hash)
                if res and res["status"] == "✅ موفق":
                    bot.send_message(chat_id, f"🔔 تراکنش `{tx_hash}` تایید شد!", 
                                     reply_markup=res["keyboard"])
                    pending_transactions[chat_id].remove(tx_hash)
            if not pending_transactions.get(chat_id):
                pending_transactions.pop(chat_id, None)

threading.Thread(target=pending_checker, daemon=True).start()

# دستور /start
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(
        message.chat.id,
        "👋 سلام! من ربات هش چکر TRON هستم.\n\n"
        "💡 برای استفاده، فقط هش تراکنش 64 کاراکتری TRX رو بفرست.\n"
        "📜 دستورات:\n"
        "/last - نمایش 10 هش آخر شما\n"
        "/help - راهنمای ربات"
    )

# دستور /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "💡 راهنمای ربات:\n"
        "- هش 64 کاراکتری TRX رو بفرست تا اطلاعات تراکنش رو دریافت کنی.\n"
        "- /last : نمایش آخرین 10 هش ارسال‌شده توسط شما.\n"
        "- هش‌های Pending بعد از تایید به شما اطلاع داده می‌شوند."
    )

# دستور /last
@bot.message_handler(commands=['last'])
def show_last(message):
    txs = user_last_hashes.get(message.chat.id, [])
    if not txs:
        bot.send_message(message.chat.id, "❌ هیچ هش فرستاده نشده.")
        return
    text = "📝 آخرین هش‌های شما:\n\n"
    for tx in txs[-10:]:
        text += f"`{tx}`\n"
    bot.send_message(message.chat.id, text)

# دریافت همه پیام‌ها
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    texts = message.text.split()
    found = False
    for t in texts:
        if not is_tx_hash(t):
            continue
        found = True
        bot.send_message(message.chat.id, "⏳ در حال بررسی تراکنش...")
        try:
            res = check_trx(t)
            if not res:
                bot.send_message(message.chat.id, "❌ تراکنش پیدا نشد")
            else:
                bot.send_message(
                    message.chat.id,
                    res["text"],
                    reply_markup=res["keyboard"],
                    disable_web_page_preview=True
                )
                # ذخیره هش کاربر
                user_last_hashes.setdefault(message.chat.id, []).append(t)
                if len(user_last_hashes[message.chat.id]) > 10:
                    user_last_hashes[message.chat.id].pop(0)
                # اگر Pending بود، ذخیره برای نوتیفیکیشن
                if res["status"] != "✅ موفق":
                    pending_transactions.setdefault(message.chat.id, []).append(t)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا:\n`{e}`")
    if not found:
        bot.send_message(message.chat.id, "❌ هش معتبر پیدا نشد\nفقط هش 64 کاراکتری TRX بفرست")

print("🤖 Bot is running...")
bot.infinity_polling()
