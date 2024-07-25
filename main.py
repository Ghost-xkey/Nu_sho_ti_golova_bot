import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from config import API_TOKEN
from handlers import router
from admin import admin_router
from db import create_tables

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)

# Инициализация диспетчера
dp = Dispatcher()

# Регистрация маршрутизаторов
dp.include_router(router)
dp.include_router(admin_router)

# Создание таблиц в БД
create_tables()

async def on_startup():
    # Ваши действия при старте (например, уведомление админов)
    pass

async def on_shutdown():
    # Ваши действия при завершении (например, закрытие соединений)
    pass

# Запуск бота
if __name__ == '__main__':
    dp.run_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)
