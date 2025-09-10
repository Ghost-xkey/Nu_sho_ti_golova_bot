from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN, MEMORY_HOUR, MEMORY_MINUTE, YEARLY_DAY, YEARLY_MONTH, YEARLY_HOUR, YEARLY_MINUTE, DAILY_VIDEO_SCHEDULES
from handlers import router
from utils import send_daily_message, send_yearly_message, check_and_send_yearly_events, check_and_send_yearly_events_sync, simple_test_function
from db import create_tables
from middlewares import ExampleMiddleware
from facts_generator import FactsGenerator

import logging
import os

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.message.middleware(ExampleMiddleware())
dp.include_router(router)

scheduler = AsyncIOScheduler()

# Ежедневные отправки видео (объединенная логика)
for i, schedule in enumerate(DAILY_VIDEO_SCHEDULES):
    scheduler.add_job(
        send_daily_message, 
        "cron", 
        hour=schedule["hour"], 
        minute=schedule["minute"],
        args=[schedule],
        id=f"daily_video_{i}"
    )
    logging.info(f"Added daily video job {i}: {schedule['hour']}:{schedule['minute']:02d} to chat {schedule['chat_id']}")

# Старое ежегодное сообщение (для совместимости)
scheduler.add_job(send_yearly_message, "cron", month=YEARLY_MONTH, day=YEARLY_DAY, hour=YEARLY_HOUR, minute=YEARLY_MINUTE)

# Проверка множественных ежегодных событий (каждые 30 секунд для тестирования)
scheduler.add_job(check_and_send_yearly_events, "interval", seconds=30)

# Синхронная версия для тестирования (каждые 15 секунд)
scheduler.add_job(check_and_send_yearly_events_sync, "interval", seconds=15)

# Простая тестовая функция (каждые 5 секунд)
scheduler.add_job(simple_test_function, "interval", seconds=5)

# Тестовая функция для проверки планировщика (каждые 10 секунд)
async def test_scheduler():
    logging.info("🧪 Test scheduler function called!")

scheduler.add_job(test_scheduler, "interval", seconds=10)

# ==================== FACTS SCHEDULER ====================

async def send_daily_fact(send_time: str):
    """Отправляет ежедневный факт всем активным пользователям"""
    try:
        logging.info(f"🧠 Sending daily fact at {send_time}")
        
        facts_gen = FactsGenerator()
        active_users = facts_gen.get_all_active_users()
        
        if not active_users:
            logging.info("No active users found for facts")
            return
        
        global bot
        if bot is None:
            logging.error("Bot instance not available")
            return
        
        sent_count = 0
        for user_id in active_users:
            try:
                fact_data = facts_gen.get_random_fact(user_id)
                if fact_data:
                    text = f"🧠 **Факт дня** ({send_time})\n\n{fact_data['fact']}\n\n{fact_data['roast']}"
                    
                    await bot.send_message(user_id, text)
                    facts_gen.mark_fact_as_sent(user_id, fact_data, send_time)
                    sent_count += 1
                    
                    logging.info(f"Fact sent to user {user_id}")
                else:
                    logging.info(f"No available facts for user {user_id}")
                    
            except Exception as e:
                logging.error(f"Error sending fact to user {user_id}: {e}")
        
        logging.info(f"Daily facts sent to {sent_count} users at {send_time}")
        
    except Exception as e:
        logging.error(f"Error in send_daily_fact: {e}")

# Добавляем задачи для отправки фактов в указанное время
fact_times = [
    ("10:00", 10, 0),
    ("13:00", 13, 0), 
    ("17:00", 17, 0),
    ("21:00", 21, 0),
    ("23:00", 23, 0)
]

for time_str, hour, minute in fact_times:
    scheduler.add_job(
        send_daily_fact,
        "cron",
        hour=hour,
        minute=minute,
        args=[time_str],
        id=f"daily_fact_{time_str.replace(':', '')}"
    )
    logging.info(f"Added daily fact job: {time_str}")

async def on_startup(dispatcher):
    logging.info("🚀 on_startup function called!")
    try:
        logging.info("Starting bot")
        logging.info("Creating database tables...")
        
        # Принудительно создаем таблицы
        try:
            create_tables()
            logging.info("✅ Database tables created successfully in on_startup")
        except Exception as db_error:
            logging.error(f"❌ Error creating tables in on_startup: {db_error}")
            import traceback
            traceback.print_exc()
        
        # Инициализируем пользователей по умолчанию
        try:
            from db import init_default_users
            init_default_users()
            logging.info("✅ Default users initialized successfully")
        except Exception as users_error:
            logging.error(f"❌ Error initializing default users: {users_error}")
            import traceback
            traceback.print_exc()
        
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
        
        # Создаем бота без кастомной сессии (aiogram сам создаст)
        global bot
        bot = Bot(token=TOKEN)

        # Запускаем бота с обработкой ошибок
        try:
            # Короткий polling_timeout помогает на нестабильной сети
            skip = os.getenv("SKIP_UPDATES", "true").lower() == "true"
            await dp.start_polling(bot, skip_updates=skip, on_startup=on_startup, on_shutdown=on_shutdown, polling_timeout=10)
        except Exception as e:
            logging.error(f"Ошибка при запуске бота: {e}")
            # Перезапускаем через 5 секунд
            await asyncio.sleep(5)
            skip = os.getenv("SKIP_UPDATES", "true").lower() == "true"
            await dp.start_polling(bot, skip_updates=skip, on_startup=on_startup, on_shutdown=on_shutdown, polling_timeout=10)
    
    asyncio.run(main())
