import telebot
import requests
from flask import Flask, request
from datetime import datetime
import os

TOKEN = os.environ.get("8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price"
FIAT_API = "https://api.coingecko.com/api/v3/simple/price"

def get_dollar_price():
    try:
        r = requests.get(FIAT_API, params={"ids":"usd","vs_currencies":"irr"}, timeout=10).json()
        return int(r["usd"]["irr"])
    except:
        return None

def get_crypto_prices():
    try:
        r = requests.get(CRYPTO_API, params={"ids":"tron,tether,bitcoin,ethereum","vs_currencies":"usd"}, timeout=10).json()
        return r
    except:
        return {}

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "💱 *ربات محاسبه قیمت ارز*\n\n"
        "✍️ مثال:\n50 دلار\n500 ترون\n100 تتر\n2 بیت‌کوین\n1 اتریوم",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def calc(msg):
    text = msg.text.replace(" ", "")
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")

    dollar = get_dollar_price()
    crypto = get_crypto_prices()

    if dollar is None or not crypto:
        bot.send_message(msg.chat.id, "❌ خطا در دریافت قیمت‌ها!")
        return

    try:
        if "دلار" in text:
            amount = float(text.replace("دلار",""))
            toman = int(amount * dollar)
            bot.send_message(msg.chat.id, f"💵 {amount} دلار\n💰 `{toman:,}` تومان\n🕒 {now}", parse_mode="Markdown")
        elif "ترون" in text:
            amount = float(text.replace("ترون",""))
            usd = amount * crypto["tron"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(msg.chat.id, f"🔴 {amount} ترون\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}", parse_mode="Markdown")
        elif "تتر" in text:
            amount = float(text.replace("تتر",""))
            usd = amount
            toman = int(usd * dollar)
            bot.send_message(msg.chat.id, f"🟢 {amount} تتر\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}", parse_mode="Markdown")
        elif "بیتکوین" in text or "بیت‌کوین" in text:
            amount = float(text.replace("بیتکوین","").replace("بیت‌کوین",""))
            usd = amount * crypto["bitcoin"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(msg.chat.id, f"₿ {amount} بیت‌کوین\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}", parse_mode="Markdown")
        elif "اتریوم" in text:
            amount = float(text.replace("اتریوم",""))
            usd = amount * crypto["ethereum"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(msg.chat.id, f"🔷 {amount} اتریوم\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}", parse_mode="Markdown")
        else:
            bot.send_message(msg.chat.id, "❌ ارز پشتیبانی نمی‌شود\n✍️ مثال صحیح:\n50 دلار\n500 ترون", parse_mode="Markdown")
    except:
        bot.send_message(msg.chat.id, "❌ فرمت پیام اشتباه است")

# ---------- Webhook ----------
PORT = int(os.environ.get("PORT", 10000))

@server.route(f"/{TOKEN}", methods=['POST'])
def get_message():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "ربات آنلاین است", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    server.run(host="0.0.0.0", port=PORT)
