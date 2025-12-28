import telebot
import requests
from datetime import datetime

# 🔐 توکن ربات
TOKEN = "7715687486:AAFzsYcAg306azyqMyrl6C1JQZQ7drN2OO8"

bot = telebot.TeleBot(TOKEN)

# API قیمت کریپتو
CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price"

# API قیمت دلار (آزاد)
DOLLAR_API = "https://api.tgju.org/v1/price/latest"

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "🤖 *ربات قیمت‌گیر*\n\n"
        "📌 مثال‌ها:\n"
        "▫️ `50 دلار`\n"
        "▫️ `500 ترون`\n"
        "▫️ `/price`\n\n"
        "⏱ قیمت‌ها لحظه‌ای"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['price'])
def price(message):
    try:
        crypto = requests.get(CRYPTO_API, params={
            "ids": "bitcoin,ethereum,tron,tether",
            "vs_currencies": "usd"
        }, timeout=10).json()

        dollar = requests.get(DOLLAR_API, timeout=10).json()
        dollar_price = int(float(dollar["data"]["price_dollar_rl"]["p"]))

        now = datetime.now().strftime("%Y/%m/%d - %H:%M")

        text = (
            "📊 *قیمت‌های امروز*\n\n"
            f"💵 دلار: `{dollar_price:,}` تومان\n"
            f"₿ بیت‌کوین: `${crypto['bitcoin']['usd']:,}`\n"
            f"🔷 اتریوم: `${crypto['ethereum']['usd']:,}`\n"
            f"🪙 ترون: `${crypto['tron']['usd']}`\n"
            f"💲 تتر: `${crypto['tether']['usd']}`\n\n"
            f"🕒 `{now}`"
        )

        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    except:
        bot.send_message(message.chat.id, "❌ خطا در دریافت قیمت‌ها")

@bot.message_handler(func=lambda m: True)
def calc(message):
    try:
        txt = message.text.replace(" ", "")
        crypto = requests.get(CRYPTO_API, params={
            "ids": "tron,tether",
            "vs_currencies": "usd"
        }, timeout=10).json()

        dollar = requests.get(DOLLAR_API, timeout=10).json()
        dollar_price = int(float(dollar["data"]["price_dollar_rl"]["p"]))

        if "دلار" in txt:
            amount = int(txt.replace("دلار", ""))
            toman = amount * dollar_price
            bot.send_message(
                message.chat.id,
                f"💵 {amount} دلار\n"
                f"💰 معادل: `{toman:,}` تومان",
                parse_mode="Markdown"
            )

        elif "ترون" in txt:
            amount = int(txt.replace("ترون", ""))
            usd = amount * crypto["tron"]["usd"]
            toman = int(usd * dollar_price)
            bot.send_message(
                message.chat.id,
                f"🪙 {amount} ترون\n"
                f"💲 {usd:.2f} دلار\n"
                f"💰 `{toman:,}` تومان",
                parse_mode="Markdown"
            )

    except:
        pass

print("🚀 ربات اجرا شد")
bot.infinity_polling()
