from aiogram import Router, types
from aiogram.filters import BaseFilter, CommandStart, Command
from text import WELCOME_MESSAGE, HELP_MESSAGE
from kb import main_keyboard
from db import save_video_message, get_video_count, get_user_stats, get_total_users
import logging

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

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        logging.info(f"Start command received from user {message.from_user.id}")
        await message.answer(WELCOME_MESSAGE, reply_markup=main_keyboard())
        logging.info("Start command response sent")
    except Exception as e:
        logging.error(f"Error in start command: {e}")

@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    try:
        await message.answer(HELP_MESSAGE)
    except Exception as e:
        print(f"Error in help command: {e}")

@router.message(Command(commands=["videos"]))
async def cmd_videos(message: types.Message):
    """Показывает статистику видеосообщений"""
    try:
        video_count = get_video_count()
        if video_count > 0:
            await message.answer(f"🎥 В коллекции воспоминаний: {video_count} видеосообщений\n\n"
                               f"Каждый день в 9:00 бот будет отправлять случайное видео с напоминанием!")
        else:
            await message.answer("🎥 Коллекция воспоминаний пуста.\n\n"
                               f"Отправьте видеосообщения в группу, чтобы бот их сохранил!")
    except Exception as e:
        logging.error(f"Error in videos command: {e}")
        await message.answer("❌ Ошибка при получении статистики")

@router.message(Command(commands=["random"]))
async def cmd_random_video(message: types.Message):
    """Отправляет случайное видео прямо сейчас"""
    try:
        from db import get_random_video
        
        video_data = get_random_video()
        
        if video_data:
            file_id, file_unique_id, username, caption = video_data
            message_text = f"🎥 Случайное воспоминание!\n\n📹 От: {username}"
            
            await message.answer_video(
                video=file_id,
                caption=message_text
            )
            logging.info(f"Random video sent manually by user {message.from_user.id}")
        else:
            await message.answer("🎥 Коллекция воспоминаний пуста.\n\n"
                               f"Отправьте видеосообщения в группу, чтобы бот их сохранил!")
    except Exception as e:
        logging.error(f"Error in random video command: {e}")
        await message.answer("❌ Ошибка при отправке случайного видео")

@router.message(Command(commands=["stats"]))
async def cmd_stats(message: types.Message):
    """Показывает статистику по пользователям"""
    try:
        video_count = get_video_count()
        total_users = get_total_users()
        user_stats = get_user_stats()
        
        if video_count > 0:
            stats_text = f"📊 Статистика коллекции воспоминаний:\n\n"
            stats_text += f"🎥 Всего видео: {video_count}\n"
            stats_text += f"👥 Участников: {total_users}\n\n"
            stats_text += f"🏆 Топ участников:\n"
            
            for i, (username, count) in enumerate(user_stats[:5], 1):
                stats_text += f"{i}. {username}: {count} видео\n"
                
            await message.answer(stats_text)
        else:
            await message.answer("📊 Статистика пуста.\n\n"
                               f"Отправьте видеосообщения в группу, чтобы увидеть статистику!")
    except Exception as e:
        logging.error(f"Error in stats command: {e}")
        await message.answer("❌ Ошибка при получении статистики")

@router.message(Command(commands=["time"]))
async def cmd_time(message: types.Message):
    """Показывает текущее время отправки воспоминаний"""
    try:
        from config import MEMORY_HOUR, MEMORY_MINUTE
        
        time_str = f"{MEMORY_HOUR:02d}:{MEMORY_MINUTE:02d}"
        await message.answer(f"⏰ Время отправки воспоминаний: {time_str}\n\n"
                           f"Для изменения времени обратитесь к администратору бота.")
    except Exception as e:
        logging.error(f"Error in time command: {e}")
        await message.answer("❌ Ошибка при получении времени")

@router.message(Command(commands=["add_video"]))
async def cmd_add_video(message: types.Message):
    """Добавляет видео вручную по file_id (для админов)"""
    try:
        # Проверяем, что это админ (можно настроить список админов)
        admin_ids = [203593418]  # Замените на ID админов
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        # Получаем file_id из текста команды
        command_text = message.text.split()
        if len(command_text) < 2:
            await message.answer("❌ Использование: /add_video <file_id>\n\n"
                               f"Пример: /add_video DQACAgIAAyEFAASVwQjMAAINKmi3iN_95n1LCbr-QabEUt3-qRvNAAKYdwACYNnASeJU1kTZBTitNgQ")
            return
        
        file_id = command_text[1]
        
        # Сохраняем видео
        success = save_video_message(
            file_id=file_id,
            file_unique_id=f"manual_{file_id[:10]}",  # Генерируем уникальный ID
            message_id=message.message_id,
            user_id=message.from_user.id,
            username=message.from_user.username or message.from_user.first_name,
            caption="Добавлено вручную"
        )
        
        if success:
            video_count = get_video_count()
            await message.answer(f"✅ Видео добавлено вручную!\n\n"
                               f"Всего в коллекции: {video_count}")
        else:
            await message.answer("❌ Ошибка при добавлении видео")
            
    except Exception as e:
        logging.error(f"Error in add_video command: {e}")
        await message.answer("❌ Ошибка при добавлении видео")

