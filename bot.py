import requests
import telebot
import re

BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "https://t.me/aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN)

# بررسی اینکه متن هش تراکنش TRX هست یا نه
def is_tx_hash(text):
    return bool(re.fullmatch(r"[a-fA-F0-9]{64}", text))

# چک کردن تراکنش
def check_trx(tx_hash):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
    r = requests.get(url, timeout=10)
    data = r.json()

    if "contractData" not in data:
        return None

    sender = data.get("ownerAddress", "نامشخص")
    receiver = data.get("toAddress", "نامشخص")
    amount = data.get("contractData", {}).get("amount", 0) / 1_000_000
    token = data.get("tokenInfo", {}).get("tokenAbbr", "TRX")
    status = "✅ موفق" if data.get("confirmed") else "⏳ در انتظار تایید"

    # پیام با گرافیک بهتر
    return (
        f"━━━━━━━━━━━━━━\n"
        f"📄 **اطلاعات تراکنش** 📄\n"
        f"━━━━━━━━━━━━━━\n"
        f"🔗 **Hash:**\n`{tx_hash}`\n\n"
        f"👤 **From:**\n`{sender}`\n\n"
        f"🎯 **To:**\n`{receiver}`\n\n"
        f"💰 **Amount:**\n`{amount} {token}`\n\n"
        f"📌 **Status:** {status}\n"
        f"━━━━━━━━━━━━━━\n"
        f"📢 کانال ما: {CHANNEL}"
    )

# همه پیام‌ها رو چک می‌کنه
@bot.message_handler(func=lambda m: True)
def all_messages(message):
    tx_hash = message.text.strip()

    if not is_tx_hash(tx_hash):
        # اگه هش نبود، پیام نده و بی‌خیال باشه
        return

    try:
        bot.send_message(message.chat.id, "⏳ در حال بررسی تراکنش...")
        result = check_trx(tx_hash)

        if not result:
            bot.send_message(message.chat.id, "❌ تراکنش پیدا نشد")
            return

        # ارسال پیام با parse_mode برای Markdown
        bot.send_message(message.chat.id, result, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا:\n{e}")

print("🤖 Bot is running...")
bot.polling(none_stop=True)
