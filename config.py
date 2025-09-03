TOKEN = '7255987005:AAEMSy4B0zWvJcH5RoJas9o4pEYvPMA__0g'
DB_PATH = 'bot_database.db'
CHAT_ID = '-1002512455884'

# Настройки времени отправки воспоминаний
MEMORY_HOUR = 9  # Час отправки (0-23)
MEMORY_MINUTE = 0  # Минута отправки (0-59)

# Настройки ежегодного напоминания (3 сентября)
YEARLY_DAY = 3
YEARLY_MONTH = 9
YEARLY_HOUR = 10
YEARLY_MINUTE = 0
YEARLY_MESSAGE = "Ну шо вы головешки, календарь перевернули?"
YANDEX_TRACK_URL = "https://music.yandex.ru/track/52010356"
# Картинка для ежегодного сообщения
YEARLY_PHOTO_FILE_ID = None  # file_id картинки

def update_yearly_photo(file_id):
    """Обновляет file_id картинки для ежегодного сообщения"""
    global YEARLY_PHOTO_FILE_ID
    YEARLY_PHOTO_FILE_ID = file_id
    print(f"Yearly photo updated: {file_id}")

def remove_yearly_photo():
    """Удаляет картинку для ежегодного сообщения"""
    global YEARLY_PHOTO_FILE_ID
    YEARLY_PHOTO_FILE_ID = None
    print("Yearly photo removed")

def get_yearly_photo():
    """Возвращает file_id картинки для ежегодного сообщения"""
    return YEARLY_PHOTO_FILE_ID
