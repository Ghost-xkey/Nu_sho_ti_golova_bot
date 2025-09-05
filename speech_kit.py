import requests
import json
import logging
import io
import base64
from config import (
    YANDEX_API_KEY, YANDEX_FOLDER_ID, 
    VOICE_ENABLED, VOICE_LANGUAGE, VOICE_GENDER, 
    VOICE_EMOTION, VOICE_SPEED, VOICE_FORMAT, VOICE_NAME
)

class YandexSpeechKit:
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.folder_id = YANDEX_FOLDER_ID
        self.stt_url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        self.tts_url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        
    def get_headers(self):
        return {
            "Authorization": f"Api-Key {self.api_key}"
        }
    
    def voice_to_text(self, voice_data: bytes) -> str:
        """
        Преобразует голосовое сообщение в текст (сырое бинарное OGG/OPUS)
        Отправляем бинарные данные напрямую с query-параметрами, как в официальных примерах.
        """
        try:
            if not VOICE_ENABLED:
                logging.warning("Voice processing is disabled")
                return ""

            # Формируем параметры запроса согласно API: https://stt.api.cloud.yandex.net/speech/v1/stt:recognize
            params = {
                "lang": VOICE_LANGUAGE,          # например, ru-RU
                "folderId": self.folder_id,
                "format": "oggopus",           # формат телеграм-голосовых
                "profanityFilter": "false"
            }

            # Для бинарной загрузки НЕ указываем Content-Type: application/json
            headers = {
                "Authorization": f"Api-Key {self.api_key}"
            }

            response = requests.post(
                self.stt_url,
                headers=headers,
                params=params,
                data=voice_data,   # сырое бинарное содержимое файла
                timeout=15
            )

            if response.status_code == 200:
                try:
                    result = response.json()
                except Exception as e:
                    logging.error(f"STT invalid JSON: {e} - {response.text[:200]}")
                    return ""

                # Обработка ошибок в теле ответа
                if isinstance(result, dict) and ("error_code" in result or "error_message" in result):
                    logging.error(f"STT error payload: {result}")
                    return ""

                # Универсальный парсинг текста
                recognized_text = ""
                if isinstance(result, dict):
                    if "result" in result:
                        res = result["result"]
                        if isinstance(res, dict):
                            # Формат: {"result": {"alternatives": [{"text": "..."}]}}
                            alternatives = res.get("alternatives")
                            if isinstance(alternatives, list) and len(alternatives) > 0:
                                first_alt = alternatives[0] or {}
                                recognized_text = (first_alt.get("text") or "").strip()
                            else:
                                # Иногда текст может быть напрямую в поле text
                                recognized_text = (res.get("text") or "").strip()
                        elif isinstance(res, str):
                            # Формат: {"result": "..."}
                            recognized_text = res.strip()
                    elif "text" in result and isinstance(result["text"], str):
                        # Формат: {"text": "..."}
                        recognized_text = result["text"].strip()

                if recognized_text:
                    logging.info(f"Voice-to-text OK: {recognized_text[:50]}...")
                    return recognized_text

                logging.warning("No text found in voice recognition result")
                return ""
            else:
                logging.error(f"STT API error: {response.status_code} - {response.text}")
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
                
            # Выбираем имя голоса: приоритет VOICE_NAME, иначе по полу
            if VOICE_NAME and isinstance(VOICE_NAME, str) and VOICE_NAME.strip():
                voice_name = VOICE_NAME.strip()
            else:
                voice_name = "filipp" if VOICE_GENDER == "male" else "jane"
            
            # Подготавливаем данные для API (urlencoded form)
            data = {
                "text": text,
                "lang": VOICE_LANGUAGE,
                "voice": voice_name,
                "speed": VOICE_SPEED,
                "format": VOICE_FORMAT,
                "folderId": self.folder_id
            }

            # Эмоция поддерживается не всеми голосами. Добавляем только если безопасно.
            safe_emotion_voices = {"jane", "filipp"}
            if VOICE_EMOTION and VOICE_EMOTION != "neutral" and voice_name in safe_emotion_voices:
                data["emotion"] = VOICE_EMOTION

            headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # Отправляем запрос к Text-to-Speech API
            response = requests.post(
                self.tts_url,
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                audio_data = response.content
                logging.info(f"TTS OK: {text[:50]}...")
                return audio_data
            else:
                logging.error(f"TTS API error: {response.status_code} - {response.text}")
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
