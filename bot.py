import telebot
import requests
from datetime import datetime

TOKEN = "توکن_ربات_تو"
bot = telebot.TeleBot(TOKEN)

# API قیمت ارز دیجیتال
COIN_API = "https://api.coingecko.com/api/v3/simple/price"
# API قیمت دلار آزاد از floatrates (بدون نیاز به API Key)
DOLLAR_API = "http://www.floatrates.com/daily/usd.json"

def get_dollar_rate():
    try:
        resp = requests.get(DOLLAR_API, timeout=10).json()
        # floatrates نرخ USD به IRR را در کلید "irr" می‌دهد
        if "irr" in resp:
            return float(resp["irr"]["rate"])
        # اگر نبود مقدار دیگری برگشت
        return None
    except:
        return None

def get_crypto_prices():
    try:
        params = {"ids":"bitcoin,ethereum,tron,tether","vs_currencies":"usd"}
        return requests.get(COIN_API, params=params, timeout=10).json()
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "سلام! 👋\nقیمت لحظه‌ای ارز و دلار رو حساب می‌کنم.\nمثال:\n500 TRX\n50 USD",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def convert(message):
    text = message.text.strip().upper()
    parts = text.split()

    prices = get_crypto_prices()
    dollar_rate = get_dollar_rate()  # دلار لحظه‌ای

    if not prices or not dollar_rate:
        bot.send_message(message.chat.id, "❌ خطا در دریافت قیمت‌ها. دوباره امتحان کن.")
        return

    try:
        amount, coin = parts
        amount = float(amount)
        coin = coin.upper()

        result = ""
        usd = 0

        if coin == "TRX":
            usd = amount * prices["tron"]["usd"]
            result = (
                f"₮ {amount:,.0f} ترون ≈ 💵 {usd:.2f} دلار\n"
                f"🏦 ≈ {usd * dollar_rate:,.0f} تومان\n"
                f"📈 قیمت دلار (روز): {dollar_rate:,.0f} تومان"
            )

        elif coin == "BTC":
            usd = amount * prices["bitcoin"]["usd"]
            result = (
                f"₿ {amount:.6f} بیت‌کوین ≈ 💵 {usd:.2f} دلار\n"
                f"🏦 ≈ {usd * dollar_rate:,.0f} تومان\n"
                f"📈 قیمت دلار (روز): {dollar_rate:,.0f} تومان"
            )

        elif coin == "ETH":
            usd = amount * prices["ethereum"]["usd"]
            result = (
                f"🔷 {amount:.6f} اتریوم ≈ 💵 {usd:.2f} دلار\n"
                f"🏦 ≈ {usd * dollar_rate:,.0f} تومان\n"
                f"📈 قیمت دلار (روز): {dollar_rate:,.0f} تومان"
            )

        elif coin == "USDT":
            usd = amount * prices["tether"]["usd"]
            result = (
                f"💵 {amount:.2f} تتر ≈ 💵 {usd:.2f} دلار\n"
                f"🏦 ≈ {usd * dollar_rate:,.0f} تومان\n"
                f"📈 قیمت دلار (روز): {dollar_rate:,.0f} تومان"
            )

        elif coin == "USD":
            result = (
                f"💵 {amount:.2f} دلار ≈ 🏦 {amount * dollar_rate:,.0f} تومان\n"
                f"📈 قیمت دلار (روز): {dollar_rate:,.0f} تومان"
            )

        else:
            result = "❌ ارز پشتیبانی نمی‌شود."

        now = datetime.now().strftime("%Y/%m/%d - %H:%M")
        result += f"\n🕒 زمان محاسبه: {now}"

        bot.send_message(message.chat.id, result)
    except:
        bot.send_message(message.chat.id, "❌ فرمت اشتباه. مثل: 500 TRX")

bot.infinity_polling()
