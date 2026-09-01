# main.py
import asyncio
from aiogram import Bot, Dispatcher
from handlers.admin import router as admin_router  # Routerni import qilish

bot = Bot(token="BOT_TOKENIZNI_YOZING")
dp = Dispatcher()

# Admin routerni ro'yxatdan o'tkazish
dp.include_router(admin_router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())