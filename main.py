import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers import router as user_router
from admin import admin_router
from db import create_tables
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)

# Инициализация диспетчера с MemoryStorage
dp = Dispatcher(storage=MemoryStorage())

# Регистрация маршрутизаторов
router = Router()
router.include_router(user_router)
router.include_router(admin_router)
dp.include_router(router)

# Создание таблиц в БД
create_tables()

# Функция для отправки сообщения
async def send_daily_message():
    try:
        response = requests.get("http://fucking-great-advice.ru/api/random")
        advice = response.json()['text']
        chat_id = '-573460520'  # Укажите ID вашего чата или канала
        await bot.send_message(chat_id=chat_id, text=f"Охуенный блять совет на сегодня, братики! {advice}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

# Инициализация планировщика
scheduler = AsyncIOScheduler()

# Добавление задачи в пла
