import requests
import telebot
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========= تنظیمات =========
BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "@aQa_pejak_jenel1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
HASH_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")

# ========= توابع =========
def extract_hash(text):
    m = HASH_RE.search(text)
    return m.group(0) if m else None

def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

def check_trx(tx_hash):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        if "contractData" not in data:
            return None
        return {
            "from": data.get("ownerAddress", "نامشخص"),
            "to": data.get("toAddress", "نامشخص"),
            "amount": data.get("contractData", {}).get("amount", 0) / 1_000_000,
            "status": "✅ تایید شده" if data.get("confirmed") else "⏳ در انتظار تایید"
        }
    except:
        return None

def check_balance(address):
    if not address.startswith("T"):
        return None
    url = f"https://apilist.tronscan.org/api/account?address={address}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        balance = data.get("balance", 0) / 1_000_000
        tokens = data.get("assetV2", [])
        return {"balance": balance, "tokens": tokens}
    except:
        return None

# ========= استارت =========
@bot.message_handler(commands=['start'])
def send_start(message):
    user_id = message.from_user.id

    if not is_joined(user_id):
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/aQa_pejak_jenel1"),
            InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")
        )

        bot.send_message(
            message.chat.id,
            "🔒 *دسترسی محدود*\n\n"
            "برای استفاده از ربات باید\n"
            "در کانال رسمی 𝐏𝐄𝐉𝐀𝐊 عضو شوید 👇",
            reply_markup=kb
        )
        return

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔍 بررسی هش", callback_data="check_tx"),
        InlineKeyboardButton("💰 بررسی موجودی", callback_data="check_balance"),
        InlineKeyboardButton("📢 کانال رسمی", url="https://t.me/aQa_pejak_jenel1")
    )

    text = (
        "╔════════════════╗\n"
        "🔥 *ربات هش چکر* 🔥\n"
        "       *a Q a  P e J a K*\n"
        "╚════════════════╝\n\n"
        "✨ *امکانات فوق حرفه‌ای:*\n"
        "• بررسی انواع هش‌ها (TRX ، ETH ، TON و ...)\n"
        "• بررسی موجودی کامل کیف پول‌ها\n"
        "• نمایش وضعیت تراکنش‌ها با جزئیات\n\n"
        "⚡️ *سریع | دقیق | همه‌جانبه*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

    bot.send_message(message.chat.id, text, reply_markup=kb)

# ========= تایید جوین =========
@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join_callback(call):
    if is_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ عضویت تایید شد")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        send_start(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو کانال نیستی", show_alert=True)

# ========= دکمه‌ها =========
@bot.callback_query_handler(func=lambda c: c.data in ["check_tx", "check_balance"])
def buttons(call):
    if call.data == "check_tx":
        bot.send_message(call.message.chat.id, "🔍 لطفاً هش 64 کاراکتری یا هر هش دیگر را ارسال کنید")
    elif call.data == "check_balance":
        bot.send_message(call.message.chat.id, "💰 لطفاً آدرس کیف پول خود را ارسال کنید")

# ========= پیام‌ها =========
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if not is_joined(message.from_user.id):
        send_start(message)
        return

    text = message.text.strip()

    # بررسی هش
    tx_hash = extract_hash(text)
    if tx_hash:
        bot.send_message(message.chat.id, "⏳ در حال بررسی هش...")
        res = check_trx(tx_hash)
        if not res:
            bot.send_message(message.chat.id, "❌ هش نامعتبر یا پیدا نشد")
            return

        bot.send_message(
            message.chat.id,
            f"💎 *نتیجه بررسی هش*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔹 Hash:\n`{tx_hash}`\n\n"
            f"👤 From:\n`{res['from']}`\n\n"
            f"🎯 To:\n`{res['to']}`\n\n"
            f"💰 Amount: `{res['amount']}`\n"
            f"📌 Status: {res['status']}\n"
            f"━━━━━━━━━━━━━━━"
        )
        return

    # بررسی موجودی همه توکن‌ها
    if text.startswith("T"):
        bot.send_message(message.chat.id, "⏳ در حال بررسی موجودی...")
        res = check_balance(text)
        if not res:
            bot.send_message(message.chat.id, "❌ آدرس نامعتبر یا مشکلی در اتصال پیش آمد")
            return

        balance = res["balance"]
        tokens = res["tokens"]

        msg = f"💰 *موجودی کیف پول*\n━━━━━━━━━━━━━━━\n📍 `{text}`\n"
        msg += f"💰 TRX: `{balance}`\n"

        if tokens:
            msg += "📦 *کل توکن های حساب:*\n"
            for t in tokens:
                msg += f"- {t.get('name','?')} : `{t.get('balance',0)}`\n"

        msg += "━━━━━━━━━━━━━━━"
        bot.send_message(message.chat.id, msg)

# ========= اجرا =========
print("🤖 BOT ONLINE")
bot.infinity_polling(skip_pending=True)
