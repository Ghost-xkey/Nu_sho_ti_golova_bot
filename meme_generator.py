import requests
import random
import logging
from typing import Optional, Dict, List

class MemeGenerator:
    def __init__(self):
        # Imgflip API credentials (можно получить на https://imgflip.com/api)
        self.api_url = "https://api.imgflip.com"
        self.username = "moskva2255@mail.ru"
        self.password = "%hQ$c5*6x.m5G3s"
        
        # Популярные мем-шаблоны с их ID
        self.meme_templates = {
            "drake": 181913649,  # Drake pointing
            "distracted_boyfriend": 112126428,  # Distracted boyfriend
            "woman_yelling_at_cat": 188390779,  # Woman yelling at cat
            "two_buttons": 87743020,  # Two buttons
            "change_my_mind": 129242436,  # Change my mind
            "expanding_brain": 93895088,  # Expanding brain
            "this_is_fine": 55311130,  # This is fine
            "stefan": 61579,  # Stefan Karlsson
            "hide_the_pain": 27813981,  # Hide the pain
            "doge": 8072285,  # Doge
            "grumpy_cat": 405658,  # Grumpy cat
            "success_kid": 61520,  # Success kid
            "bad_luck_brian": 61585,  # Bad luck Brian
            "first_world_problems": 61532,  # First world problems
            "y_u_no": 61527,  # Y U No
            "trollface": 61539,  # Trollface
            "forever_alone": 61533,  # Forever alone
            "fry": 61520,  # Not sure if
            "all_the_things": 61579,  # X all the things
            "one_does_not_simply": 61579,  # One does not simply
        }
        
        # Персональные мемы для участников чата
        self.personal_memes = {
            "vadik": {
                "templates": ["drake", "two_buttons", "expanding_brain"],
                "texts": [
                    ("Рыбалка", "Друзья"),
                    ("Купить катер", "Сделать ремонт в доме"),
                    ("Бросить курить", "Продолжить курить"),
                    ("Ездить на октахе", "Мечтать о катере"),
                ]
            },
            "leha": {
                "templates": ["drake", "distracted_boyfriend", "woman_yelling_at_cat"],
                "texts": [
                    ("Кальян", "BMW"),
                    ("Жить в Никеле", "Видеть солнце"),
                    ("Ходить пешком", "Ездить на BMW"),
                    ("Вискарь с колой", "Здоровый образ жизни"),
                ]
            },
            "profanity": {
                "templates": ["woman_yelling_at_cat", "this_is_fine", "trollface"],
                "texts": [
                    ("Мат", "Вежливость"),
                    ("Ругаться", "Молчать"),
                    ("Агрессия", "Спокойствие"),
                ]
            },
            "jokes": {
                "templates": ["expanding_brain", "two_buttons", "drake"],
                "texts": [
                    ("Черный юмор", "Обычные шутки"),
                    ("Едкие шутки", "Добрые шутки"),
                    ("Сарказм", "Прямота"),
                ]
            }
        }

    def get_meme_templates(self) -> List[Dict]:
        """Получает список доступных шаблонов мемов"""
        try:
            response = requests.get(f"{self.api_url}/get_memes")
            if response.status_code == 200:
                return response.json()['data']['memes']
            else:
                logging.error(f"Error getting meme templates: {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"Error getting meme templates: {e}")
            return []

    def create_meme(self, template_id: int, top_text: str = "", bottom_text: str = "") -> Optional[str]:
        """Создает мем с заданным текстом"""
        try:
            url = f"{self.api_url}/caption_image"
            data = {
                'template_id': template_id,
                'username': self.username,
                'password': self.password,
                'text0': top_text,
                'text1': bottom_text
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    return result['data']['url']
                else:
                    logging.error(f"Meme creation failed: {result['error_message']}")
                    return None
            else:
                logging.error(f"HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error creating meme: {e}")
            return None

    def create_personal_meme(self, user_type: str, context: str = "") -> Optional[str]:
        """Создает персональный мем для участника чата"""
        if user_type not in self.personal_memes:
            return None
            
        meme_data = self.personal_memes[user_type]
        
        # Выбираем случайный шаблон
        template_name = random.choice(meme_data["templates"])
        template_id = self.meme_templates.get(template_name)
        
        if not template_id:
            return None
            
        # Выбираем случайный текст
        text_pair = random.choice(meme_data["texts"])
        top_text, bottom_text = text_pair
        
        return self.create_meme(template_id, top_text, bottom_text)

    def create_context_meme(self, message_text: str, user_info: str = "") -> Optional[str]:
        """Создает мем на основе контекста сообщения"""
        message_lower = message_text.lower()
        
        # Определяем тип мема по контексту
        if any(word in message_lower for word in ["вадик", "vadik", "рыбалка", "катер", "дом"]):
            return self.create_personal_meme("vadik")
        elif any(word in message_lower for word in ["лёха", "leha", "кальян", "bmw", "никель"]):
            return self.create_personal_meme("leha")
        elif any(word in message_lower for word in ["мат", "ругайся", "выругайся", "агрессивный"]):
            return self.create_personal_meme("profanity")
        elif any(word in message_lower for word in ["шутка", "анекдот", "юмор", "смешно"]):
            return self.create_personal_meme("jokes")
        else:
            # Создаем случайный мем
            template_id = random.choice(list(self.meme_templates.values()))
            return self.create_meme(template_id, "Гриша шутит", "")

    def create_random_meme(self) -> Optional[str]:
        """Создает случайный мем"""
        template_id = random.choice(list(self.meme_templates.values()))
        
        # Случайные тексты для Гриши
        grisha_texts = [
            ("Гриша", "не бот"),
            ("Я просто друг", "который иногда пишет"),
            ("Черный юмор", "мой конек"),
            ("Мат", "это искусство"),
            ("Сарказм", "мой язык"),
        ]
        
        top_text, bottom_text = random.choice(grisha_texts)
        return self.create_meme(template_id, top_text, bottom_text)

# Создаем глобальный экземпляр
meme_generator = MemeGenerator()
