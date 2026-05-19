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

FINGERS = ["👆", "🫆", "✌️", "👍", "👌", "🤘", "🖐️"]

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("📸 এডিট করার জন্য একটা ছবি পাঠাও:")

@dp.message(F.photo)
async def receive_photo(message: types.Message):
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{file.file_path}"

        user_data[message.from_user.id] = {"image_url": file_url, "username": message.from_user.first_name}

        # সিম্পল কীবোর্ড
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}")] for emoji in FINGERS
        ])

        await message.answer("✅ ছবি পেয়েছি!\n\nকোন ফিঙ্গার চাও?", reply_markup=kb)
        
    except Exception as e:
        await message.answer("❌ ছবি প্রসেস করতে সমস্যা হয়েছে। আবার পাঠাও।")

# Callback Handler
@dp.callback_query(F.callback_data.startswith("finger_"))
async def edit_image(callback: types.CallbackQuery):
    print(f"✅ Callback received: {callback.data}")  # Log এ দেখা যাবে
    
    uid = callback.from_user.id
    if uid not in user_data:
        return await callback.answer("আগে ছবি পাঠাও!", show_alert=True)

    emoji = callback.data.split("_")[1]
    
    await callback.message.answer(f"🧠 AI এডিট হচ্ছে... {emoji} ফিঙ্গার দিয়ে")

    # এখনো AI না চালিয়ে টেস্ট করার জন্য সিম্পল রেসপন্স
    await callback.message.answer_photo(
        user_data[uid]["image_url"],  # আপাতত একই ছবি পাঠাচ্ছে
        caption=f"✅ টেস্ট সফল!\n\nFinger: {emoji}\nDate: {datetime.now().strftime('%d/%m/%Y')}"
    )

    await callback.answer("✅ Done!")

async def main():
    print("🚀 Bot Started - Test Mode")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
