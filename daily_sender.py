import asyncio
import logging
from datetime import datetime, time
from aiogram import Bot
from aiogram.types import Chat
from db import get_random_video, get_video_count
from config import TARGET_CHAT_ID, SOURCE_CHAT_ID, DAILY_VIDEO_HOUR, DAILY_VIDEO_MINUTE

class DailyVideoSender:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.target_chat_id = TARGET_CHAT_ID  # 2512455884
        self.source_chat_id = SOURCE_CHAT_ID  # 887092139
        
    async def send_daily_video(self):
        """Отправляет случайное видео в целевой чат с подписью"""
        try:
            # Проверяем, есть ли видео в базе
            video_count = get_video_count()
            if video_count == 0:
                logging.info("No videos in database, skipping daily send")
                return
                
            # Получаем случайное видео
            video_data = get_random_video()
            if not video_data:
                logging.warning("Failed to get random video from database")
                return
                
            file_id, file_unique_id, username, caption = video_data
            
            # Формируем подпись
            message_text = "Давайте вспомним, как было круто?"
            if username:
                message_text += f"\n\n📹 От: {username}"
            if caption and caption != "Видеосообщение-кружочек":
                message_text += f"\n💬 {caption}"
                
            # Отправляем видео
            await self.bot.send_video(
                chat_id=self.target_chat_id,
                video=file_id,
                caption=message_text
            )
            
            logging.info(f"Daily video sent to chat {self.target_chat_id}: {file_id}")
            
        except Exception as e:
            logging.error(f"Error sending daily video: {e}")
            
    async def start_daily_scheduler(self):
        """Запускает планировщик ежедневной отправки видео"""
        while True:
            try:
                # Получаем текущее время
                now = datetime.now()
                current_time = now.time()
                
                # Проверяем, наступило ли время отправки
                target_time = time(DAILY_VIDEO_HOUR, DAILY_VIDEO_MINUTE)
                
                if current_time.hour == target_time.hour and current_time.minute == target_time.minute:
                    await self.send_daily_video()
                    
                    # Ждем минуту, чтобы не отправлять несколько раз
                    await asyncio.sleep(60)
                else:
                    # Проверяем каждую минуту
                    await asyncio.sleep(60)
                    
            except Exception as e:
                logging.error(f"Error in daily scheduler: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повтором
