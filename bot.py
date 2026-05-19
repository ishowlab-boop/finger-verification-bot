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
    "👆": "right index finger", "🫆": "index finger", "✌️": "peace sign",
    "👍": "thumb up", "👌": "OK sign", "🤘": "rock on", "🖐️": "open hand"
}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 এডিট করার জন্য একটা ছবি পাঠাও:")

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    try:
        token = os.getenv("BOT_TOKEN")
        print(f"DEBUG: Token exists = {bool(token)} | Length = {len(token) if token else 0}")
        
        if not token or len(token) < 30:
            return await message.answer("❌ BOT_TOKEN সঠিকভাবে সেট করা নেই। Railway Variables চেক করো।")

        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{token}/{file.file_path}"

        user_data[message.from_user.id] = {"image_url": file_url, "username": message.from_user.first_name}

        kb = InlineKeyboardMarkup(row_width=3)
        kb.add(*[InlineKeyboardButton(text=emo, callback_data=f"finger_{emo}") for emo in FINGERS.keys()])

        await message.answer("✅ ছবি পেয়েছি!\n\nকোন ফিঙ্গার চাও?", reply_markup=kb)

    except Exception as e:
        print("FULL ERROR:", str(e))
        await message.answer(f"❌ Error: {str(e)[:100]}\n\nআবার ছবি পাঠাও")

@dp.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    # ... (আগের কোডের মতো রাখো, চাইলে বলো আবার দিবো)

    await callback.answer("AI Processing...")

async def main():
    print("Bot Started | Token Check:", bool(os.getenv("BOT_TOKEN")))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
