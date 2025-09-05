from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Привет")]],
        resize_keyboard=True
    )
    return keyboard

def get_main_menu_keyboard():
    """Главное меню с основными функциями"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="➕ Добавить событие",
        callback_data="add_event"
    ))
    builder.add(InlineKeyboardButton(
        text="📅 Список событий",
        callback_data="list_events"
    ))
    builder.add(InlineKeyboardButton(
        text="📊 Статистика",
        callback_data="statistics"
    ))
    builder.add(InlineKeyboardButton(
        text="🎥 Видео статистика",
        callback_data="video_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="⚙️ Настройки",
        callback_data="settings"
    ))
    builder.add(InlineKeyboardButton(
        text="❓ Помощь",
        callback_data="help"
    ))
    
    # Располагаем кнопки по 2 в ряд
    builder.adjust(2, 2, 2)
    
    return builder.as_markup()

def get_event_actions_keyboard(event_id: int):
    """Клавиатура с действиями для конкретного события"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="✏️ Редактировать",
        callback_data=f"edit_event_{event_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="📋 Дублировать",
        callback_data=f"duplicate_event_{event_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🗑️ Удалить",
        callback_data=f"delete_event_{event_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔄 Включить/Выключить",
        callback_data=f"toggle_event_{event_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад к списку",
        callback_data="list_events"
    ))
    
    # Располагаем кнопки по 2 в ряд
    builder.adjust(2, 2, 1)
    
    return builder.as_markup()

def get_confirm_delete_keyboard(event_id: int):
    """Клавиатура подтверждения удаления"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="✅ Да, удалить",
        callback_data=f"confirm_delete_{event_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data=f"cancel_delete_{event_id}"
    ))
    
    return builder.as_markup()

def get_back_to_menu_keyboard():
    """Простая клавиатура с кнопкой 'Назад'"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="main_menu"
    ))
    
    return builder.as_markup()

def get_events_list_keyboard(events):
    """Клавиатура со списком событий"""
    builder = InlineKeyboardBuilder()
    
    for event in events:
        event_id, name, day, month, hour, minute, message_text, music_url, photo_file_id, is_active, created_at = event
        
        # Определяем эмодзи для месяца
        month_emojis = {
            1: "❄️", 2: "💝", 3: "🌸", 4: "🌱", 5: "🌺", 6: "☀️",
            7: "🏖️", 8: "🌻", 9: "🍂", 10: "🎃", 11: "🍁", 12: "🎄"
        }
        month_emoji = month_emojis.get(month, "📅")
        
        # Статус активности
        status_emoji = "🟢" if is_active else "🔴"
        
        button_text = f"{status_emoji} {name} {month_emoji} {day:02d}.{month:02d}"
        
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"event_details_{event_id}"
        ))
    
    builder.add(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="main_menu"
    ))
    
    # Располагаем кнопки по 1 в ряд для лучшей читаемости
    builder.adjust(1)
    
    return builder.as_markup()

def get_statistics_keyboard():
    """Клавиатура для статистики"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="📊 Общая статистика",
        callback_data="general_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="👥 Статистика пользователей",
        callback_data="user_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="🎥 Статистика видео",
        callback_data="video_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="📅 Статистика событий",
        callback_data="events_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="main_menu"
    ))
    
    # Располагаем кнопки по 2 в ряд
    builder.adjust(2, 2, 1)
    
    return builder.as_markup()

def get_profanity_settings_keyboard(enabled: bool, level: str):
    """Клавиатура управления 'жёстким режимом'"""
    builder = InlineKeyboardBuilder()

    # Кнопка переключения
    toggle_text = "🟢 Мат: Вкл" if enabled else "⚪ Мат: Выкл"
    builder.add(InlineKeyboardButton(
        text=toggle_text,
        callback_data="profanity_toggle"
    ))

    # Кнопки уровней
    lvl = (level or "").lower()
    def label(name: str) -> str:
        return f"✅ {name}" if lvl == name else name

    builder.add(InlineKeyboardButton(text=label("mild"), callback_data="profanity_level_mild"))
    builder.add(InlineKeyboardButton(text=label("medium"), callback_data="profanity_level_medium"))
    builder.add(InlineKeyboardButton(text=label("hard"), callback_data="profanity_level_hard"))

    # Назад в меню
    builder.add(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="main_menu"
    ))

    builder.adjust(1, 3, 1)
    return builder.as_markup()
