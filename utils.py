from aiogram import Bot
from config import TOKEN

bot = Bot(token=TOKEN)

async def send_daily_message():
    await bot.send_message(chat_id="-573460520", text="Охуенный блять совет на сегодня, братики!")

async def send_yearly_message():
    await bot.send_message(chat_id="-573460520", text="Ну шо ты лысый @perfomers")
