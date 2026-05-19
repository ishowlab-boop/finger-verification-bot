from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👆 Test Button", callback_data="test")]
    ])
    await message.answer("টেস্ট বাটন চাপো 👇", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "test")
async def test_button(callback: types.CallbackQuery):
    await callback.message.edit_text("✅ বাটন কাজ করছে! 🎉\n\nএবার সব ঠিক আছে।")
    await callback.answer("সফল!", show_alert=True)

async def main():
    print("🚀 Test Bot চালু হয়েছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
