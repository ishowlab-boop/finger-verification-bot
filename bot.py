from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
import asyncio
from PIL import Image, ImageDraw
import io
import os
from datetime import datetime

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router = Router()

user_data = {}

FINGER_EMOJIS = [
    "🫆", "✋", "👆", "👇", "👈", "👉", "👍", "👎", "👌", "✌️",
    "🤞", "🤘", "🤙", "🖐️", "✊", "👊", "🤛", "🤜", "👋", "🫱",
    "🫲", "🫳", "🫴", "🫵", "🤏", "🤌", "🖖", "🫰", "💪", "🙌"
]

@router.message(Command("start"))
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer(
        "👋 **Finger Verification Paper Bot** এ স্বাগতম!\n\n"
        "প্রথমে তোমার তথ্য দাও:\n"
        "নাম লিখো (Full Name):"
    )

@router.message()
async def process_info(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("আবার /start করো")
        return

    data = user_data[user_id]
    
    if "name" not in data:
        data["name"] = message.text
        await message.answer("পিতার নাম লিখো:")
    elif "father" not in data:
        data["father"] = message.text
        await message.answer("জন্ম তারিখ (DD/MM/YYYY):")
    elif "dob" not in data:
        data["dob"] = message.text
        await message.answer("ঠিকানা লিখো:")
    elif "address" not in data:
        data["address"] = message.text
        await show_finger_selection(message)
    else:
        await message.answer("ইতিমধ্যে প্রসেস চলছে...")

async def show_finger_selection(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=4)
    buttons = [InlineKeyboardButton(text=emoji, callback_data=f"finger_{emoji}") for emoji in FINGER_EMOJIS]
    keyboard.inline_keyboard = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
    
    await message.answer(
        "✅ তথ্য সংগ্রহ হয়েছে!\n\n"
        "এখন ফিঙ্গারপ্রিন্টের জন্য একটা ইমোজি সিলেক্ট করো:",
        reply_markup=keyboard
    )

@router.callback_query(F.callback_data.startswith("finger_"))
async def generate_paper(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    emoji = callback.data.split("_")[1]
    
    if user_id not in user_data:
        await callback.answer("সমস্যা হয়েছে, আবার /start করো")
        return

    data = user_data[user_id]
    
    # Create image
    img = Image.new('RGB', (800, 1000), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([0, 0, 800, 120], fill='#1e3a8a')
    draw.text((150, 40), "FINGERPRINT VERIFICATION PAPER", fill='white', font_size=35)
    
    # Info
    lines = [
        f"Full Name     : {data.get('name', 'N/A')}",
        f"Father's Name : {data.get('father', 'N/A')}",
        f"Date of Birth : {data.get('dob', 'N/A')}",
        f"Address       : {data.get('address', 'N/A')}",
        f"Date          : {datetime.now().strftime('%d/%m/%Y')}",
        "",
        "Fingerprint:"
    ]
    
    y = 180
    for line in lines:
        draw.text((50, y), line, fill='black', font_size=26)
        y += 55
    
    # Fingerprint box
    draw.rectangle([280, 520, 520, 760], outline='#1e3a8a', width=10)
    draw.text((360, 590), emoji, font_size=140)
    
    draw.text((250, 820), "Authorized Signature / Stamp", fill='gray', font_size=26)
    
    # Save to bytes
    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    
    await callback.message.answer_photo(
        bio,
        caption="✅ তোমার Fingerprint Verification Paper রেডি!\n\nআবার /start করো নতুন একটা বানাতে।"
    )
    await callback.answer("✅ Done!")

dp.include_router(router)

async def main():
    print("✅ Finger Verification Bot চালু হয়েছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
