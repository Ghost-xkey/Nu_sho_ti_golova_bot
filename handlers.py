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
        from kb import get_main_menu_keyboard
        from db import save_user
        
        # Сохраняем пользователя в базу данных
        user = message.from_user
        save_user(user.id, user.username or user.first_name)
        
        text = "🎉 **ДОБРО ПОЖАЛОВАТЬ!** 🎉\n\n"
        text += "Это бот для управления ежегодными событиями и видеосообщениями!\n\n"
        text += "Выберите действие из меню ниже:"
        
        await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
        logging.info("Start command response sent")
    except Exception as e:
        logging.error(f"Error in start command: {e}")

@router.message(Command(commands=["menu"]))
async def cmd_menu(message: types.Message):
    """Команда для открытия главного меню"""
    try:
        from kb import get_main_menu_keyboard
        from db import save_user
        
        # Сохраняем пользователя в базу данных
        user = message.from_user
        save_user(user.id, user.username or user.first_name)
        
        text = "🎉 **ГЛАВНОЕ МЕНЮ** 🎉\n\n"
        text += "Выберите действие из меню ниже:"
        
        await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
        
    except Exception as e:
        logging.error(f"Error in menu command: {e}")
        await message.answer("❌ Ошибка при открытии меню")

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
        
        # Получаем текст команды (может быть в caption если есть фото)
        command_text_raw = message.text or message.caption or ""
        
        # Проверяем, есть ли текст команды
        if not command_text_raw:
            await message.answer("❌ Пожалуйста, отправьте команду с текстом:\n\n"
                               "/add_yearly_event <название> <день> <месяц> [час] [минута]\n\n"
                               "Пример: /add_yearly_event День_рождения 15 3 12 0\n\n"
                               "💡 Для добавления картинки: отправьте фото с подписью-командой")
            return
        
        # Получаем параметры из команды
        command_text = command_text_raw.split()
        if len(command_text) < 4:
            await message.answer("❌ Использование: /add_yearly_event <название> <день> <месяц> [час] [минута]\n\n"
                               "Пример: /add_yearly_event День_рождения 15 3 12 0\n"
                               "Пример: /add_yearly_event Новый_год 1 1\n\n"
                               "💡 Для добавления картинки: отправьте фото с подписью-командой")
            return
        
        # Извлекаем числовые параметры с конца
        try:
            # Берем последние 4 элемента как числа
            minute = int(command_text[-1]) if len(command_text) > 5 else 0
            hour = int(command_text[-2]) if len(command_text) > 4 else 10
            month = int(command_text[-3])
            day = int(command_text[-4])
            
            # Все остальное - это название события
            name_parts = command_text[1:-4] if len(command_text) > 5 else command_text[1:-2]
            name = ' '.join(name_parts).replace('_', ' ')
            
        except ValueError as e:
            await message.answer(f"❌ Ошибка в параметрах: {e}\n\n"
                               "Убедитесь, что день, месяц, час и минута - это числа\n\n"
                               "Пример: /add_yearly_event С днем улыбок 3 9 6 43")
            return
        
        # Проверяем, есть ли фото в сообщении
        photo_file_id = None
        if message.photo:
            photo_file_id = message.photo[-1].file_id
            logging.info(f"Photo detected for yearly event: {photo_file_id}")
        
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
            
            success = add_yearly_event(name, day, month, hour, minute, f"{name}!", None, photo_file_id)
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
            # Определяем эмодзи для месяца
            month_emojis = {
                1: "❄️", 2: "💝", 3: "🌸", 4: "🌱", 5: "🌺", 6: "☀️",
                7: "🏖️", 8: "🌻", 9: "🍂", 10: "🎃", 11: "🍁", 12: "🎄"
            }
            month_emoji = month_emojis.get(month, "📅")
            
            # Красивое сообщение об успешном добавлении
            success_text = "🎉 **СОБЫТИЕ УСПЕШНО ДОБАВЛЕНО!** 🎉\n"
            success_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            success_text += f"┌─ 🎯 **НОВОЕ СОБЫТИЕ** ─────────────────────┐\n"
            success_text += f"│ 🏷️ Название: **{name}**\n"
            success_text += f"│ {month_emoji} Дата: **{day:02d}.{month:02d}** в **{hour:02d}:{minute:02d}**\n"
            success_text += f"│ 💬 Сообщение: {name}!\n"
            
            # Информация о медиа
            if photo_file_id:
                success_text += f"│ 📷 Картинка: ✅\n"
            else:
                success_text += f"│ 📷 Картинка: ❌\n"
            
            success_text += f"│ 🎵 Музыка: ❌\n"
            success_text += f"│ 🟢 Статус: **Активно**\n"
            success_text += f"└─────────────────────────────────────────┘\n\n"
            success_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            success_text += "💡 Используйте `/list_yearly_events` для просмотра всех событий"
            
            await message.answer(success_text, parse_mode="Markdown")
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
        
        events_text = "🎉 **ЕЖЕГОДНЫЕ СОБЫТИЯ** 🎉\n"
        events_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, event in enumerate(events, 1):
            event_id, name, day, month, hour, minute, message_text, music_url, photo_file_id, is_active, created_at = event
            
            # Определяем эмодзи для месяца
            month_emojis = {
                1: "❄️", 2: "💝", 3: "🌸", 4: "🌱", 5: "🌺", 6: "☀️",
                7: "🏖️", 8: "🌻", 9: "🍂", 10: "🎃", 11: "🍁", 12: "🎄"
            }
            month_emoji = month_emojis.get(month, "📅")
            
            # Красивая карточка события
            events_text += f"┌─ 🎯 **СОБЫТИЕ #{i}** ─────────────────────┐\n"
            events_text += f"│ 🆔 ID: `{event_id}`\n"
            events_text += f"│ 🏷️ Название: **{name}**\n"
            events_text += f"│ {month_emoji} Дата: **{day:02d}.{month:02d}** в **{hour:02d}:{minute:02d}**\n"
            events_text += f"│ 💬 Сообщение: {message_text}\n"
            
            # Добавляем информацию о медиа
            if music_url:
                events_text += f"│ 🎵 Музыка: [Ссылка]({music_url})\n"
            else:
                events_text += f"│ 🎵 Музыка: ❌\n"
                
            if photo_file_id:
                events_text += f"│ 📷 Картинка: ✅\n"
            else:
                events_text += f"│ 📷 Картинка: ❌\n"
            
            # Статус активности
            status_emoji = "🟢" if is_active else "🔴"
            status_text = "Активно" if is_active else "Неактивно"
            events_text += f"│ {status_emoji} Статус: **{status_text}**\n"
            
            events_text += f"└─────────────────────────────────────────┘\n\n"
        
        events_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        events_text += f"📊 **Всего событий:** {len(events)}\n"
        events_text += "💡 Используйте `/delete_yearly_event <ID>` для удаления"
        
        await message.answer(events_text, parse_mode="Markdown")
        
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
            # Красивое сообщение об удалении
            delete_text = "🗑️ **СОБЫТИЕ УДАЛЕНО!** 🗑️\n"
            delete_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            delete_text += f"┌─ 🎯 **УДАЛЕННОЕ СОБЫТИЕ** ─────────────────┐\n"
            delete_text += f"│ 🆔 ID: **{event_id}**\n"
            delete_text += f"│ 🔴 Статус: **Удалено**\n"
            delete_text += f"└─────────────────────────────────────────┘\n\n"
            delete_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            delete_text += "💡 Используйте `/list_yearly_events` для просмотра оставшихся событий"
            
            await message.answer(delete_text, parse_mode="Markdown")
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

