from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
import fal_client
from datetime import datetime

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

client = fal_client.AsyncClient(key=os.getenv("FAL_KEY"))

user_data = {}

# Finger options with proper prompt names
FINGERS = {
    "🫆": "index finger",
    "👆": "right index finger",
    "👇": "middle finger",
    "✌️": "two fingers (peace sign)",
    "👍": "thumb up",
    "👌": "OK sign",
    "🤘": "rock on sign",
    "🖐️": "open palm with all fingers",
}

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=4)
    for emoji, name in FINGERS.items():
        kb.add(InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}"))
    
    await message.answer(
        "🖐️ **Finger Verification Bot**\n\n"
        "যে ফিঙ্গার তুলে ধরতে চাও সেটা সিলেক্ট করো:",
        reply_markup=kb
    )

@dp.callback_query(F.callback_data.startswith("finger_"))
async def process_finger(callback: types.CallbackQuery):
    emoji = callback.data.split("_")[1]
    finger_name = FINGERS.get(emoji, "index finger")
    
    user_data[callback.from_user.id] = {
        "emoji": emoji,
        "finger_name": finger_name,
        "image_url": "https://i.imgur.com/YOUR_IMAGE_LINK.jpg"  # পরে চেঞ্জ করবো
    }
    
    await callback.message.answer(
        f"✅ সিলেক্ট করা হয়েছে: {emoji}\n\n"
        "এখন তোমার **Full Name** লিখো:"
    )
    await callback.answer()

@dp.message()
async def collect_info(message: types.Message):
    uid = message.from_user.id
    if uid not in user_data:
        return await message.answer("/start চাপো")

    data = user_data[uid]

    if "name" not in data:
        data["name"] = message.text
        await message.answer("পিতার নাম লিখো:")
    elif "father" not in data:
        data["father"] = message.text
        await generate_ai_image(message, data)

async def generate_ai_image(message: types.Message, data):
    try:
        await message.answer("🧠 AI দিয়ে ছবি এডিট করা হচ্ছে... কিছুক্ষণ সময় লাগবে।")

        prompt = f"the girl is holding up her {data['finger_name']} clearly visible towards the camera, photorealistic, same face, same girl, same outfit, high detail"

        result = await client.run(
            "fal-ai/flux-pro/kontext",  # অথবা "xai/grok-imagine-image/edit"
            arguments={
                "image_url": "https://files.catbox.moe/0v3f8k.jpg",  # তোমার ছবির লিংক এখানে দাও
                "prompt": prompt,
                "strength": 0.75,
                "num_images": 1
            }
        )

        edited_url = result["images"][0]["url"]

        await message.answer_photo(
            edited_url,
            caption=f"✅ **Finger Verification Complete**\n\n"
                    f"Name   : {data.get('name')}\n"
                    f"Father : {data.get('father')}\n"
                    f"Date   : {datetime.now().strftime('%d/%m/%Y')}\n\n"
                    f"Selected Finger: {data['emoji']}"
        )

    except Exception as e:
        await message.answer(f"❌ এরর হয়েছে: {str(e)}\n\nআবার /start চাপো")

async def main():
    print("✅ AI Finger Verification Bot চালু আছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
