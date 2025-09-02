from aiogram import Router, types
from aiogram.filters import BaseFilter, Command
from text import WELCOME_MESSAGE, HELP_MESSAGE
from kb import main_keyboard

class TextEqualsFilter(BaseFilter):
    def __init__(self, text: str, ignore_case: bool = True):
        self.text = text
        self.ignore_case = ignore_case

    async def __call__(self, message: types.Message) -> bool:
        if message.text is None:
            return False
        if self.ignore_case:
            return message.text.lower() == self.text.lower()
        return message.text == self.text

router = Router()

@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    try:
        await message.answer(WELCOME_MESSAGE, reply_markup=main_keyboard())
    except Exception as e:
        print(f"Error in start command: {e}")

@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    try:
        await message.answer(HELP_MESSAGE)
    except Exception as e:
        print(f"Error in help command: {e}")

@router.message(TextEqualsFilter(text="Привет"))
async def greet(message: types.Message):
    try:
        await message.answer("Привет! Как дела?")
    except Exception as e:
        print(f"Error in greet handler: {e}")
