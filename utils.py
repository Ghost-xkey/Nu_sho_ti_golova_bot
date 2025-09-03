from aiogram import Bot
from config import TOKEN, CHAT_ID, YEARLY_MESSAGE, YANDEX_TRACK_URL
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
        # Отправляем сообщение с текстом и ссылкой на трек
        message_text = f"{YEARLY_MESSAGE}\n\n🎵 Музыка: {YANDEX_TRACK_URL}"
        
        await bot.send_message(chat_id=CHAT_ID, text=message_text)
        print("Yearly message sent successfully")
        
        # TODO: Добавить отправку картинки когда она будет загружена
        # await bot.send_photo(chat_id=CHAT_ID, photo=photo_file_id)
        
    except Exception as e:
        print(f"Error sending yearly message: {e}")
    finally:
        await bot.session.close()
