import requests
import telebot

BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "https://t.me/aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN)

# وقتی /start یا /check زده شد
@bot.message_handler(commands=["start", "check"])
def ask_hash(message):
    bot.send_message(
        message.chat.id,
        "برای چک کردن لطفا هش رو بفرست!👤"
    )

# وقتی کاربر هش فرستاد
@bot.message_handler(func=lambda m: True)
def check_tx(message):
    tx_hash = message.text.strip()

    if len(tx_hash) < 20:
        bot.send_message(message.chat.id, "❌ هش نامعتبره")
        return

    bot.send_message(message.chat.id, "⏳ در حال بررسی تراکنش...")

    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if "contractData" not in data:
            bot.send_message(message.chat.id, "❌ تراکنش پیدا نشد")
            return

        sender = data.get("ownerAddress", "نامشخص")
        receiver = data.get("toAddress", "نامشخص")
        amount = data.get("contractData", {}).get("amount", 0) / 1_000_000
        token = data.get("tokenInfo", {}).get("tokenAbbr", "TRX")
        status = "✅ موفق" if data.get("confirmed") else "⏳ در انتظار تایید"

        msg = (
            "📄 اطلاعات تراکنش\n\n"
            f"🔗 Hash:\n{tx_hash}\n\n"
            f"👤 From:\n{sender}\n\n"
            f"🎯 To:\n{receiver}\n\n"
            f"💰 Amount:\n{amount} {token}\n\n"
            f"📌 Status: {status}\n\n"
            f"📢 Channel: {CHANNEL}"
        )

        bot.send_message(message.chat.id, msg)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا:\n{e}")

print("🤖 Bot is running...")
bot.infinity_polling()
