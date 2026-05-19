from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("টেস্ট মোড চালু\nছবি পাঠাও")

@dp.message(F.photo)
async def photo_received(message: types.Message):
    # খুব সিম্পল কীবোর্ড
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👆 Test 1", callback_data="test1")],
        [InlineKeyboardButton(text="👍 Test 2", callback_data="test2")]
    ])
    
    await message.answer("✅ ছবি পেয়েছি!\n\nনিচের বাটন চাপো", reply_markup=kb)

@dp.callback_query()
async def any_callback(callback: types.CallbackQuery):
    await callback.message.answer("✅ বাটন কাজ করছে! 🎉\nCallback Received!")
    await callback.answer("সফল", show_alert=True)

async def main():
    print("🚀 Ultra Simple Test Bot চালু...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
