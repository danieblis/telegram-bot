import os
import requests
from flask import Flask, request
import telebot
from datetime import datetime

# ====== TOKEN ======
TOKEN = os.environ.get("8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ====== PRICE API ======
CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=usd"
DOLLAR_API = "https://api.exchangerate-api.com/v4/latest/USD"

# ====== FUNCTIONS ======
def get_tron_price():
    try:
        r = requests.get(CRYPTO_API, timeout=10).json()
        return r["tron"]["usd"]
    except:
        return None

def get_dollar_price():
    try:
        r = requests.get(DOLLAR_API, timeout=10).json()
        return r["rates"]["IRR"]
    except:
        return None

# ====== BOT HANDLER ======
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")

    tron = get_tron_price()
    dollar = get_dollar_price()

    if tron is None or dollar is None:
        bot.reply_to(message, "❌ خطا در دریافت قیمت‌ها!")
        return

    if "ترون" in text or "trx" in text:
        msg = f"""
💎 قیمت ترون (TRX)

🔹 قیمت جهانی: {tron} دلار
🔹 معادل تومان: {int(tron * dollar):,} تومان

🕒 {now}
"""
        bot.reply_to(message, msg)

    elif "دلار" in text or "$" in text:
        msg = f"""
💵 قیمت دلار

🔹 نرخ روز: {int(dollar):,} تومان

🕒 {now}
"""
        bot.reply_to(message, msg)

    else:
        bot.reply_to(
            message,
            "✳️ برای دریافت قیمت بنویس:\n\nدلار\nترون"
        )

# ====== WEBHOOK ======
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running", 200

# ====== START ======
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR-RENDER-URL.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
