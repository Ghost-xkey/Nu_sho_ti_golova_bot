import logging
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import executor
from config import API_TOKEN
from handlers import router
from admin import admin_router
from db import create_tables

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Регистрация маршрутизаторов
dp.include_router(router)
dp.include_router(admin_router)

# Создание таблиц в БД
create_tables()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
