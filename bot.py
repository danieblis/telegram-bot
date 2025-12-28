import telebot
import requests
from datetime import datetime

TOKEN = "8505732689:AAGyWtz_HqJLCa7qwNJPTe6uI4qMzOKLTdQ"
bot = telebot.TeleBot(TOKEN)

CRYPTO_API = "https://api.coingecko.com/api/v3/simple/price"

# دریافت قیمت دلار (تومان)
def get_dollar_price():
    try:
        r = requests.get("https://api.tgju.org/v1/market/price_dollar_rl", timeout=10).json()
        return int(r["data"]["price"])
    except:
        return None

# دریافت قیمت ارزها
def get_crypto_prices():
    return requests.get(
        CRYPTO_API,
        params={
            "ids": "tron,tether,bitcoin,ethereum",
            "vs_currencies": "usd"
        },
        timeout=10
    ).json()

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "💱 *ربات محاسبه قیمت ارز*\n\n"
        "✍️ مثال:\n"
        "• `50 دلار`\n"
        "• `500 ترون`\n"
        "• `100 تتر`\n"
        "• `2 بیت کوین`\n\n"
        "📌 قابل استفاده در گروه و کانال",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def calc(msg):
    text = msg.text.replace(" ", "")
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")

    dollar = get_dollar_price()
    crypto = get_crypto_prices()

    if dollar is None:
        bot.send_message(msg.chat.id, "❌ خطا در دریافت قیمت دلار")
        return

    try:
        if "دلار" in text:
            amount = float(text.replace("دلار", ""))
            toman = int(amount * dollar)
            bot.send_message(
                msg.chat.id,
                f"💵 {amount} دلار\n"
                f"💰 `{toman:,}` تومان\n\n"
                f"🕒 {now}",
                parse_mode="Markdown"
            )

        elif "ترون" in text:
            amount = float(text.replace("ترون", ""))
            usd = amount * crypto["tron"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"🔴 {amount} ترون\n"
                f"💲 {usd:.2f} دلار\n"
                f"💰 `{toman:,}` تومان\n\n"
                f"🕒 {now}",
                parse_mode="Markdown"
            )

        elif "تتر" in text:
            amount = float(text.replace("تتر", ""))
            usd = amount
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"🟢 {amount} تتر\n"
                f"💲 {usd:.2f} دلار\n"
                f"💰 `{toman:,}` تومان\n\n"
                f"🕒 {now}",
                parse_mode="Markdown"
            )

        elif "بیتکوین" in text or "بیتکوین" in text:
            amount = float(text.replace("بیتکوین", "").replace("بیت‌کوین", ""))
            usd = amount * crypto["bitcoin"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"₿ {amount} بیت‌کوین\n"
                f"💲 {usd:.2f} دلار\n"
                f"💰 `{toman:,}` تومان\n\n"
                f"🕒 {now}",
                parse_mode="Markdown"
            )

        elif "اتریوم" in text:
            amount = float(text.replace("اتریوم", ""))
            usd = amount * crypto["ethereum"]["usd"]
            toman = int(usd * dollar)
            bot.send_message(
                msg.chat.id,
                f"🔷 {amount} اتریوم\n"
                f"💲 {usd:.2f} دلار\n"
                f"💰 `{toman:,}` تومان\n\n"
                f"🕒 {now}",
                parse_mode="Markdown"
            )

        else:
            bot.send_message(
                msg.chat.id,
                "❌ ارز پشتیبانی نمی‌شود\n\n"
                "✍️ مثال صحیح:\n"
                "`50 دلار`\n"
                "`500 ترون`",
                parse_mode="Markdown"
            )

    except:
        bot.send_message(msg.chat.id, "❌ فرمت پیام اشتباه است")

print("🚀 ربات اجرا شد")
bot.infinity_polling()
