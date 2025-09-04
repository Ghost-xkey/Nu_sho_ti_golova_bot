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
            
            # Пробуем разные форматы аудио
            audio_formats = [
                {
                    "audioEncoding": "OGG_OPUS",
                    "sampleRateHertz": 48000,
                    "data": voice_data
                },
                {
                    "audioEncoding": "LINEAR16_PCM", 
                    "sampleRateHertz": 16000,
                    "data": voice_data
                },
                {
                    "audioEncoding": "MP3",
                    "sampleRateHertz": 44100,
                    "data": voice_data
                }
            ]
            
            for audio_format in audio_formats:
                try:
                    # Кодируем аудио в base64
                    audio_base64 = base64.b64encode(audio_format["data"]).decode('utf-8')
                    
                    # Подготавливаем данные для API
                    data = {
                        "config": {
                            "specification": {
                                "languageCode": VOICE_LANGUAGE,
                                "model": "general",
                                "profanityFilter": False,
                                "audioEncoding": audio_format["audioEncoding"],
                                "sampleRateHertz": audio_format["sampleRateHertz"]
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
                            logging.info(f"Voice-to-text successful with {audio_format['audioEncoding']}: {text[:50]}...")
                            return text
                        else:
                            logging.warning(f"No text found with {audio_format['audioEncoding']}")
                            continue
                    else:
                        logging.warning(f"Speech-to-Text API error with {audio_format['audioEncoding']}: {response.status_code} - {response.text}")
                        continue
                        
                except Exception as format_error:
                    logging.warning(f"Error with {audio_format['audioEncoding']}: {format_error}")
                    continue
            
            # Если ни один формат не сработал
            logging.error("All audio formats failed for voice recognition")
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
