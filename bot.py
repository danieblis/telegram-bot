import requests
import telebot
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========= تنظیمات =========
BOT_TOKEN = "7778912181:AAGY_XOuv8U2eHsnVzYgTyLKAtsdO8wv62k"
CHANNEL = "@aQa_pejak_jenel1"
OWNER_ID = 123456789
VIP_USERS = [OWNER_ID]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MarkdownV2")
user_last_hashes = {}
HASH_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")

# ======= تابع escape =======
def escape_md(text: str) -> str:
    if not text: return ""
    chars = r"\_*[]()~`>#+-=|{}.!"
    for c in chars:
        text = text.replace(c, f"\\{c}")
    return text

# ======= توابع اصلی =======
def extract_hash(text):
    m = HASH_RE.search(text)
    return m.group(0) if m else None

def check_trx(tx_hash):
    url = f"https://apilist.tronscan.org/api/transaction-info?hash={tx_hash}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return None
        data = r.json()
        if "contractData" not in data: return None
        sender = data.get("ownerAddress","نامشخص")
        receiver = data.get("toAddress","نامشخص")
        amount = data.get("contractData",{}).get("amount",0)/1_000_000
        token = data.get("tokenInfo",{}).get("tokenAbbr","TRX")
        confirmed = data.get("confirmed",False)
        return {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token,
            "status": "✅ تایید شده" if confirmed else "⏳ در انتظار تایید"
        }
    except:
        return "NETWORK_ERROR"

def check_balance(address):
    if not address.startswith("T") or len(address)<25: return None
    url = f"https://apilist.tronscan.org/api/account?address={address}"
    try:
        r = requests.get(url,timeout=10)
        if r.status_code != 200: return None
        data = r.json()
        balance = data.get("balance",0)/1_000_000
        tokens = data.get("assetV2",[])
        return {"balance": balance, "tokens": tokens}
    except:
        return None

# ========= START =========
@bot.message_handler(commands=['start'])
def send_start(message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🔍 بررسی تراکنش", callback_data="check_tx"),
        InlineKeyboardButton("👛 بررسی موجودی", callback_data="check_balance")
    )
    kb.add(
        InlineKeyboardButton("⭐ VIP", callback_data="vip_info"),
        InlineKeyboardButton("📢 کانال", url=f"https://t.me/{CHANNEL[1:]}")
    )
    name = escape_md(message.from_user.first_name)
    text = (
        f"👋 سلام *{name}*\\!\n\n"
        "💎 من ربات هش چکر TRON هستم\\.\n"
        "🎯 قابلیت‌ها:\n"
        "- بررسی تراکنش‌ها با گرافیک VIP\n"
        "- بررسی موجودی TRX و توکن‌ها\n"
        "- نسخه VIP و قابلیت‌های فوق‌العاده"
    )
    bot.send_message(message.chat.id, text, reply_markup=kb)

# ========= CALLBACK =========
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(query):
    uid = query.from_user.id
    if query.data=="check_tx":
        bot.send_message(query.message.chat.id,"⏳ لطفاً هش تراکنش TRX 64 کاراکتری را ارسال کنید...")
    elif query.data=="check_balance":
        bot.send_message(query.message.chat.id,"⏳ لطفاً آدرس TRON خود را ارسال کنید...")
    elif query.data=="vip_info":
        if uid in VIP_USERS:
            vip_text = (
                "⭐ شما VIP هستید!\n\n"
                "💥 قابلیت‌های VIP:\n"
                "- مشاهده آخرین 50 تراکنش خود\n"
                "- تراکنش‌های بزرگ با علامت VIP ALERT\n"
                "- بررسی چند آدرس همزمان\n"
                "- فیلتر تراکنش‌ها بر اساس مقدار دلخواه\n"
                "- گزارش کامل توکن‌ها"
            )
            bot.send_message(query.message.chat.id, vip_text)
        else:
            bot.send_message(query.message.chat.id,"❌ شما VIP نیستید. برای دریافت نسخه VIP با صاحب ربات تماس بگیرید.")

