from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 ছবি পাঠাও টেস্ট করার জন্য")

@dp.message(F.photo)
async def get_photo(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👆", callback_data="finger_1")],
        [InlineKeyboardButton(text="👍", callback_data="finger_2")],
        [InlineKeyboardButton(text="🖐️", callback_data="finger_3")]
    ])
    
    await message.answer("✅ ছবি পেয়েছি!\n\nএকটা ফিঙ্গার চাপো 👇", reply_markup=kb)

@dp.callback_query(F.callback_data.startswith("finger_"))
async def button_click(callback: types.CallbackQuery):
    await callback.message.answer("✅ বাটন কাজ করছে! 🎉\nতুমি ক্লিক করেছো।")
    await callback.answer("সফল!", show_alert=True)

async def main():
    print("Bot চালু আছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
