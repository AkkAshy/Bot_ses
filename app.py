from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.user_form import router as user_router
from handlers.admin import router as admin_router
import asyncio
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()


dp.include_router(admin_router)
dp.include_router(user_router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())