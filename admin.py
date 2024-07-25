from aiogram import Router, types
from aiogram.filters import Command

admin_router = Router()

@admin_router.message(Command(commands=["admin"]))
async def admin_command(message: types.Message):
    await message.answer("Привет, админ!")
