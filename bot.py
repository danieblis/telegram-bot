import requests
import telebot
from datetime import datetime

TOKEN = "8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ"
bot = telebot.TeleBot(TOKEN)

# نگاشت فارسی → شناسه CoinGecko
coins_map = {
    "ترون": "tron",
    "بیت‌کوین": "bitcoin",
    "اتریوم": "ethereum",
    "تتر": "tether",
    "دلار": "usd",
    "یورو": "eur"
}

def get_price(coin_id):
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd"},
            timeout=10
        ).json()
        return res[coin_id]["usd"]
    except:
        return None

@bot.message_handler(commands=['price'])
def price(message):
    text = message.text.replace("/price", "").strip()  # ورودی کاربر
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")

    if text not in coins_map:
        bot.send_message(message.chat.id, f"❌ ارز پشتیبانی نمی‌شود. 🕒 {now}")
        return

    coin_id = coins_map[text]
    value = get_price(coin_id)
    if value is None:
        bot.send_message(message.chat.id, f"❌ خطا در دریافت قیمت! 🕒 {now}")
        return

    if text in ["دلار", "یورو"]:
        bot.send_message(message.chat.id, f"💵 قیمت {text}: {value} تومان\n🕒 {now}")
    else:
        bot.send_message(message.chat.id, f"💰 قیمت {text}: ${value}\n🕒 {now}")

bot.infinity_polling()
