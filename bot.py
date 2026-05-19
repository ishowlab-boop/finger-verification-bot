from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
from datetime import datetime
import fal_client

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

client = fal_client.AsyncClient(key=os.getenv("FAL_KEY"))

user_data = {}

FINGERS = {
    "👆": "right index finger raised clearly towards the camera",
    "🫆": "index finger prominently visible",
    "✌️": "peace sign with two fingers",
    "👍": "thumb up gesture",
    "👌": "OK hand sign",
    "🤘": "rock on sign",
    "🖐️": "open palm with all fingers",
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 যে ছবিটা এডিট করতে চাও সেটা পাঠাও:")

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    try:
        # BOT_TOKEN চেক
        token = os.getenv("BOT_TOKEN")
        if not token:
            return await message.answer("❌ BOT_TOKEN সেট করা নেই। Railway এ চেক করো।")

        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        
        file_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"
        
        user_data[message.from_user.id] = {
            "image_url": file_url,
            "username": message.from_user.first_name
        }
        
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(text=emo, callback_data=f"finger_{emo}") for emo in FINGERS.keys()]
        kb.add(*buttons)
        
        await message.answer(
            "✅ ছবি সফলভাবে পেয়েছি!\n\n"
            "এখন কোন ফিঙ্গার তুলে ধরতে চাও? সিলেক্ট করো 👇",
            reply_markup=kb
        )
        
    except Exception as e:
        print("Photo Processing Error:", str(e))  # Railway Log এ দেখা যাবে
        await message.answer("❌ ছবি প্রসেস করতে সমস্যা হয়েছে।\n\nআবার নতুন করে ছবি পাঠাও।")

@dp.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        return await callback.answer("আগে ছবি পাঠাও")

    emoji = callback.data.split("_")[1]
    finger_desc = FINGERS[emoji]
    data = user_data[uid]

    await callback.message.answer("🧠 AI এডিট হচ্ছে... (২০-৪০ সেকেন্ড লাগবে)")

    try:
        prompt = f"photorealistic edit, the person is clearly holding up their {finger_desc}, same person, same face, same clothes, natural lighting, sharp focus"

        result = await client.run(
            "fal-ai/flux-pro/kontext",
            arguments={
                "image_url": data["image_url"],
                "prompt": prompt,
                "strength": 0.65,
                "num_images": 1
            }
        )

        edited_url = result["images"][0]["url"]

        await callback.message.answer_photo(
            edited_url,
            caption=f"✅ **AI Finger Verification Done**\n\n"
                    f"Name : {data['username']}\n"
                    f"Date : {datetime.now().strftime('%d/%m/%Y')}\n"
                    f"Finger : {emoji}"
        )
    except Exception as e:
        await callback.message.answer(f"❌ AI এডিটে সমস্যা: {str(e)[:100]}")
        print("AI Error:", str(e))

    await callback.answer()

async def main():
    print("🚀 Bot Started Successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
