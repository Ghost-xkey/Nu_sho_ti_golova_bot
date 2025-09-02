from aiogram import Bot
from config import TOKEN, CHAT_ID

async def send_daily_message():
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text="Охуенный блять совет на сегодня, братики!")
    except Exception as e:
        print(f"Error sending daily message: {e}")
    finally:
        await bot.session.close()

async def send_yearly_message():
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text="Ну шо ты лысый @perfomers")
    except Exception as e:
        print(f"Error sending yearly message: {e}")
    finally:
        await bot.session.close()
