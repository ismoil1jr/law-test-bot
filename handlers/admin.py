from aiogram import Router, types
from aiogram.filters import Command
from database import SessionLocal
from admin_service import add_user_with_limit  # service faylingiz joylashuviga qarab

router = Router()

@router.message(Command("add"))
async def add_user_handler(message: types.Message):
    ADMIN_IDS = [12345678]  # O'zingizning Telegram ID-ingiz
    if message.from_user.id not in ADMIN_IDS:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Noto'g'ri format.\nIshlatish: `/add 12345678` yoki `/add @username`", parse_mode="Markdown")
        return

    identifier = args[1]
    db = SessionLocal()
    
    try:
        result = add_user_with_limit(db, identifier, test_count=5)
        await message.answer(f"✅ {result['msg']}")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
    finally:
        db.close()