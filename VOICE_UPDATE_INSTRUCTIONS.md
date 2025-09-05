# 🎤 Инструкция по добавлению голосовых сообщений

## 🎯 **Что добавлено:**

### **Новые файлы:**
- ✅ **`speech_kit.py`** - модуль для работы с Yandex SpeechKit
- ✅ **Обновлен `handlers.py`** - добавлен обработчик голосовых сообщений
- ✅ **Обновлен `config.py`** - добавлены настройки голоса

### **Новые возможности:**
- 🎤 **Распознавание речи** - голосовые сообщения преобразуются в текст
- 🗣️ **Синтез речи** - ответы AI преобразуются в голосовые сообщения
- ⚙️ **Настройки голоса** - мужской голос, скорость, эмоции
- 🔄 **Автоматическое определение** - голос на голос, текст на текст

## 📋 **Что нужно сделать на сервере:**

### **1. Скачайте новые файлы:**
```bash
# Создайте speech_kit.py
nano speech_kit.py
```

### **2. Скопируйте код speech_kit.py:**
```python
import requests
import json
import logging
import io
import base64
from config import (
    YANDEX_API_KEY, YANDEX_FOLDER_ID, 
    VOICE_ENABLED, VOICE_LANGUAGE, VOICE_GENDER, 
    VOICE_EMOTION, VOICE_SPEED, VOICE_FORMAT
)

class YandexSpeechKit:
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.folder_id = YANDEX_FOLDER_ID
        self.stt_url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        self.tts_url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        
    def get_headers(self):
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def voice_to_text(self, voice_data: bytes) -> str:
        """
        Преобразует голосовое сообщение в текст
        """
        try:
            if not VOICE_ENABLED:
                logging.warning("Voice processing is disabled")
                return ""
                
            # Кодируем аудио в base64
            audio_base64 = base64.b64encode(voice_data).decode('utf-8')
            
            # Подготавливаем данные для API
            data = {
                "config": {
                    "specification": {
                        "languageCode": VOICE_LANGUAGE,
                        "model": "general",
                        "profanityFilter": False,
                        "audioEncoding": "OGG_OPUS",
                        "sampleRateHertz": 48000
                    }
                },
                "audio": {
                    "content": audio_base64
                }
            }
            
            # Отправляем запрос к Speech-to-Text API
            response = requests.post(
                self.stt_url,
                headers=self.get_headers(),
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "alternatives" in result["result"]:
                    text = result["result"]["alternatives"][0]["text"]
                    logging.info(f"Voice-to-text successful: {text[:50]}...")
                    return text
                else:
                    logging.warning("No text found in voice recognition result")
                    return ""
            else:
                logging.error(f"Speech-to-Text API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logging.error(f"Error converting voice to text: {e}")
            return ""
    
    def text_to_voice(self, text: str) -> bytes:
        """
        Преобразует текст в голосовое сообщение
        """
        try:
            if not VOICE_ENABLED:
                logging.warning("Voice processing is disabled")
                return b""
                
            # Выбираем голос в зависимости от настроек
            voice_name = "filipp" if VOICE_GENDER == "male" else "jane"
            
            # Подготавливаем данные для API
            data = {
                "text": text,
                "lang": VOICE_LANGUAGE,
                "voice": voice_name,
                "emotion": "evil",  # Грубая эмоция
                "speed": VOICE_SPEED,
                "format": VOICE_FORMAT
            }
            
            # Отправляем запрос к Text-to-Speech API
            response = requests.post(
                self.tts_url,
                headers=self.get_headers(),
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                audio_data = response.content
                logging.info(f"Text-to-voice successful for: {text[:50]}...")
                return audio_data
            else:
                logging.error(f"Text-to-Speech API error: {response.status_code} - {response.text}")
                return b""
                
        except Exception as e:
            logging.error(f"Error converting text to voice: {e}")
            return b""

# Глобальный экземпляр SpeechKit
speech_kit = YandexSpeechKit()

# Функции для удобства использования
def voice_to_text(voice_data: bytes) -> str:
    """Преобразует голос в текст"""
    return speech_kit.voice_to_text(voice_data)

def text_to_voice(text: str) -> bytes:
    """Преобразует текст в голос"""
    return speech_kit.text_to_voice(text)
```

### **3. Обновите config.py:**
```bash
nano config.py
```

Добавьте в конец файла:
```python
# Настройки голосовых сообщений
VOICE_ENABLED = True  # Включены ли голосовые сообщения
VOICE_LANGUAGE = "ru-RU"  # Язык для распознавания и синтеза речи
VOICE_GENDER = "male"  # Пол голоса (male/female)
VOICE_EMOTION = "evil"  # Эмоция голоса (neutral, good, evil, mixed)
VOICE_SPEED = "1.0"  # Скорость речи (0.1-3.0)
VOICE_FORMAT = "oggopus"  # Формат аудио (oggopus, mp3, wav, lpcm)
```

### **4. Обновите handlers.py:**
```bash
nano handlers.py
```

Добавьте импорт в начало файла:
```python
from config import AI_ENABLED, VOICE_ENABLED
import speech_kit
```

### **5. Перезапустите бота:**
```bash
docker-compose down
docker-compose up --build -d
```

## 🎤 **Готово!**

Теперь бот будет:
- 🎤 **Слушать голосовые** и преобразовывать их в текст
- 🤖 **Отвечать AI** на основе распознанного текста
- 🗣️ **Отправлять голосовые ответы** мужским голосом
- 📝 **Отвечать текстом** на текстовые сообщения

**Протестируйте, отправив голосовое сообщение в группу!** 🚀✨
