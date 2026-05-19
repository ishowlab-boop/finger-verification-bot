from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
from datetime import datetime

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

user_data = {}

FINGERS = ["👆", "🫆", "✌️", "👍", "👌", "🤘", "🖐️"]

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 ছবি পাঠাও:")

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file.file_path}"

        user_data[message.from_user.id] = {"image_url": file_url}

        buttons = [[InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}")] for emoji in FINGERS]
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("✅ ছবি পেয়েছি!\n\nকোন ফিঙ্গার চাও?", reply_markup=kb)
    except:
        await message.answer("❌ Error")

@dp.callback_query(F.callback_data.startswith("finger_"))
async def callback_test(callback: types.CallbackQuery):
    emoji = callback.data.split("_")[1]
    await callback.message.answer(f"✅ তুমি {emoji} সিলেক্ট করেছো!")
    await callback.answer("Done!")

async def main():
    print("Bot Running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
