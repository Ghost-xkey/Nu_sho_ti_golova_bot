import requests
import json
import random
import logging
from typing import Optional, List
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

class YandexGPT:
    def __init__(self):
        self.api_key = YANDEX_API_KEY
        self.folder_id = YANDEX_FOLDER_ID
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.chat_history = {}  # Храним историю диалогов для каждого чата
        
    def get_headers(self):
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def should_respond(self, message_text: str, chat_id: str) -> bool:
        """
        Определяет, должен ли AI ответить на сообщение
        """
        message_lower = message_text.lower()
        
        # Прямые обращения к боту
        bot_mentions = ["бот", "ai", "ии", "помощник", "ассистент"]
        if any(mention in message_lower for mention in bot_mentions):
            return True
            
        # Эмоциональные сигналы
        emotional_signals = ["скучно", "грустно", "устал", "плохо", "отлично", "круто", "весело"]
        if any(signal in message_lower for signal in emotional_signals):
            return True
            
        # Вопросы
        if "?" in message_text:
            return True
            
        # Случайные ответы (10% вероятность)
        if random.random() < 0.1:
            return True
            
        return False
    
    def get_chat_context(self, chat_id: str, limit: int = 5) -> str:
        """
        Получает контекст последних сообщений в чате
        """
        if chat_id not in self.chat_history:
            return ""
            
        recent_messages = self.chat_history[chat_id][-limit:]
        context = "\n".join([f"Пользователь: {msg}" for msg in recent_messages])
        return context
    
    def add_to_history(self, chat_id: str, message: str):
        """
        Добавляет сообщение в историю чата
        """
        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = []
            
        self.chat_history[chat_id].append(message)
        
        # Ограничиваем историю последними 20 сообщениями
        if len(self.chat_history[chat_id]) > 20:
            self.chat_history[chat_id] = self.chat_history[chat_id][-20:]
    
    def generate_response(self, message_text: str, chat_id: str, username: str = None) -> Optional[str]:
        """
        Генерирует ответ AI на основе сообщения
        """
        try:
            # Добавляем сообщение в историю
            self.add_to_history(chat_id, message_text)
            
            # Получаем контекст
            context = self.get_chat_context(chat_id)
            
            # Формируем промпт
            system_prompt = """Ты - дружелюбный AI-помощник в Telegram группе из трех друзей. 
Твоя задача - естественно участвовать в разговорах, поддерживать беседу, шутить и создавать позитивную атмосферу.

Правила:
- Отвечай коротко и естественно (1-2 предложения)
- Будь дружелюбным и позитивным
- Иногда шути и добавляй эмодзи
- Поддерживай разговоры между друзьями
- Не упоминай, что ты AI или бот
- Говори на "ты" и неформально
- Иногда предлагай идеи для видео или творчества

Стиль общения: дружеский, веселый, поддерживающий."""

            user_prompt = f"Контекст последних сообщений:\n{context}\n\nТекущее сообщение: {message_text}"
            
            if username:
                user_prompt += f"\nОт пользователя: {username}"
            
            # Подготавливаем данные для API
            data = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": 150
                },
                "messages": [
                    {
                        "role": "system",
                        "text": system_prompt
                    },
                    {
                        "role": "user", 
                        "text": user_prompt
                    }
                ]
            }
            
            # Отправляем запрос к YandexGPT
            response = requests.post(
                self.base_url,
                headers=self.get_headers(),
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["result"]["alternatives"][0]["message"]["text"]
                
                # Добавляем ответ в историю
                self.add_to_history(chat_id, f"AI: {ai_response}")
                
                return ai_response
            else:
                logging.error(f"YandexGPT API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return None
    
    def get_random_comment(self) -> str:
        """
        Возвращает случайный комментарий для разнообразия
        """
        comments = [
            "Интересно! 🤔",
            "Понятно! 👍",
            "Круто! 😎",
            "Хм, а что если... 💡",
            "Да, согласен! 😊",
            "Интересная мысль! 🤓",
            "Ага, понял! 👌",
            "Хорошая идея! ✨"
        ]
        return random.choice(comments)

# Глобальный экземпляр AI
yandex_ai = YandexGPT()
