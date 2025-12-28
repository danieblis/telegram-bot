import telebot
import requests
from datetime import datetime

TOKEN = "8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ"  # حتما توکن واقعی بذار
bot = telebot.TeleBot(TOKEN)

CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price"

# دریافت قیمت دلار از CoinGecko (جایگزین API مشکل‌دار)
def get_dollar_price():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "usd", "vs_currencies": "irr"},
            timeout=10
        ).json()
        return int(r["usd"]["irr"])
    except:
        return None

# دریافت قیمت ارزهای دیجیتال
def get_crypto_prices():
    try:
        r = requests.get(
            CRYPTO_API,
            params={
                "ids": "tron,tether,bitcoin,ethereum",
                "vs_currencies": "usd"
            },
            timeout=10
        ).json()
        return r
    except:
        return {}

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "💱 *ربات محاسبه قیمت ارز*\n\n"
        "✍️ مثال:\n"
        "• `50 دلار`\n"
        "• `500 ترون`\n"
        "• `100 تتر`\n"
        "• `2 بیت‌کوین`\n"
        "• `1 اتریوم`\n\n"
        "📌 قابل استفاده در گروه و کانال",
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
        # دلار
        if "دلار" in text:
            amount = float(text.replace("دلار", ""))
            toman = int(amount * dollar)
            bot.send_message(
                msg.chat.id,
                f"💵 {amount} دلار\n"
                f"💰 `{toman:,}` تومان\n🕒 {now}",
                parse_mode="Markdown"
            )
        # ترون
        elif "ترون" in text:
            amount = float(text.replace("ترون", ""))
            usd = amount * crypto["tron"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"🔴 {amount} ترون\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}",
                parse_mode="Markdown"
            )
        # تتر
        elif "تتر" in text:
            amount = float(text.replace("تتر", ""))
            usd = amount
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"🟢 {amount} تتر\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}",
                parse_mode="Markdown"
            )
        # بیت‌کوین
        elif "بیتکوین" in text or "بیت‌کوین" in text:
            amount = float(text.replace("بیتکوین", "").replace("بیت‌کوین", ""))
            usd = amount * crypto["bitcoin"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"₿ {amount} بیت‌کوین\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}",
                parse_mode="Markdown"
            )
        # اتریوم
        elif "اتریوم" in text:
            amount = float(text.replace("اتریوم", ""))
            usd = amount * crypto["ethereum"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"🔷 {amount} اتریوم\n💲 {usd:.2f} دلار\n💰 `{toman:,}` تومان\n🕒 {now}",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                msg.chat.id,
                "❌ ارز پشتیبانی نمی‌شود\n✍️ مثال صحیح:\n`50 دلار`\n`500 ترون`",
                parse_mode="Markdown"
            )
    except:
        bot.send_message(msg.chat.id, "❌ فرمت پیام اشتباه است")

print("🚀 ربات اجرا شد")
bot.infinity_polling()
