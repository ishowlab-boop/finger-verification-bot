from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
from datetime import datetime
import fal_client

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router = Router()

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

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 এডিট করার জন্য একটা ছবি পাঠাও:")

@router.message(F.photo)
async def receive_photo(message: types.Message):
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file.file_path}"

        user_data[message.from_user.id] = {"image_url": file_url, "username": message.from_user.first_name}

        buttons = [[InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}")] for emoji in FINGERS.keys()]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("✅ ছবি পেয়েছি!\n\nকোন ফিঙ্গার চাও?", reply_markup=kb)

    except Exception as e:
        await message.answer("❌ ছবি প্রসেস করতে সমস্যা হয়েছে। আবার পাঠাও।")

@router.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data:
        return await callback.answer("আগে ছবি পাঠাও!", show_alert=True)

    emoji = callback.data.split("_")[1]
    finger_desc = FINGERS[emoji]
    data = user_data[uid]

    await callback.message.answer("🧠 AI এডিট হচ্ছে... অপেক্ষা করো (২০-৪০ সেকেন্ড)")

    try:
        prompt = f"photorealistic edit, the person is clearly holding their {finger_desc} towards camera, same person, same face, same clothes"

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
            caption=f"✅ সফল হয়েছে!\nFinger: {emoji}\nDate: {datetime.now().strftime('%d/%m/%Y')}"
        )
    except Exception as e:
        await callback.message.answer(f"❌ AI Error: {str(e)[:150]}")

    await callback.answer()

dp.include_router(router)

async def main():
    print("🚀 Bot Started - Waiting for photo...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
