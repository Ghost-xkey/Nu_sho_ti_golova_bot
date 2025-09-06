import os

TOKEN = os.getenv('TOKEN', '')
DB_PATH = os.getenv('DB_PATH', '/app/data/bot_database.db')  # Файловая база данных в Docker volume
CHAT_ID = os.getenv('CHAT_ID', '')

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

# Настройки AI-чата
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")  # API ключ YandexGPT (не хранить в гите)
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "b1gr16qlpg0u8bo2h5eg")  # Folder ID проекта

# Настройки Кинопоиска
KINOPOISK_API_TOKEN = os.getenv("KINOPOISK_API_TOKEN", "PVB3DPY-4E7MSX5-Q1SEQPV-J5KXG8T")

# Настройки AI поведения
AI_ENABLED = True  # Включен ли AI-чат
AI_RESPONSE_CHANCE = 0.1  # Вероятность случайного ответа (10%)
AI_MAX_RESPONSES_PER_HOUR = 20  # Максимум ответов в час

# Настройки голосовых сообщений
VOICE_ENABLED = True  # Включены ли голосовые сообщения
VOICE_LANGUAGE = "ru-RU"  # Язык для распознавания и синтеза речи
VOICE_GENDER = "male"  # Пол голоса (male/female)
VOICE_EMOTION = "evil"  # Эмоция голоса (neutral, good, evil, mixed)
VOICE_SPEED = "1.0"  # Скорость речи (0.1-3.0)
VOICE_FORMAT = "oggopus"  # Формат аудио (oggopus, mp3, wav, lpcm)
VOICE_NAME = "zahar"  # Имя конкретного голоса (например: "zahar", "ermil", "alena"). Если указано, перекрывает VOICE_GENDER

# Настройки лексики
ALLOW_PROFANITY = True  # Разрешать крепкую лексику (без хейта/дискриминации/угроз)
PROFANITY_LEVEL = "hard"  # Уровень: mild | medium | hard
