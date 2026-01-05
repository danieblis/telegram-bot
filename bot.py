import requests
import telebot
import re

BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "@aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# تشخیص هش TRX (۶۴ کاراکتر hex)
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

    return (
        "💎━━━━━━━━━━━━━━━━💎\n"
        "*اطلاعات تراکنش TRON*\n"
        "💎━━━━━━━━━━━━━━━━💎\n\n"
        f"🔗 *Hash:*\n`{tx_hash}`\n"
        f"[مشاهده در Tronscan]({tx_link})\n\n"
        f"👤 *From:*\n`{sender}`\n\n"
        f"🎯 *To:*\n`{receiver}`\n\n"
        f"💰 *Amount:*\n`{amount} {token}`\n\n"
        f"📌 *Status:* {status}\n\n"
        "💠━━━━━━━━━━━━━━━━💠\n"
        f"📢 کانال: [{CHANNEL}](https://t.me/{CHANNEL[1:]})"
    )

# دریافت پیام‌ها (پیوی + گروه)
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
            result = check_trx(t)
            if not result:
                bot.send_message(message.chat.id, "❌ تراکنش پیدا نشد")
            else:
                bot.send_message(
                    message.chat.id,
                    result,
                    disable_web_page_preview=True
                )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا:\n`{e}`")

    if not found:
        bot.send_message(
            message.chat.id,
            "❌ هش معتبر پیدا نشد\n"
            "فقط هش ۶۴ کاراکتری TRX بفرست"
        )

print("🤖 Bot is running...")
bot.infinity_polling()