# ========= HANDLE MESSAGE =========
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    uid = message.from_user.id
    text = message.text.strip()

    # بررسی هش
    tx_hash = extract_hash(text)
    if tx_hash:
        bot.send_message(message.chat.id,"⏳ در حال بررسی تراکنش...")
        res = check_trx(tx_hash)
        if res=="NETWORK_ERROR":
            bot.send_message(message.chat.id,"❌ خطای اتصال به سرور TRON")
            return
        if not res:
            bot.send_message(message.chat.id,"❌ تراکنشی با این هش پیدا نشد")
            return
        tx_link = f"https://tronscan.org/#/transaction/{tx_hash}"
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("نمایش در Tronscan",url=tx_link),
            InlineKeyboardButton("کانال ما",url=f"https://t.me/{CHANNEL[1:]}")
        )
        big_tx = ""
        if res["amount"]>=500:
            big_tx = "💥 تراکنش بزرگ!"
            if uid in VIP_USERS: big_tx += " 👑 VIP ALERT!"
        msg = (
            f"💎 *اطلاعات تراکنش TRON*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 *Hash:*\n`{escape_md(tx_hash)}`\n\n"
            f"👤 *From:*\n`{escape_md(res['sender'])}`\n\n"
            f"🎯 *To:*\n`{escape_md(res['receiver'])}`\n\n"
            f"💰 *Amount:* `{res['amount']} {escape_md(res['token'])}` {big_tx}\n"
            f"📌 *Status:* {res['status']}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📢 {CHANNEL}"
        )
        bot.send_message(message.chat.id,msg,reply_markup=kb,disable_web_page_preview=True)
        user_last_hashes.setdefault(uid,[]).append(tx_hash)
        if uid in VIP_USERS:
            if len(user_last_hashes[uid])>50: user_last_hashes[uid].pop(0)
        else:
            if len(user_last_hashes[uid])>10: user_last_hashes[uid].pop(0)
        return

    # بررسی موجودی چند آدرس برای VIP
    addresses = text.split() if uid in VIP_USERS else [text]
    final_msg = ""
    for addr in addresses:
        res = check_balance(addr)
        if not res:
            final_msg += f"❌ آدرس {addr} معتبر نیست یا مشکل اتصال\n"
            continue
        balance = res["balance"]
        tokens = res["tokens"]
        msg = f"👛 *موجودی آدرس TRON*\n━━━━━━━━━━━━━━━\n📍 آدرس: `{escape_md(addr)}`\n💰 TRX: `{balance}`\n"
        if tokens:
            msg += "📦 توکن‌ها:\n"
            total = sum(t.get('balance',0) for t in tokens)
            for t in tokens:
                pct = t.get('balance',0)/total*100 if total>0 else 0
                msg += f"- {escape_md(t.get('name','?'))}: `{t.get('balance',0)}` ({pct:.2f}%)\n"
        msg += "━━━━━━━━━━━━━━━\n"
        final_msg += msg
    final_msg += f"📢 {CHANNEL}"
    bot.send_message(message.chat.id,final_msg,disable_web_page_preview=True)

# ========= /last =========
@bot.message_handler(commands=['last'])
def show_last(message):
    uid = message.chat.id
    txs = user_last_hashes.get(uid,[])
    if not txs:
        bot.send_message(uid,"❌ هیچ هش فرستاده نشده.")
        return
    limit = 50 if uid in VIP_USERS else 10
    text = "📝 آخرین هش‌های شما:\n\n"
    for tx in txs[-limit:]:
        text += f"`{escape_md(tx)}`\n"
    bot.send_message(uid,text)

# ========= اجرا =========
print("🤖 VIP God Bot (بدون matplotlib) در حال اجراست...")
bot.infinity_polling(skip_pending=True)
