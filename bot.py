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
    "🤘": "rock on / devil horns sign",
    "🖐️": "open palm showing all five fingers",
    "👇": "middle finger pointing down",
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "📸 **AI Finger Verification Bot**\n\n"
        "প্রথমে যে ছবিটা এডিট করতে চাও সেটা পাঠাও (photo হিসেবে):"
    )

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file.file_path}"
    
    user_data[message.from_user.id] = {
        "image_url": file_url,
        "username": message.from_user.first_name
    }
    
    # Finger selection
    kb = InlineKeyboardMarkup(row_width=3)
    for emoji, desc in FINGERS.items():
        kb.add(InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}"))
    
    await message.answer(
        "✅ ছবি পেয়েছি!\n\n"
        "এখন কোন ফিঙ্গার তুলে ধরতে চাও? সিলেক্ট করো:",
        reply_markup=kb
    )

@dp.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        return await callback.answer("ছবি আগে পাঠাও")

    emoji = callback.data.split("_")[1]
    finger_desc = FINGERS[emoji]
    data = user_data[uid]

    await callback.message.answer("🧠 AI এডিট করা হচ্ছে... ১৫-৪০ সেকেন্ড লাগবে")

    try:
        prompt = f"photorealistic edit, the person in the photo is clearly holding up their {finger_desc}, same person, same face, same clothes, natural lighting, high detail, sharp focus"

        result = await client.run(
            "fal-ai/flux-pro/kontext",
            arguments={
                "image_url": data["image_url"],
                "prompt": prompt,
                "strength": 0.70,
                "num_images": 1
            }
        )

        edited_url = result["images"][0]["url"]

        await callback.message.answer_photo(
            edited_url,
            caption=f"✅ **AI Finger Verification Done!**\n\n"
                    f"User     : {data['username']}\n"
                    f"Date     : {datetime.now().strftime('%d/%m/%Y %I:%M %p')}\n"
                    f"Finger   : {emoji}"
        )

    except Exception as e:
        await callback.message.answer(f"❌ এরর হয়েছে:\n{str(e)[:200]}\n\nআবার ছবি পাঠিয়ে চেষ্টা করো")

    await callback.answer()

async def main():
    print("✅ Dynamic AI Finger Verification Bot চালু আছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
