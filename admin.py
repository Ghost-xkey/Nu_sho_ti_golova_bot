from aiogram import Router, types
from aiogram.filters import Command

admin_router = Router()

@admin_router.message(Command(commands=["admin"]))
async def admin_command(message: types.Message):
    try:
        await message.answer("Привет, админ!")
    except Exception as e:
        print(f"Error in admin command: {e}")