# ==================== CALLBACK HANDLERS ====================

@router.callback_query(lambda c: c.data == "main_menu")
async def callback_main_menu(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Главное меню'"""
    try:
        from kb import get_main_menu_keyboard
        from db import save_user
        
        # Сохраняем пользователя в базу данных
        user = callback_query.from_user
        save_user(user.id, user.username or user.first_name)
        
        text = "🎉 **ДОБРО ПОЖАЛОВАТЬ В ГЛАВНОЕ МЕНЮ!** 🎉\n\n"
        text += "Выберите действие из меню ниже:"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in main_menu callback: {e}")
        await callback_query.answer("❌ Ошибка при открытии меню")

@router.callback_query(lambda c: c.data == "list_events")
async def callback_list_events(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Список событий'"""
    try:
        from db import get_yearly_events
        from kb import get_events_list_keyboard, get_back_to_menu_keyboard
        
        events = get_yearly_events()
        
        if not events:
            text = "📅 **ЕЖЕГОДНЫЕ СОБЫТИЯ** 📅\n\n"
            text += "Событий пока нет.\n\n"
            text += "💡 Используйте кнопку 'Добавить событие' для создания нового события."
            
            await callback_query.message.edit_text(
                text=text,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="Markdown"
            )
        else:
            text = f"📅 **ЕЖЕГОДНЫЕ СОБЫТИЯ** 📅\n\n"
            text += f"Найдено событий: **{len(events)}**\n\n"
            text += "Выберите событие для просмотра деталей:"
            
            await callback_query.message.edit_text(
                text=text,
                reply_markup=get_events_list_keyboard(events),
                parse_mode="Markdown"
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in list_events callback: {e}")
        await callback_query.answer("❌ Ошибка при получении списка событий")

@router.callback_query(lambda c: c.data.startswith("event_details_"))
async def callback_event_details(callback_query: types.CallbackQuery):
    """Обработчик просмотра деталей события"""
    try:
        event_id = int(callback_query.data.split("_")[2])
        from db import get_yearly_events
        from kb import get_event_actions_keyboard
        
        events = get_yearly_events()
        event = None
        
        for e in events:
            if e[0] == event_id:
                event = e
                break
        
        if not event:
            await callback_query.answer("❌ Событие не найдено")
            return
        
        event_id, name, day, month, hour, minute, message_text, music_url, photo_file_id, is_active, created_at = event
        
        # Определяем эмодзи для месяца
        month_emojis = {
            1: "❄️", 2: "💝", 3: "🌸", 4: "🌱", 5: "🌺", 6: "☀️",
            7: "🏖️", 8: "🌻", 9: "🍂", 10: "🎃", 11: "🍁", 12: "🎄"
        }
        month_emoji = month_emojis.get(month, "📅")
        
        # Красивая карточка события
        text = "🎯 **ДЕТАЛИ СОБЫТИЯ** 🎯\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"┌─ 🎯 **СОБЫТИЕ #{event_id}** ─────────────────────┐\n"
        text += f"│ 🆔 ID: `{event_id}`\n"
        text += f"│ 🏷️ Название: **{name}**\n"
        text += f"│ {month_emoji} Дата: **{day:02d}.{month:02d}** в **{hour:02d}:{minute:02d}**\n"
        text += f"│ 💬 Сообщение: {message_text}\n"
        
        # Добавляем информацию о медиа
        if music_url:
            text += f"│ 🎵 Музыка: [Ссылка]({music_url})\n"
        else:
            text += f"│ 🎵 Музыка: ❌\n"
            
        if photo_file_id:
            text += f"│ 📷 Картинка: ✅\n"
        else:
            text += f"│ 📷 Картинка: ❌\n"
        
        # Статус активности
        status_emoji = "🟢" if is_active else "🔴"
        status_text = "Активно" if is_active else "Неактивно"
        text += f"│ {status_emoji} Статус: **{status_text}**\n"
        
        text += f"└─────────────────────────────────────────┘\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "Выберите действие:"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_event_actions_keyboard(event_id),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in event_details callback: {e}")
        await callback_query.answer("❌ Ошибка при получении деталей события")

@router.callback_query(lambda c: c.data.startswith("delete_event_"))
async def callback_delete_event(callback_query: types.CallbackQuery):
    """Обработчик кнопки удаления события"""
    try:
        event_id = int(callback_query.data.split("_")[2])
        from kb import get_confirm_delete_keyboard
        
        text = "⚠️ **ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ** ⚠️\n\n"
        text += f"Вы действительно хотите удалить событие **#{event_id}**?\n\n"
        text += "❗ **Это действие нельзя отменить!**"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_confirm_delete_keyboard(event_id),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in delete_event callback: {e}")
        await callback_query.answer("❌ Ошибка при подготовке удаления")

@router.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def callback_confirm_delete(callback_query: types.CallbackQuery):
    """Обработчик подтверждения удаления"""
    try:
        event_id = int(callback_query.data.split("_")[2])
        from db import delete_yearly_event
        from kb import get_back_to_menu_keyboard
        
        success = delete_yearly_event(event_id)
        
        if success:
            text = "🗑️ **СОБЫТИЕ УДАЛЕНО!** 🗑️\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            text += f"┌─ 🎯 **УДАЛЕННОЕ СОБЫТИЕ** ─────────────────┐\n"
            text += f"│ 🆔 ID: **{event_id}**\n"
            text += f"│ 🔴 Статус: **Удалено**\n"
            text += f"└─────────────────────────────────────────┘\n\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "✅ Событие успешно удалено!"
            
            await callback_query.message.edit_text(
                text=text,
                reply_markup=get_back_to_menu_keyboard(),
                parse_mode="Markdown"
            )
            await callback_query.answer("✅ Событие удалено!")
        else:
            await callback_query.answer("❌ Ошибка при удалении события")
        
    except Exception as e:
        logging.error(f"Error in confirm_delete callback: {e}")
        await callback_query.answer("❌ Ошибка при удалении события")

@router.callback_query(lambda c: c.data.startswith("cancel_delete_"))
async def callback_cancel_delete(callback_query: types.CallbackQuery):
    """Обработчик отмены удаления"""
    try:
        event_id = int(callback_query.data.split("_")[2])
        from kb import get_event_actions_keyboard
        
        # Возвращаемся к деталям события
        await callback_event_details(callback_query)
        
    except Exception as e:
        logging.error(f"Error in cancel_delete callback: {e}")
        await callback_query.answer("❌ Ошибка при отмене удаления")

@router.callback_query(lambda c: c.data == "statistics")
async def callback_statistics(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Статистика'"""
    try:
        from kb import get_statistics_keyboard
        
        text = "📊 **СТАТИСТИКА** 📊\n\n"
        text += "Выберите тип статистики:"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_statistics_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in statistics callback: {e}")
        await callback_query.answer("❌ Ошибка при открытии статистики")

@router.callback_query(lambda c: c.data == "general_stats")
async def callback_general_stats(callback_query: types.CallbackQuery):
    """Обработчик общей статистики"""
    try:
        from db import get_video_count, get_total_users, get_yearly_events
        from kb import get_back_to_menu_keyboard
        
        video_count = get_video_count()
        total_users = get_total_users()
        events = get_yearly_events()
        active_events = len([e for e in events if e[9]])  # is_active
        
        text = "📊 **ОБЩАЯ СТАТИСТИКА** 📊\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"┌─ 📈 **ОСНОВНЫЕ ПОКАЗАТЕЛИ** ─────────────────┐\n"
        text += f"│ 🎥 Видеосообщений: **{video_count}**\n"
        text += f"│ 👥 Пользователей: **{total_users}**\n"
        text += f"│ 📅 Всего событий: **{len(events)}**\n"
        text += f"│ 🟢 Активных событий: **{active_events}**\n"
        text += f"│ 🔴 Неактивных событий: **{len(events) - active_events}**\n"
        text += f"└─────────────────────────────────────────┘\n\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "💡 Используйте другие кнопки для детальной статистики"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in general_stats callback: {e}")
        await callback_query.answer("❌ Ошибка при получении статистики")

@router.callback_query(lambda c: c.data == "video_stats")
async def callback_video_stats(callback_query: types.CallbackQuery):
    """Обработчик статистики видео"""
    try:
        from db import get_video_count, get_user_stats
        from kb import get_back_to_menu_keyboard
        
        video_count = get_video_count()
        user_stats = get_user_stats()
        
        text = "🎥 **СТАТИСТИКА ВИДЕО** 🎥\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"┌─ 📹 **ВИДЕОСООБЩЕНИЯ** ─────────────────────┐\n"
        text += f"│ 📊 Всего видео: **{video_count}**\n"
        text += f"└─────────────────────────────────────────┘\n\n"
        
        if user_stats:
            text += "┌─ 👥 **ТОП ПОЛЬЗОВАТЕЛЕЙ** ───────────────────┐\n"
            for i, (username, count) in enumerate(user_stats[:5], 1):
                text += f"│ {i}. {username}: **{count}** видео\n"
            text += f"└─────────────────────────────────────────┘\n\n"
        else:
            text += "┌─ 👥 **ПОЛЬЗОВАТЕЛИ** ───────────────────────┐\n"
            text += f"│ 📊 Пока нет данных\n"
            text += f"└─────────────────────────────────────────┘\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "💡 Отправляйте видеосообщения для пополнения статистики!"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in video_stats callback: {e}")
        await callback_query.answer("❌ Ошибка при получении статистики видео")

@router.callback_query(lambda c: c.data == "events_stats")
async def callback_events_stats(callback_query: types.CallbackQuery):
    """Обработчик статистики событий"""
    try:
        from db import get_yearly_events
        from kb import get_back_to_menu_keyboard
        
        events = get_yearly_events()
        active_events = [e for e in events if e[9]]  # is_active
        
        # Статистика по месяцам
        month_stats = {}
        for event in active_events:
            month = event[3]  # month
            month_names = {
                1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
                5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
                9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
            }
            month_name = month_names.get(month, f"Месяц {month}")
            month_stats[month_name] = month_stats.get(month_name, 0) + 1
        
        text = "📅 **СТАТИСТИКА СОБЫТИЙ** 📅\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"┌─ 📊 **ОБЩАЯ ИНФОРМАЦИЯ** ─────────────────┐\n"
        text += f"│ 📈 Всего событий: **{len(events)}**\n"
        text += f"│ 🟢 Активных: **{len(active_events)}**\n"
        text += f"│ 🔴 Неактивных: **{len(events) - len(active_events)}**\n"
        text += f"└─────────────────────────────────────────┘\n\n"
        
        if month_stats:
            text += "┌─ 📆 **СОБЫТИЯ ПО МЕСЯЦАМ** ───────────────┐\n"
            for month, count in sorted(month_stats.items()):
                text += f"│ {month}: **{count}** событий\n"
            text += f"└─────────────────────────────────────────┘\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "💡 Добавляйте больше событий для разнообразия!"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in events_stats callback: {e}")
        await callback_query.answer("❌ Ошибка при получении статистики событий")

