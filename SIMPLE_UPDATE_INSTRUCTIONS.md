# 🎤 Простое обновление голосовых сообщений

## 📋 **Что нужно сделать на сервере:**

### **1. Создайте файл speech_kit.py:**
```bash
nano speech_kit.py
```

### **2. Скопируйте и вставьте этот код:**
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

### **3. Сохраните файл:**
- Нажмите `Ctrl + X`
- Нажмите `Y`
- Нажмите `Enter`

### **4. Обновите config.py:**
```bash
nano config.py
```

### **5. Добавьте в конец файла:**
```python
# Настройки голосовых сообщений
VOICE_ENABLED = True  # Включены ли голосовые сообщения
VOICE_LANGUAGE = "ru-RU"  # Язык для распознавания и синтеза речи
VOICE_GENDER = "male"  # Пол голоса (male/female)
VOICE_EMOTION = "evil"  # Эмоция голоса (neutral, good, evil, mixed)
VOICE_SPEED = "1.0"  # Скорость речи (0.1-3.0)
VOICE_FORMAT = "oggopus"  # Формат аудио (oggopus, mp3, wav, lpcm)
```

### **6. Обновите handlers.py:**
```bash
nano handlers.py
```

### **7. Найдите строку 7:**
```python
from config import AI_ENABLED
```

### **8. Замените на:**
```python
from config import AI_ENABLED, VOICE_ENABLED
import speech_kit
```

### **9. Найдите строку с общим обработчиком (примерно 1326):**
```python
# AI-чат обработчик текстовых сообщений
@router.message()
async def handle_ai_message(message: types.Message):
```

### **10. Добавьте ПЕРЕД этой строкой:**
```python
# AI-чат обработчик голосовых сообщений
@router.message(lambda message: message.voice is not None)
async def handle_voice_message(message: types.Message):
    """
    Обработчик для AI-чата - отвечает на голосовые сообщения
    """
    try:
        # Проверяем, включен ли AI и голосовые сообщения
        if not AI_ENABLED or not VOICE_ENABLED:
            return
            
        # Получаем информацию о пользователе
        username = message.from_user.username or message.from_user.first_name or "Пользователь"
        chat_id = str(message.chat.id)
        
        logging.info(f"Processing voice message from {username}")
        
        # Скачиваем голосовое сообщение
        voice_file = await message.bot.get_file(message.voice.file_id)
        voice_data = await message.bot.download_file(voice_file.file_path)
        
        # Преобразуем голос в текст
        text_from_voice = speech_kit.voice_to_text(voice_data.read())
        
        if not text_from_voice:
            logging.warning("Failed to convert voice to text")
            return
            
        logging.info(f"Voice converted to text: {text_from_voice[:50]}...")
        
        # Проверяем, должен ли AI ответить
        if yandex_ai.should_respond(text_from_voice, chat_id):
            logging.info(f"AI responding to voice message from {username}")
            
            # Генерируем ответ
            ai_response = yandex_ai.generate_response(text_from_voice, chat_id, username)
            
            if ai_response:
                # Преобразуем ответ в голос
                voice_response = speech_kit.text_to_voice(ai_response)
                
                if voice_response:
                    # Отправляем голосовой ответ
                    await message.answer_voice(
                        voice=voice_response,
                        caption=f"🎤 {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}"
                    )
                    logging.info(f"AI voice response sent: {ai_response[:50]}...")
                else:
                    # Если не удалось создать голос, отправляем текстом
                    await message.answer(f"🎤 {ai_response}")
                    logging.info(f"AI text response sent (voice failed): {ai_response[:50]}...")
            else:
                # Fallback ответ
                fallback_response = yandex_ai.get_random_comment()
                voice_fallback = speech_kit.text_to_voice(fallback_response)
                
                if voice_fallback:
                    await message.answer_voice(voice=voice_fallback)
                else:
                    await message.answer(fallback_response)
                    
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")

```

### **11. Перезапустите бота:**
```bash
docker-compose down
docker-compose up --build -d
```

## 🎤 **Готово!**

Теперь бот будет отвечать на голосовые сообщения грубым мужским голосом! 🗣️✨
