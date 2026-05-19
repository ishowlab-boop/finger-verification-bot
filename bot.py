from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👆 Test Button", callback_data="test_click")]
    ])
    await message.answer("টেস্ট বাটন 👇", reply_markup=kb)

@dp.callback_query(F.callback_data == "test_click")
async def test_callback(callback: types.CallbackQuery):
    await callback.message.answer("✅ বাটন কাজ করছে! 🎉")
    await callback.answer("সফল!", show_alert=True)

async def main():
    print("🚀 Test Bot চালু আছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
