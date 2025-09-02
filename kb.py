from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Привет")]],
        resize_keyboard=True
    )
    return keyboard
