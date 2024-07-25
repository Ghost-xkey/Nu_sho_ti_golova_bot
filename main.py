import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config import API_TOKEN
from handlers import router
from admin import admin_router
from db import create_tables
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)

# Инициализация диспетчера
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Регистрация маршрутизаторов
dp.include_router(router)
dp.include_router(admin_router)

# Создание таблиц в БД
create_tables()

# Функция для отправки сообщения
async def send_daily_message():
    try:
        response = requests.get("http://fucking-great-advice.ru/api/random")
        advice = response.json()['text']
        chat_id = '-573460520'  # Укажите ID вашего чата или канала
        await bot.send_message(chat_id=chat_id, text=advice)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

# Инициализация планировщика
scheduler = AsyncIOScheduler()

# Добавление задачи в планировщик
scheduler.add_job(send_daily_message, 'cron', hour=10, minute=0, timezone='Europe/Moscow')

# Запуск планировщика
scheduler.start()

async def on_startup(dispatcher):
    logging.info("Бот запущен")
    await send_daily_message()

async def on_shutdown(dispatcher):
    logging.info("Бот остановлен")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
