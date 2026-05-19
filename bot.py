from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
from datetime import datetime
from PIL import Image, ImageDraw

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

user_data = {}

FINGER_EMOJIS = ["🫆","✋","👆","👇","👈","👉","👍","👎","👌","✌️","🤞","🤘","🖐️","✊","👊","👋","🫱","🫲","💪","🙌"]

@dp.message(Command("start"))
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("👋 স্বাগতম!\n\nতোমার **Full Name** লিখো:")

@dp.message()
async def collect_data(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data:
        return await message.answer("/start চাপো")

    data = user_data[uid]

    if "name" not in data:
        data["name"] = message.text
        await message.answer("পিতার নাম লিখো:")
    elif "father" not in data:
        data["father"] = message.text
        await message.answer("জন্ম তারিখ (DD/MM/YYYY):")
    elif "dob" not in data:
        data["dob"] = message.text
        await message.answer("ঠিকানা লিখো:")
    elif "address" not in data:
        data["address"] = message.text
        await send_finger_options(message)
    else:
        await message.answer("নতুন করতে /start চাপো")

async def send_finger_options(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=5)
    for e in FINGER_EMOJIS:
        kb.add(InlineKeyboardButton(text=e, callback_data=f"fp_{e}"))
    await message.answer("🖐️ ফিঙ্গারপ্রিন্ট ইমোজি সিলেক্ট করো:", reply_markup=kb)

@dp.callback_query(F.callback_data.startswith("fp_"))
async def make_paper(callback: types.CallbackQuery):
    try:
        uid = callback.from_user.id
        emoji = callback.data[3:]   # fp_ বাদ দিয়ে ইমোজি নেওয়া

        data = user_data.get(uid, {})

        # সিম্পল ইমেজ
        img = Image.new("RGB", (800, 950), "#f0f4f8")
        draw = ImageDraw.Draw(img)

        draw.rectangle((0, 0, 800, 100), fill="#1e3a8a")
        draw.text((150, 35), "FINGERPRINT VERIFICATION", fill="white", size=30)

        texts = [
            f"Name     : {data.get('name','N/A')}",
            f"Father   : {data.get('father','N/A')}",
            f"DOB      : {data.get('dob','N/A')}",
            f"Address  : {data.get('address','N/A')}",
            f"Date     : {datetime.now().strftime('%d/%m/%Y')}"
        ]

        y = 160
        for t in texts:
            draw.text((40, y), t, fill="black", size=22)
            y += 55

        # ফিঙ্গার বক্স
        draw.rectangle((280, 480, 520, 720), outline="#1e3a8a", width=12)
        draw.text((370, 560), emoji, size=130)

        draw.text((280, 780), "Signature / Stamp", fill="#555", size=20)

        # পাঠানো
        bio = io.BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)

        await callback.message.answer_photo(bio, caption="✅ তোমার Verification Paper রেডি!")
        await callback.answer("সফল!")

    except Exception as e:
        await callback.answer("❌ এরর হয়েছে। আবার চেষ্টা করো")
        print("Error:", e)

async def main():
    print("Bot Starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