@router.message(Command(commands=["test_yearly"]))
async def cmd_test_yearly(message: types.Message):
    """Тестирует ежегодное сообщение (для админов)"""
    try:
        logging.info(f"Test yearly command received from user {message.from_user.id}")
        
        # Проверяем, что это админ
        admin_ids = [203593418]  # Замените на ID админов
        
        logging.info(f"User ID: {message.from_user.id}, Admin IDs: {admin_ids}")
        
        if message.from_user.id not in admin_ids:
            logging.warning(f"User {message.from_user.id} is not admin")
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        logging.info("User is admin, proceeding with test")
        
        # Импортируем функцию отправки
        from utils import send_yearly_message
        
        # Отправляем тестовое сообщение
        logging.info("Sending yearly message...")
        await send_yearly_message()
        logging.info("Yearly message sent successfully")
        await message.answer("✅ Ежегодное сообщение отправлено в группу!")
            
    except Exception as e:
        logging.error(f"Error in test_yearly command: {e}")
        import traceback
        traceback.print_exc()
        await message.answer("❌ Ошибка при отправке тестового сообщения")

@router.message(Command(commands=["my_id"]))
async def cmd_my_id(message: types.Message):
    """Показывает ID пользователя для отладки"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Нет username"
        first_name = message.from_user.first_name or "Нет имени"
        
        await message.answer(f"🆔 Ваш ID: {user_id}\n"
                           f"👤 Username: @{username}\n"
                           f"📝 Имя: {first_name}")
        
        logging.info(f"User ID check: {user_id}, username: {username}, name: {first_name}")
        
    except Exception as e:
        logging.error(f"Error in my_id command: {e}")
        await message.answer("❌ Ошибка при получении ID")

@router.message(TextEqualsFilter(text="Привет"))
async def greet(message: types.Message):
    try:
        await message.answer("Привет! Как дела?")
    except Exception as e:
        print(f"Error in greet handler: {e}")

@router.message(lambda message: message.video is not None)
async def handle_video(message: types.Message):
    """Обрабатывает видеосообщения и сохраняет их в базу данных"""
    try:
        logging.info(f"Video message received from user {message.from_user.id}")
        video = message.video
        user = message.from_user
        
        logging.info(f"Video details: file_id={video.file_id}, file_unique_id={video.file_unique_id}")
        
        # Сохраняем видеосообщение в базу данных
        success = save_video_message(
            file_id=video.file_id,
            file_unique_id=video.file_unique_id,
            message_id=message.message_id,
            user_id=user.id,
            username=user.username or user.first_name,
            caption=message.caption
        )
        
        if success:
            logging.info(f"Video saved successfully from user {user.id}: {video.file_id}")
        else:
            logging.error(f"Failed to save video from user {user.id}: {video.file_id}")
            
    except Exception as e:
        logging.error(f"Error handling video: {e}")
        await message.reply("❌ Произошла ошибка при обработке видео")

@router.message(lambda message: message.video_note is not None)
async def handle_video_note(message: types.Message):
    """Обрабатывает видеосообщения-кружочки и сохраняет их в базу данных"""
    try:
        logging.info(f"Video note received from user {message.from_user.id}")
        video_note = message.video_note
        user = message.from_user
        
        logging.info(f"Video note details: file_id={video_note.file_id}, file_unique_id={video_note.file_unique_id}")
        
        # Сохраняем видеосообщение в базу данных
        success = save_video_message(
            file_id=video_note.file_id,
            file_unique_id=video_note.file_unique_id,
            message_id=message.message_id,
            user_id=user.id,
            username=user.username or user.first_name,
            caption="Видеосообщение-кружочек"
        )
        
        if success:
            logging.info(f"Video note saved successfully from user {user.id}: {video_note.file_id}")
        else:
            logging.error(f"Failed to save video note from user {user.id}: {video_note.file_id}")
            
    except Exception as e:
        logging.error(f"Error handling video note: {e}")
        await message.reply("❌ Произошла ошибка при обработке видеосообщения")
