from aiogram import Bot
from config import TOKEN, CHAT_ID
from db import get_random_video, get_video_count

async def send_daily_message():
    bot = Bot(token=TOKEN)
    try:
        # Получаем случайное видео
        video_data = get_random_video()
        
        if video_data:
            file_id, file_unique_id, username, caption = video_data
            message_text = f"🎥 Давайте вспомним, как было круто?\n\n📹 От: {username}"
            
            # Отправляем видео с подписью
            await bot.send_video(
                chat_id=CHAT_ID,
                video=file_id,
                caption=message_text
            )
            print(f"Random video sent: {file_id}")
        else:
            # Если нет видео, отправляем обычное сообщение
            await bot.send_message(chat_id=CHAT_ID, text="Охуенный блять совет на сегодня, братики!")
            print("No videos available, sent regular message")
            
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
