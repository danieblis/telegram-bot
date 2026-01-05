import requests
import telebot
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========= تنظیمات =========
BOT_TOKEN = "8483312390:AAG87RcsCDBhJ8wKDISKpJlQgptj4jfjL7s"
CHANNEL = "@aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

HASH_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")

# ========= بررسی هش =========
def extract_hash(text):
    if not text:
        return None
    m = HASH_RE.search(text)
    return m.group(0) if m else None

# ========= چک تراکنش =========
def check_trx(tx_hash):
    url = "https://apilist.tronscan.org/api/transaction-info"
    try:
        r = requests.get(url, params={"hash": tx_hash}, timeout=8)
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

# ========= پیام‌ها =========
@bot.message_handler(content_types=["text"])
def handle_message(message):
    tx_hash = extract_hash(message.text)
    if not tx_hash:
        return  # ❌ اگه هش نبود، هیچی نگو (اسپم نکن)

    bot.send_message(message.chat.id, "⏳ در حال بررسی تراکنش...")

    result = check_trx(tx_hash)

    if result == "NETWORK_ERROR":
        bot.send_message(message.chat.id, "❌ خطای اتصال به سرور TRON")
        return

    if not result:
        bot.send_message(message.chat.id, "❌ تراکنشی با این هش پیدا نشد")
        return

    text = (
        "💎 *اطلاعات تراکنش TRON*\n"
        "━━━━━━━━━━━━━━━\n"
        f"🔗 *Hash:*\n`{tx_hash}`\n\n"
        f"👤 *From:*\n`{result['sender']}`\n\n"
        f"🎯 *To:*\n`{result['receiver']}`\n\n"
        f"💰 *Amount:* `{result['amount']} {result['token']}`\n"
        f"📌 *Status:* {result['status']}\n"
        "━━━━━━━━━━━━━━━\n"
        f"📢 {CHANNEL}"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "🔍 مشاهده در Tronscan",
            url=f"https://tronscan.org/#/transaction/{tx_hash}"
        )
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=kb,
        disable_web_page_preview=True
    )

# ========= اجرا =========
print("🤖 Bot started")
bot.infinity_polling(skip_pending=True)