@router.callback_query(lambda c: c.data == "user_stats")
async def callback_user_stats(callback_query: types.CallbackQuery):
    """Обработчик статистики пользователей"""
    try:
        from db import get_user_stats, get_total_users
        from kb import get_back_to_menu_keyboard
        
        total_users = get_total_users()
        user_stats = get_user_stats()
        
        text = "👥 **СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ** 👥\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"┌─ 📊 **ОБЩАЯ ИНФОРМАЦИЯ** ─────────────────┐\n"
        text += f"│ 👤 Всего пользователей: **{total_users}**\n"
        text += f"└─────────────────────────────────────────┘\n\n"
        
        if user_stats:
            text += "┌─ 🏆 **ТОП ПОЛЬЗОВАТЕЛЕЙ ПО ВИДЕО** ───────┐\n"
            for i, (username, count) in enumerate(user_stats[:10], 1):
                # Добавляем эмодзи для топ-3
                if i == 1:
                    emoji = "🥇"
                elif i == 2:
                    emoji = "🥈"
                elif i == 3:
                    emoji = "🥉"
                else:
                    emoji = f"{i}."
                
                text += f"│ {emoji} {username}: **{count}** видео\n"
            text += f"└─────────────────────────────────────────┘\n\n"
            
            # Статистика активности
            total_videos = sum(count for _, count in user_stats)
            avg_videos = total_videos / len(user_stats) if user_stats else 0
            
            text += "┌─ 📈 **СТАТИСТИКА АКТИВНОСТИ** ───────────┐\n"
            text += f"│ 📊 Всего видео от пользователей: **{total_videos}**\n"
            text += f"│ 📈 Среднее видео на пользователя: **{avg_videos:.1f}**\n"
            text += f"│ 👥 Пользователей с видео: **{len(user_stats)}**\n"
            text += f"└─────────────────────────────────────────┘\n\n"
        else:
            text += "┌─ 📊 **АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЕЙ** ─────────┐\n"
            text += f"│ 📹 Пока никто не отправлял видео\n"
            text += f"│ 💡 Отправьте видеосообщение для начала!\n"
            text += f"└─────────────────────────────────────────┘\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "💡 Отправляйте больше видео для пополнения статистики!"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in user_stats callback: {e}")
        await callback_query.answer("❌ Ошибка при получении статистики пользователей")

