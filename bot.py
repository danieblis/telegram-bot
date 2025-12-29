import telebot
from flask import Flask, request
import requests
from datetime import datetime
import os

TOKEN = os.environ.get("8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

coins = {
    "ترون": "tron",
    "بیت کوین": "bitcoin",
    "اتریوم": "ethereum",
    "تتر": "tether"
}

def get_price(coin_id):
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        )
        return r.json()[coin_id]["usd"]
    except:
        return None

@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text.strip()
    now = datetime.now().strftime("%Y/%m/%d %H:%M")

    if text in coins:
        price = get_price(coins[text])
        if price:
            bot.send_message(
                message.chat.id,
                f"💰 قیمت {text}\n\n"
                f"💵 {price} دلار\n"
                f"🕒 {now}"
            )
        else:
            bot.send_message(message.chat.id, "❌ خطا در دریافت قیمت")
    else:
        bot.send_message(
            message.chat.id,
            "❗️اسم ارز رو فارسی بفرست:\n"
            "ترون\nبیت کوین\nاتریوم\nتتر"
        )

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
