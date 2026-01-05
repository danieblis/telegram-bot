import requests
import telebot
import re

BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "@aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN)

# بررسی هش TRX
def is_tx_hash(text):
    return bool(re.fullmatch(r"[a-fA-F0-9]{64}", text))

# چک تراکنش
def check_trx(tx_hash):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
    r = requests.get(url, timeout=10)
    data = r.json()

    if "contractData" not in data:
        return None

    sender = data.get("ownerAddress", "❌ نامشخص")
    receiver = data.get("toAddress", "❌ نامشخص")
    amount = data.get("contractData", {}).get("amount", 0) / 1_000_000
    token = data.get("tokenInfo", {}).get("tokenAbbr", "TRX")
    status = "✅ موفق" if data.get("confirmed") else "⏳ در انتظار تایید"

    tx_link = f"https://tronscan.org/#/transaction/{tx_hash}"

    # پیام گرافیکی و حرفه‌ای
    return (
        f"💎━━━━━━━━━━━━━━━━💎\n"
        f"        **اطلاعات تراکنش TRON**\n"
        f"💎━━━━━━━━━━━━━━━━💎\n\n"
        f"🔗 **Hash:**\n`{tx_hash}`\n[نمایش در Tronscan]({tx_link})\n\n"
        f"👤 **From:**\n`{sender}`\n\n"
        f"🎯 **To:**\n`{receiver}`\n\n"
        f"💰 **Amount:**\n`{amount} {token}`\n\n"
        f"📌 **Status:** {status}\n\n"
        f"💠━━━━━━━━━━━━━━━━💠\n"
        f"📢 کانال ما: [{CHANNEL}](https://t.me/aQa_pejak_jenel1)\n"
        f"💠━━━━━━━━━━━━━━━━💠"
    )

# ذخیره آخرین هش‌ها برای هر کاربر
user_last_hashes = {}

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    texts = message.text.split()
    found_hash = False

    for text in texts:
        tx_hash = text.strip()
        if not is_tx_hash(tx_hash):
            continue
        found_hash = True

        try:
            # ذخیره آخرین هش‌ها
            user_last_hashes.setdefault(message.chat.id, [])
            user_last_hashes[message.chat.id].append(tx_hash)
            if len(user_last_hashes[message.chat.id]) > 10:
                user_last_hashes[message.chat.id].pop(0)

            bot.send_message(message.chat.id, "⏳ در حال بررسی تراکنش...")
            result = check_trx(tx_hash)

            if not result:
                bot.send_message(message.chat.id, f"❌ تراکنش `{tx_hash}` پیدا نشد")
                continue

            bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا:\n{e}")

    if not found_hash:
        
print("🤖 Bot is running...")
bot.polling(none_stop=True)
