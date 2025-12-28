import requests
import telebot
from datetime import datetime

TOKEN = "8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ"
bot = telebot.TeleBot(TOKEN)

# لینک TGJU برای دلار و یورو
TGJU_URL = "https://www.tgju.org/"
# لینک CoinGecko برای کریپتو
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

def get_fiat_prices():
    try:
        res = requests.get(TGJU_URL, timeout=10)
        html = res.text
        import re
        dollar = re.search(r'data-title="دلار آمریکا".*?class="price">(.*?)<', html).group(1).strip()
        euro   = re.search(r'data-title="یورو".*?class="price">(.*?)<', html).group(1).strip()
        return {"دلار": dollar, "یورو": euro}
    except:
        return None

def get_crypto_prices():
    try:
        data = requests.get(COINGECKO_API, params={
            "ids": "bitcoin,ethereum,trong,usdt",
            "vs_currencies": "usd"
        }, timeout=10).json()
        return {
            "Bitcoin": data["bitcoin"]["usd"],
            "Ethereum": data["ethereum"]["usd"],
            "Tron": data["trong"]["usd"],
            "USDT": data["usdt"]["usd"]
        }
    except:
        return None

@bot.message_handler(commands=['price'])
def price(message):
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")
    fiat = get_fiat_prices()
    crypto = get_crypto_prices()
    if not fiat and not crypto:
        bot.send_message(message.chat.id, f"❌ خطا در دریافت قیمت‌ها! 🕒 {now}")
        return

    text = f"📊 قیمت روز ارزها و کریپتو\n\n"
    if fiat:
        for k,v in fiat.items():
            text += f"{k}: {v} تومان\n"
    if crypto:
        for k,v in crypto.items():
            text += f"{k}: ${v}\n"
    text += f"\n🕒 {now}"
    bot.send_message(message.chat.id, text)

bot.infinity_polling()
