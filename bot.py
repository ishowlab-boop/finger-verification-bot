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
    await message.answer("📸 ছবি পাঠাও যেটাতে ফিঙ্গার এডিট করতে চাও:")

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file.file_path}"
        
        user_data[message.from_user.id] = {
            "image_url": file_url,
            "username": message.from_user.first_name
        }
        
        # Finger Keyboard
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}") for emoji in FINGERS.keys()]
        kb.add(*buttons)
        
        await message.answer(
            "✅ ছবি পেয়েছি!\n\n"
            "এখন কোন ফিঙ্গার তুলে ধরতে চাও?\nসিলেক্ট করো:",
            reply_markup=kb
        )
        print(f"✅ Photo received from {message.from_user.id}")
        
    except Exception as e:
        await message.answer("❌ ছবি প্রসেস করতে সমস্যা হয়েছে। আবার পাঠাও।")
        print("Photo Error:", e)

@dp.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        return await callback.answer("আগে ছবি পাঠাও /start")

    emoji = callback.data.split("_")[1]
    finger_desc = FINGERS[emoji]
    data = user_data[uid]

    await callback.message.answer("🧠 AI এডিট হচ্ছে... একটু অপেক্ষা করো (২০-৪০ সেকেন্ড)")

    try:
        prompt = f"photorealistic, the person is clearly holding up their {finger_desc}, same person, same face, same clothes, natural light, sharp details"

        result = await client.run(
            "fal-ai/flux-pro/kontext",
            arguments={
                "image_url": data["image_url"],
                "prompt": prompt,
                "strength": 0.68,
                "num_images": 1
            }
        )

        edited_url = result["images"][0]["url"]

        await callback.message.answer_photo(
            edited_url,
            caption=f"✅ **AI Finger Verification Successful**\n\n"
                    f"Name   : {data['username']}\n"
                    f"Date   : {datetime.now().strftime('%d/%m/%Y')}\n"
                    f"Finger : {emoji}"
        )

    except Exception as e:
        await callback.message.answer(f"❌ AI Error: {str(e)[:150]}")
        print("AI Error:", e)

    await callback.answer()

async def main():
    print("🚀 AI Finger Bot চালু হয়েছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
