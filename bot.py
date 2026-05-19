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
    "👆": "right index finger",
    "🫆": "index finger",
    "✌️": "peace sign",
    "👍": "thumb up",
    "👌": "OK sign",
    "🤘": "rock on",
    "🖐️": "open hand",
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 এডিট করার জন্য একটা ছবি পাঠাও:")

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

        # Correct Inline Keyboard
        keyboard_buttons = [[InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}")] for emoji in FINGERS]
        kb = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        await message.answer(
            "✅ ছবি পেয়েছি!\n\nকোন ফিঙ্গার তুলে ধরতে চাও?",
            reply_markup=kb
        )
    except Exception as e:
        await message.answer("❌ ছবি প্রসেস করতে সমস্যা হয়েছে। আবার পাঠাও।")

# ✅ Callback Handler
@dp.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        return await callback.answer("আগে ছবি পাঠাও /start", show_alert=True)

    emoji = callback.data.split("_")[1]
    finger_desc = FINGERS[emoji]
    data = user_data[uid]

    await callback.message.answer("🧠 AI এডিট হচ্ছে... ১৫-৪০ সেকেন্ড লাগবে")

    try:
        prompt = f"photorealistic, the person is clearly holding up their {finger_desc}, same face, same body, same clothes, natural lighting, sharp"

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
            caption=f"✅ **সফল হয়েছে!**\n\n"
                    f"Name : {data['username']}\n"
                    f"Finger : {emoji}\n"
                    f"Date : {datetime.now().strftime('%d/%m/%Y')}"
        )
    except Exception as e:
        await callback.message.answer(f"❌ এরর হয়েছে:\n{str(e)[:200]}")

    await callback.answer("✅ Done!")

async def main():
    print("🚀 Bot Running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
