from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN, MEMORY_HOUR, MEMORY_MINUTE, YEARLY_DAY, YEARLY_MONTH, YEARLY_HOUR, YEARLY_MINUTE
from handlers import router
from utils import send_daily_message, send_yearly_message, check_and_send_yearly_events, check_and_send_yearly_events_sync
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

# Ежедневные воспоминания
scheduler.add_job(send_daily_message, "cron", hour=MEMORY_HOUR, minute=MEMORY_MINUTE)

# Старое ежегодное сообщение (для совместимости)
scheduler.add_job(send_yearly_message, "cron", month=YEARLY_MONTH, day=YEARLY_DAY, hour=YEARLY_HOUR, minute=YEARLY_MINUTE)

# Проверка множественных ежегодных событий (каждые 30 секунд для тестирования)
scheduler.add_job(check_and_send_yearly_events, "interval", seconds=30)

# Синхронная версия для тестирования (каждые 15 секунд)
scheduler.add_job(check_and_send_yearly_events_sync, "interval", seconds=15)

# Тестовая функция для проверки планировщика (каждые 10 секунд)
async def test_scheduler():
    logging.info("🧪 Test scheduler function called!")

scheduler.add_job(test_scheduler, "interval", seconds=10)

async def on_startup(dispatcher):
    logging.info("🚀 on_startup function called!")
    try:
        logging.info("Starting bot")
        logging.info("Creating database tables...")
        create_tables()
        logging.info("Database initialized")
        
        logging.info("Starting scheduler...")
        scheduler.start()
        logging.info("Scheduler started successfully")
        
        # Проверим, что задачи добавлены
        jobs = scheduler.get_jobs()
        logging.info(f"Scheduler has {len(jobs)} jobs:")
        for job in jobs:
            logging.info(f"  - {job.name}: {job.trigger}")
            
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
    
    async def main():
        # Запускаем планировщик вручную
        logging.info("🚀 Starting scheduler manually...")
        scheduler.start()
        logging.info("✅ Scheduler started manually")
        
        # Проверим, что задачи добавлены
        jobs = scheduler.get_jobs()
        logging.info(f"Scheduler has {len(jobs)} jobs:")
        for job in jobs:
            logging.info(f"  - {job.name}: {job.trigger}")
        
        # Запускаем бота
        await dp.start_polling(bot, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    
    asyncio.run(main())
