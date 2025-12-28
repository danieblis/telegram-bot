import requests
import telebot
from datetime import datetime

TOKEN = "8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ"
bot = telebot.TeleBot(TOKEN)

# نگاشت فارسی به شناسه CoinGecko
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
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        res = requests.get(url, params=params, timeout=20)  # Timeout بالاتر
        res.raise_for_status()
        data = res.json()
        return data[coin_id]["usd"]
    except:
        return None

@bot.message_handler(commands=['price'])
def price(message):
    user_input = message.text.replace("/price", "").strip()
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")

    if user_input not in coins_map:
        bot.send_message(message.chat.id, f"❌ ارز پشتیبانی نمی‌شود. 🕒 {now}")
        return

    coin_id = coins_map[user_input]
    value = get_price(coin_id)
    if value is None:
        bot.send_message(message.chat.id, f"❌ خطا در دریافت قیمت! 🕒 {now}")
        return

    if user_input in ["دلار", "یورو"]:
        bot.send_message(message.chat.id, f"💵 قیمت {user_input}: {value} تومان\n🕒 {now}")
    else:
        bot.send_message(message.chat.id, f"💰 قیمت {user_input}: ${value}\n🕒 {now}")

bot.infinity_polling()
