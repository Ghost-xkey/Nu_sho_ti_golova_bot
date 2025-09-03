from aiogram import Router, types
from aiogram.filters import BaseFilter, CommandStart, Command
from text import WELCOME_MESSAGE, HELP_MESSAGE
from kb import main_keyboard
from db import save_video_message, get_video_count
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
        video = message.video
        user = message.from_user
        
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
            video_count = get_video_count()
            await message.reply(f"🎥 Видеосообщение сохранено! Всего в коллекции: {video_count}")
            logging.info(f"Video saved from user {user.id}: {video.file_id}")
        else:
            await message.reply("❌ Ошибка при сохранении видеосообщения")
            
    except Exception as e:
        logging.error(f"Error handling video: {e}")
        await message.reply("❌ Произошла ошибка при обработке видео")
