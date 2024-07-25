from airogram import Router, types
from airogram.filters import Command, Text
from text import WELCOME_MESSAGE, HELP_MESSAGE
from kb import main_keyboard

router = Router()

@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(WELCOME_MESSAGE, reply_markup=main_keyboard())

@router.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer(HELP_MESSAGE)

@router.message(Text(equals="Привет", ignore_case=True))
async def greet(message: types.Message):
    await message.answer("Привет! Как дела?")
