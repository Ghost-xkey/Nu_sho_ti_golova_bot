from aiogram import Bot
from config import TOKEN, CHAT_ID, YEARLY_MESSAGE, YANDEX_TRACK_URL, get_yearly_photo
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
    """Отправляет ежегодное сообщение (старая версия для совместимости)"""
    bot = Bot(token=TOKEN)
    try:
        # Отправляем сообщение с текстом и ссылкой на трек
        message_text = f"{YEARLY_MESSAGE}\n\n🎵 Музыка: {YANDEX_TRACK_URL}"
        
        print(f"Sending yearly message to chat_id: {CHAT_ID}")
        print(f"Message text: {message_text}")
        
        # Получаем file_id картинки
        photo_file_id = get_yearly_photo()
        
        if photo_file_id:
            # Отправляем сообщение с картинкой
            await bot.send_photo(
                chat_id=CHAT_ID, 
                photo=photo_file_id,
                caption=message_text
            )
            print(f"Yearly message with photo sent successfully: {photo_file_id}")
        else:
            # Отправляем обычное сообщение без картинки
            await bot.send_message(chat_id=CHAT_ID, text=message_text)
            print("Yearly message without photo sent successfully")
        
    except Exception as e:
        print(f"Error sending yearly message: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()

async def send_yearly_event_message(event_data):
    """Отправляет сообщение для конкретного ежегодного события"""
    bot = Bot(token=TOKEN)
    try:
        event_id, name, day, month, hour, minute, message_text, music_url, photo_file_id, is_active, created_at = event_data
        
        # Формируем сообщение
        full_message = f"🎉 **{name}**\n\n{message_text}"
        
        if music_url:
            full_message += f"\n\n🎵 Музыка: {music_url}"
        
        print(f"Sending yearly event message: {name} to chat_id: {CHAT_ID}")
        print(f"Message text: {full_message}")
        
        if photo_file_id:
            # Отправляем сообщение с картинкой
            await bot.send_photo(
                chat_id=CHAT_ID, 
                photo=photo_file_id,
                caption=full_message
            )
            print(f"Yearly event message with photo sent successfully: {photo_file_id}")
        else:
            # Отправляем обычное сообщение без картинки
            await bot.send_message(chat_id=CHAT_ID, text=full_message)
            print("Yearly event message without photo sent successfully")
        
    except Exception as e:
        print(f"Error sending yearly event message: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()
