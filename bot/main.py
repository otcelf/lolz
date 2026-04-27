import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import start, deals, requisites, other, worker, admin
from middleware import BanCheckMiddleware

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(BanCheckMiddleware())
    dp.callback_query.middleware(BanCheckMiddleware())

    dp.include_router(start.router)
    dp.include_router(deals.router)
    dp.include_router(requisites.router)
    dp.include_router(worker.router)
    dp.include_router(other.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
