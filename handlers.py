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

@router.message(Command(commands=["test_chat"]))
async def cmd_test_chat(message: types.Message):
    """Тестирует отправку сообщения в группу (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        from config import CHAT_ID
        from aiogram import Bot
        from config import TOKEN
        
        bot = Bot(token=TOKEN)
        
        try:
            # Отправляем тестовое сообщение в группу
            await bot.send_message(
                chat_id=CHAT_ID, 
                text="🧪 Тестовое сообщение от бота!\n\nЕсли вы видите это сообщение, значит бот работает в группе."
            )
            await message.answer(f"✅ Тестовое сообщение отправлено в группу {CHAT_ID}")
            
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки в группу: {e}")
            
        finally:
            await bot.session.close()
            
    except Exception as e:
        logging.error(f"Error in test_chat command: {e}")
        await message.answer("❌ Ошибка при тестировании чата")

@router.message(Command(commands=["get_chat_id"]))
async def cmd_get_chat_id(message: types.Message):
    """Показывает ID текущего чата"""
    try:
        chat_id = message.chat.id
        chat_type = message.chat.type
        chat_title = message.chat.title or "Личный чат"
        
        await message.answer(f"🆔 ID чата: {chat_id}\n"
                           f"📝 Тип: {chat_type}\n"
                           f"🏷️ Название: {chat_title}")
        
        logging.info(f"Chat ID: {chat_id}, Type: {chat_type}, Title: {chat_title}")
        
    except Exception as e:
        logging.error(f"Error in get_chat_id command: {e}")
        await message.answer("❌ Ошибка при получении ID чата")

@router.message(Command(commands=["set_yearly_image"]))
async def cmd_set_yearly_image(message: types.Message):
    """Устанавливает картинку для ежегодного сообщения (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        # Проверяем, что это изображение
        if not message.photo:
            await message.answer("❌ Пожалуйста, отправьте изображение вместе с командой /set_yearly_image")
            return
        
        # Получаем file_id самого большого размера
        photo = message.photo[-1]
        file_id = photo.file_id
        
        # Обновляем конфиг
        from config import update_yearly_photo
        update_yearly_photo(file_id)
        
        await message.answer(f"✅ Картинка для ежегодного сообщения установлена!\n\n"
                           f"File ID: {file_id}\n"
                           f"Теперь ежегодное сообщение будет отправляться с этой картинкой.")
        
        logging.info(f"Yearly image updated by user {message.from_user.id}: {file_id}")
        
    except Exception as e:
        logging.error(f"Error in set_yearly_image command: {e}")
        await message.answer("❌ Ошибка при установке картинки")

@router.message(Command(commands=["remove_yearly_image"]))
async def cmd_remove_yearly_image(message: types.Message):
    """Удаляет картинку для ежегодного сообщения (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        # Удаляем картинку из конфига
        from config import remove_yearly_photo
        remove_yearly_photo()
        
        await message.answer("✅ Картинка для ежегодного сообщения удалена!\n\n"
                           "Теперь ежегодное сообщение будет отправляться без картинки.")
        
        logging.info(f"Yearly image removed by user {message.from_user.id}")
        
    except Exception as e:
        logging.error(f"Error in remove_yearly_image command: {e}")
        await message.answer("❌ Ошибка при удалении картинки")

@router.message(Command(commands=["add_yearly_event"]))
async def cmd_add_yearly_event(message: types.Message):
    """Добавляет новое ежегодное событие (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        # Получаем параметры из команды
        command_text = message.text.split()
        if len(command_text) < 4:
            await message.answer("❌ Использование: /add_yearly_event <название> <день> <месяц> [час] [минута]\n\n"
                               "Пример: /add_yearly_event День_рождения 15 3 12 0\n"
                               "Пример: /add_yearly_event Новый_год 1 1")
            return
        
        # Извлекаем название (может содержать подчеркивания вместо пробелов)
        name = command_text[1].replace('_', ' ')
        
        # Извлекаем числовые параметры
        try:
            day = int(command_text[2])
            month = int(command_text[3])
            hour = int(command_text[4]) if len(command_text) > 4 else 10
            minute = int(command_text[5]) if len(command_text) > 5 else 0
        except ValueError as e:
            await message.answer(f"❌ Ошибка в параметрах: {e}\n\n"
                               "Убедитесь, что день, месяц, час и минута - это числа")
            return
        
        # Добавляем событие
        from db import add_yearly_event, get_yearly_events
        
        logging.info(f"Adding yearly event: name={name}, day={day}, month={month}, hour={hour}, minute={minute}")
        
        # Проверим, что таблица существует
        existing_events = get_yearly_events()
        logging.info(f"Existing events count: {len(existing_events)}")
        
        # Попробуем вызвать функцию напрямую
        try:
            logging.info("Calling add_yearly_event function...")
            logging.info(f"Parameters: name={name}, day={day}, month={month}, hour={hour}, minute={minute}")
            
            # Проверим, что функция импортирована
            from db import add_yearly_event
            logging.info(f"add_yearly_event function: {add_yearly_event}")
            
            success = add_yearly_event(name, day, month, hour, minute, f"{name}!")
            logging.info(f"Function call completed, result: {success}")
        except Exception as e:
            logging.error(f"Exception in add_yearly_event: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        logging.info(f"Add yearly event result: {success}")
        
        # Проверим, что событие добавилось
        events_after = get_yearly_events()
        logging.info(f"Events after adding: {len(events_after)}")
        
        if success:
            await message.answer(f"✅ Ежегодное событие добавлено!\n\n"
                               f"📅 Название: {name}\n"
                               f"📆 Дата: {day}.{month}\n"
                               f"⏰ Время: {hour:02d}:{minute:02d}")
        else:
            await message.answer("❌ Ошибка при добавлении события")
            
    except Exception as e:
        logging.error(f"Error in add_yearly_event command: {e}")
        await message.answer("❌ Ошибка при добавлении события")

@router.message(Command(commands=["list_yearly_events"]))
async def cmd_list_yearly_events(message: types.Message):
    """Показывает список всех ежегодных событий"""
    try:
        from db import get_yearly_events
        
        events = get_yearly_events()
        
        if not events:
            await message.answer("📅 Ежегодных событий пока нет")
            return
        
        events_text = "📅 **Ежегодные события:**\n\n"
        
        for event in events:
            event_id, name, day, month, hour, minute, message_text, music_url, photo_file_id, is_active, created_at = event
            events_text += f"🆔 **{event_id}** - {name}\n"
            events_text += f"📆 {day:02d}.{month:02d} в {hour:02d}:{minute:02d}\n"
            events_text += f"💬 {message_text[:50]}{'...' if len(message_text) > 50 else ''}\n\n"
        
        await message.answer(events_text)
        
    except Exception as e:
        logging.error(f"Error in list_yearly_events command: {e}")
        await message.answer("❌ Ошибка при получении списка событий")

@router.message(Command(commands=["delete_yearly_event"]))
async def cmd_delete_yearly_event(message: types.Message):
    """Удаляет ежегодное событие (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        # Получаем ID события
        command_text = message.text.split()
        if len(command_text) < 2:
            await message.answer("❌ Использование: /delete_yearly_event <ID_события>\n\n"
                               "Сначала используйте /list_yearly_events чтобы увидеть ID")
            return
        
        event_id = int(command_text[1])
        
        # Удаляем событие
        from db import delete_yearly_event
        success = delete_yearly_event(event_id)
        
        if success:
            await message.answer(f"✅ Событие {event_id} удалено!")
        else:
            await message.answer("❌ Ошибка при удалении события")
            
    except Exception as e:
        logging.error(f"Error in delete_yearly_event command: {e}")
        await message.answer("❌ Ошибка при удалении события")

@router.message(Command(commands=["init_db"]))
async def cmd_init_db(message: types.Message):
    """Принудительно создает таблицы базы данных (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        # Принудительно создаем таблицы
        from db import create_tables
        create_tables()
        
        await message.answer("✅ Таблицы базы данных созданы/обновлены!")
        
        logging.info(f"Database tables initialized by user {message.from_user.id}")
        
    except Exception as e:
        logging.error(f"Error in init_db command: {e}")
        await message.answer("❌ Ошибка при создании таблиц")

@router.message(Command(commands=["debug_db"]))
async def cmd_debug_db(message: types.Message):
    """Диагностика базы данных (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        import os
        from config import DB_PATH
        
        # Проверяем файл базы данных
        debug_info = f"🔍 **Диагностика базы данных:**\n\n"
        debug_info += f"📁 Путь к БД: `{DB_PATH}`\n"
        debug_info += f"📂 Текущая директория: `{os.getcwd()}`\n"
        debug_info += f"📋 Содержимое директории:\n"
        
        try:
            files = os.listdir('.')
            for file in files[:10]:  # Показываем первые 10 файлов
                debug_info += f"  - {file}\n"
            if len(files) > 10:
                debug_info += f"  ... и еще {len(files) - 10} файлов\n"
        except Exception as e:
            debug_info += f"  ❌ Ошибка чтения директории: {e}\n"
        
        debug_info += f"\n📊 Статус файла БД:\n"
        if os.path.exists(DB_PATH):
            debug_info += f"  ✅ Файл существует\n"
            debug_info += f"  📏 Размер: {os.path.getsize(DB_PATH)} байт\n"
            debug_info += f"  🔐 Права: {oct(os.stat(DB_PATH).st_mode)[-3:]}\n"
        else:
            debug_info += f"  ❌ Файл не существует\n"
        
        # Пробуем создать тестовое подключение
        debug_info += f"\n🔌 Тест подключения:\n"
        try:
            import sqlite3
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            debug_info += f"  ✅ Подключение успешно\n"
            debug_info += f"  📋 Таблицы: {[table[0] for table in tables]}\n"
            conn.close()
        except Exception as e:
            debug_info += f"  ❌ Ошибка подключения: {e}\n"
        
        await message.answer(debug_info)
        
    except Exception as e:
        logging.error(f"Error in debug_db command: {e}")
        await message.answer(f"❌ Ошибка диагностики: {e}")

@router.message(Command(commands=["reset_db"]))
async def cmd_reset_db(message: types.Message):
    """Сбрасывает базу данных (для админов)"""
    try:
        # Проверяем, что это админ
        admin_ids = [203593418]
        
        if message.from_user.id not in admin_ids:
            await message.answer("❌ У вас нет прав для выполнения этой команды")
            return
        
        import os
        from config import DB_PATH
        
        # Удаляем файл/директорию базы данных если они существуют
        if DB_PATH != ':memory:' and os.path.exists(DB_PATH):
            import shutil
            if os.path.isdir(DB_PATH):
                # Если это директория, удаляем её
                shutil.rmtree(DB_PATH)
                await message.answer(f"✅ Директория базы данных удалена: {DB_PATH}")
            else:
                # Если это файл, удаляем его
                os.remove(DB_PATH)
                await message.answer(f"✅ Файл базы данных удален: {DB_PATH}")
        else:
            await message.answer("ℹ️ База данных в памяти или файл не существует")
        
        # Пересоздаем таблицы
        from db import create_tables
        create_tables()
        
        await message.answer("✅ База данных сброшена и таблицы пересозданы!")
        
        logging.info(f"Database reset by user {message.from_user.id}")
        
    except Exception as e:
        logging.error(f"Error in reset_db command: {e}")
        await message.answer(f"❌ Ошибка сброса базы данных: {e}")

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
