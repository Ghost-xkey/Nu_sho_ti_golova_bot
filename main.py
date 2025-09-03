from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN, MEMORY_HOUR, MEMORY_MINUTE
from handlers import router
from utils import send_daily_message, send_yearly_message
from db import create_tables
from middlewares import ExampleMiddleware

import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.message.middleware(ExampleMiddleware())
dp.include_router(router)

scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_message, "cron", hour=MEMORY_HOUR, minute=MEMORY_MINUTE)
scheduler.add_job(send_yearly_message, "cron", month=7, day=25, hour=MEMORY_HOUR, minute=MEMORY_MINUTE)

async def on_startup(dispatcher):
    try:
        logging.info("Starting bot")
        logging.info("Creating database tables...")
        create_tables()
        logging.info("Database initialized")
        scheduler.start()
        logging.info("Scheduler started")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        import traceback
        traceback.print_exc()

async def on_shutdown(dispatcher):
    try:
        logging.info("Shutting down bot")
        scheduler.shutdown()
        logging.info("Scheduler stopped")
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown))
