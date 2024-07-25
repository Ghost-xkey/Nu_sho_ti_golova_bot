from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import start_polling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN
from handlers import router  # Импортируем router
from utils import send_daily_message, send_yearly_message

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация роутера
dp.include_router(router)  # Включаем router в Dispatcher

# Планировщик заданий
scheduler = AsyncIOScheduler()

# Настройка задач для планировщика
scheduler.add_job(send_daily_message, "cron", hour=9, minute=0)
scheduler.add_job(send_yearly_message, "cron", month=7, day=25, hour=9, minute=0)

async def on_startup(dispatcher):
    logging.info("Starting bot")
    scheduler.start()

async def on_shutdown(dispatcher):
    logging.info("Shutting down bot")
    scheduler.shutdown()

if __name__ == "__main__":
    dp.run_polling(skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