@router.callback_query(lambda c: c.data == "add_event")
async def callback_add_event(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Добавить событие'"""
    try:
        from kb import get_back_to_menu_keyboard
        
        text = "➕ **ДОБАВЛЕНИЕ СОБЫТИЯ** ➕\n\n"
        text += "Для добавления нового события используйте команду:\n\n"
        text += "`/add_yearly_event <название> <день> <месяц> [час] [минута]`\n\n"
        text += "**Примеры:**\n"
        text += "• `/add_yearly_event День_рождения 15 3 12 0`\n"
        text += "• `/add_yearly_event Новый_год 1 1`\n\n"
        text += "💡 **Совет:** Отправьте фото с подписью-командой для добавления картинки к событию!"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in add_event callback: {e}")
        await callback_query.answer("❌ Ошибка при открытии добавления события")

@router.callback_query(lambda c: c.data == "help")
async def callback_help(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Помощь'"""
    try:
        from kb import get_back_to_menu_keyboard
        
        text = "❓ **ПОМОЩЬ** ❓\n\n"
        text += "**Основные команды:**\n\n"
        text += "📅 **События:**\n"
        text += "• `/add_yearly_event` - добавить событие\n"
        text += "• `/list_yearly_events` - список событий\n"
        text += "• `/delete_yearly_event <ID>` - удалить событие\n\n"
        text += "🎥 **Видео:**\n"
        text += "• `/random_video` - случайное видео\n"
        text += "• `/video_stats` - статистика видео\n\n"
        text += "⚙️ **Админ:**\n"
        text += "• `/init_db` - инициализация БД\n"
        text += "• `/reset_db` - сброс БД\n\n"
        text += "💡 **Совет:** Используйте кнопки меню для удобной навигации!"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in help callback: {e}")
        await callback_query.answer("❌ Ошибка при открытии помощи")

@router.callback_query(lambda c: c.data == "settings")
async def callback_settings(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Настройки'"""
    try:
        from kb import get_back_to_menu_keyboard
        
        text = "⚙️ **НАСТРОЙКИ** ⚙️\n\n"
        text += "**Доступные настройки:**\n\n"
        text += "🕐 **Время напоминаний:**\n"
        text += "• Ежедневные воспоминания: 09:00\n"
        text += "• Ежегодные события: по расписанию\n\n"
        text += "🎵 **Медиа настройки:**\n"
        text += "• Автосохранение видео: ✅\n"
        text += "• Поддержка картинок: ✅\n"
        text += "• Поддержка музыки: ✅\n\n"
        text += "🌍 **Часовой пояс:**\n"
        text += "• Текущий: Москва (UTC+3)\n\n"
        text += "📊 **База данных:**\n"
        text += "• Статус: ✅ Активна\n"
        text += "• Путь: `/tmp/bot_database.db`\n\n"
        text += "💡 **Для изменения настроек используйте команды:**\n"
        text += "• `/init_db` - пересоздать БД\n"
        text += "• `/reset_db` - сбросить БД"
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=get_back_to_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback_query.answer()
        
    except Exception as e:
        logging.error(f"Error in settings callback: {e}")
        await callback_query.answer("❌ Ошибка при открытии настроек")
