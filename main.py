import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN
from handlers import register_handlers
from admin import register_admin_handlers
from utils import send_daily_message, send_yearly_message

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

scheduler = AsyncIOScheduler()

# Register handlers
register_handlers(dp)
register_admin_handlers(dp)

# Schedule daily message
scheduler.add_job(send_daily_message, "cron", hour=9, minute=0)

# Schedule yearly message on 25th of July
scheduler.add_job(send_yearly_message, "cron", month=7, day=25, hour=9, minute=0)

async def on_startup(dispatcher):
    logging.info("Starting bot")
    scheduler.start()

async def on_shutdown(dispatcher):
    logging.info("Shutting down bot")
    scheduler.shutdown()

if __name__ == "__main__":
    start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
