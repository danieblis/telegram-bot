from telethon import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest
import asyncio
from datetime import datetime

# ===== اطلاعات اکانت =====
api_id = 1234567        # api_id خودت
api_hash = "API_HASH_HERE"

# متن پایه اسم
BASE_NAME = "a Q a P e J a K"

client = TelegramClient("session_name", api_id, api_hash)

async def change_name():
    while True:
        now = datetime.now()
        time_str = now.strftime("%H:%M")

        new_name = f"{BASE_NAME} {time_str}"

        await client(UpdateProfileRequest(
            first_name=new_name
        ))

        print("نام تغییر کرد →", new_name)

        await asyncio.sleep(60)  # هر 1 دقیقه

async def main():
    await client.start()
    print("ربات تغییر نام فعال شد")
    await change_name()

client.loop.run_until_complete(main())
