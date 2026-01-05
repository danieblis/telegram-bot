import requests
import telebot
import re
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ====== تنظیمات ======
BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "@aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ذخیره هش‌ها برای هر کاربر
user_last_hashes = {}
# ذخیره تراکنش‌های Pending برای نوتیفیکیشن
pending_transactions = {}

HASH_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")

# ====== استخراج هش ======
def extract_hash(text):
    if not text:
        return None
    m = HASH_RE.search(text)
    return m.group(0) if m else None

# ====== بررسی تراکنش ======
def check_trx(tx_hash):
    url = "https://apilist.tronscan.org/api/transaction-info"
    try:
        r = requests.get(url, params={"hash": tx_hash}, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        if "contractData" not in data:
            return None
        sender = data.get("ownerAddress", "نامشخص")
        receiver = data.get("toAddress", "نامشخص")
        amount = data.get("contractData", {}).get("amount", 0) / 1_000_000
        token = data.get("tokenInfo", {}).get("tokenAbbr", "TRX")
        confirmed = data.get("confirmed", False)
        return {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token,
            "status": "✅ تایید شده" if confirmed else "⏳ در انتظار تایید"
        }
    except requests.exceptions.RequestException:
        return "NETWORK_ERROR"

# ====== نوتیفیکیشن Pending ======
def pending_checker():
    while True:
        time.sleep(60)
        for chat_id, tx_list in list(pending_transactions.items()):
            for tx_hash in tx_list:
                res = check_trx(tx_hash)
                if res and res["status"] == "✅ تایید شده":
                    kb = InlineKeyboardMarkup()
                    kb.add(InlineKeyboardButton("نمایش در Tronscan", url=f"https://tronscan.org/#/transaction/{tx_hash}"))
                    bot.send_message(chat_id, f"🔔 تراکنش `{tx_hash}` تایید شد!", reply_markup=kb)
                    pending_transactions[chat_id].remove(tx_hash)
            if not pending_transactions.get(chat_id):
                pending_transactions.pop(chat_id, None)

threading.Thread(target=pending_checker, daemon=True).start()

# ====== دستور /start ======
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(
        message.chat.id,
        "👋 سلام! من ربات هش چکر a Q a  P e J a k هستم.\n\n"
        "💡 برای استفاده، فقط هش تراکنش 64 کاراکتری TRX رو بفرست.\n"
        "📜 دستورات:\n"
        "/last - نمایش 10 هش آخر شما\n"
        "/help - راهنمای ربات"
    )

# ====== دستور /help ======
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "💡 راهنمای ربات:\n"
        "- هش 64 کاراکتری TRX رو بفرست تا اطلاعات تراکنش رو دریافت کنی.\n"
        "- /last : نمایش آخرین 10 هش ارسال‌شده توسط شما.\n"
        "- هش‌های Pending بعد از تایید به شما اطلاع داده می‌شوند."
    )

# ====== دستور /last ======
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

# ====== دریافت همه پیام‌ها ======
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    tx_hash = extract_hash(message.text)
    if not tx_hash:
        return  # اگه هش نبود، هیچ پیامی نده

    bot.send_message(message.chat.id, "⏳ در حال بررسی تراکنش...")

    res = check_trx(tx_hash)
    if res == "NETWORK_ERROR":
        bot.send_message(message.chat.id, "❌ خطای اتصال به سرور TRON")
        return
    if not res:
        bot.send_message(message.chat.id, "❌ تراکنشی با این هش پیدا نشد")
        return

    # دکمه‌های inline
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("نمایش در Tronscan", url=f"https://tronscan.org/#/transaction/{tx_hash}"),
        InlineKeyboardButton("کانال ما", url=f"https://t.me/{CHANNEL[1:]}")
    )

    # هش بزرگ
    big_tx = "💥 تراکنش بزرگ!" if res["amount"] >= 1000 else ""

    text = (
        "💎 *اطلاعات تراکنش TRON*\n"
        "━━━━━━━━━━━━━━━\n"
        f"🔗 *Hash:*\n`{tx_hash}`\n\n"
        f"👤 *From:*\n`{res['sender']}`\n\n"
        f"🎯 *To:*\n`{res['receiver']}`\n\n"
        f"💰 *Amount:* `{res['amount']} {res['token']}` {big_tx}\n"
        f"📌 *Status:* {res['status']}\n"
        "━━━━━━━━━━━━━━━"
    )

    bot.send_message(message.chat.id, text, reply_markup=kb, disable_web_page_preview=True)

    # ذخیره هش کاربر
    user_last_hashes.setdefault(message.chat.id, []).append(tx_hash)
    if len(user_last_hashes[message.chat.id]) > 10:
        user_last_hashes[message.chat.id].pop(0)

    # ذخیره Pending
    if res["status"] != "✅ تایید شده":
        pending_transactions.setdefault(message.chat.id, []).append(tx_hash)

# ====== اجرا ======
print("🤖 Bot is running...")
bot.infinity_polling(skip_pending=True)
