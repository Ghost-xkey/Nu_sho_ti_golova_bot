import aiohttp
import base64
import logging
from typing import Dict, Any, List, Optional
from config import GOOGLE_VISION_API_KEY

class GoogleVisionAnalyzer:
    """Анализатор изображений через Google Vision API"""
    
    def __init__(self):
        self.api_key = GOOGLE_VISION_API_KEY
        self.base_url = "https://vision.googleapis.com/v1/images:annotate"
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Анализирует изображение через Google Vision API"""
        
        # Кодируем изображение в base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Формируем запрос
        request_body = {
            "requests": [{
                "image": {
                    "content": image_base64
                },
                "features": [
                    {
                        "type": "LABEL_DETECTION",
                        "maxResults": 10
                    },
                    {
                        "type": "FACE_DETECTION",
                        "maxResults": 10
                    },
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 10
                    },
                    {
                        "type": "OBJECT_LOCALIZATION",
                        "maxResults": 10
                    },
                    {
                        "type": "LANDMARK_DETECTION",
                        "maxResults": 5
                    },
                    {
                        "type": "LOGO_DETECTION",
                        "maxResults": 5
                    }
                ]
            }]
        }
        
        # URL с API ключом
        url = f"{self.base_url}?key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_body) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self.parse_analysis_result(result)
                    else:
                        error_text = await response.text()
                        logging.error(f"Google Vision API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logging.error(f"Error calling Google Vision API: {e}")
            return None
    
    def parse_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Парсит результат анализа Google Vision API"""
        
        if not result or 'responses' not in result:
            return None
        
        response = result['responses'][0]
        parsed = {
            'labels': [],
            'faces': [],
            'text': [],
            'objects': [],
            'landmarks': [],
            'logos': []
        }
        
        # Извлекаем метки (labels)
        if 'labelAnnotations' in response:
            for label in response['labelAnnotations']:
                parsed['labels'].append({
                    'description': label['description'],
                    'confidence': label['score']
                })
        
        # Извлекаем лица
        if 'faceAnnotations' in response:
            for face in response['faceAnnotations']:
                emotions = []
                if 'joyLikelihood' in face:
                    emotions.append(f"радость: {face['joyLikelihood']}")
                if 'sorrowLikelihood' in face:
                    emotions.append(f"грусть: {face['sorrowLikelihood']}")
                if 'angerLikelihood' in face:
                    emotions.append(f"злость: {face['angerLikelihood']}")
                if 'surpriseLikelihood' in face:
                    emotions.append(f"удивление: {face['surpriseLikelihood']}")
                
                parsed['faces'].append({
                    'emotions': emotions,
                    'detection_confidence': face.get('detectionConfidence', 0)
                })
        
        # Извлекаем текст
        if 'textAnnotations' in response:
            for text in response['textAnnotations']:
                parsed['text'].append(text['description'])
        
        # Извлекаем объекты
        if 'localizedObjectAnnotations' in response:
            for obj in response['localizedObjectAnnotations']:
                parsed['objects'].append({
                    'name': obj['name'],
                    'confidence': obj['score']
                })
        
        # Извлекаем достопримечательности
        if 'landmarkAnnotations' in response:
            for landmark in response['landmarkAnnotations']:
                parsed['landmarks'].append({
                    'description': landmark['description'],
                    'confidence': landmark['score']
                })
        
        # Извлекаем логотипы
        if 'logoAnnotations' in response:
            for logo in response['logoAnnotations']:
                parsed['logos'].append({
                    'description': logo['description'],
                    'confidence': logo['score']
                })
        
        return parsed

class GrishaPhotoCommenter:
    """Генератор токсичных комментариев Гриши для фотографий"""
    
    def __init__(self):
        self.comment_templates = {
            'selfie': [
                "О, еще одно селфи. Надеюсь, ты потратил на него меньше времени, чем на этот комментарий 😏",
                "Красиво, но не так красиво, как мой код 💻",
                "Фильтры работают, а вот твоя логика - нет 🤔",
                "Селфи как селфи, но твои шутки хуже 📸"
            ],
            'food': [
                "Еда выглядит лучше, чем твои шутки 🍕",
                "Надеюсь, это не твоя кулинария, иначе я сочувствую твоему желудку 🤢",
                "Красивая тарелка, жаль, что содержимое не так аппетитно 🍽️",
                "Еда есть, а мозгов у тебя нет 🍔"
            ],
            'pet': [
                "Животное милее тебя, это факт 🐱",
                "Кот выглядит умнее тебя, и это не комплимент 🐈",
                "Собака верная, в отличие от твоих обещаний 🐕",
                "Питомец симпатичнее хозяина 🐾"
            ],
            'landscape': [
                "Красиво, но не так красиво, как мой код 🌅",
                "Природа не виновата, что ты ее фотографируешь 🌲",
                "Пейзаж хорош, жаль, что ты его портишь своим присутствием 🏔️",
                "Природа красивая, а ты - нет 🌿"
            ],
            'group': [
                "Очередная групповая фотка, где все улыбаются, а внутри плачут 👥",
                "Слишком много людей на одном фото, как в твоей голове 🤯",
                "Групповое фото - это когда все притворяются, что им весело 🎭",
                "Много лиц, но мозгов не видно 👥"
            ],
            'text': [
                "Текст на фото умнее тебя 📝",
                "Надпись читается лучше, чем твои мысли ✍️",
                "Текст есть, а смысла нет 📄"
            ],
            'default': [
                "Интересное фото, но не так интересное, как мой комментарий 📸",
                "Фото есть, но ничего особенного не вижу 👀",
                "Красиво, но не так красиво, как мой код 💻",
                "Фотка как фотка, ничего особенного 🤷‍♂️"
            ]
        }
    
    async def generate_comment(self, analysis: Dict[str, Any]) -> str:
        """Генерирует токсичный комментарий на основе анализа"""
        
        if not analysis:
            return "Не могу проанализировать это фото. Возможно, оно слишком ужасное даже для меня."
        
        # Определяем тип фото
        photo_type = self.determine_photo_type(analysis)
        
        # Выбираем случайный комментарий
        import random
        comments = self.comment_templates.get(photo_type, self.comment_templates['default'])
        base_comment = random.choice(comments)
        
        # Возвращаем только комментарий без технической информации
        return base_comment
    
    def determine_photo_type(self, analysis: Dict[str, Any]) -> str:
        """Определяет тип фото на основе анализа"""
        
        # Проверяем наличие лиц
        if analysis.get('faces'):
            face_count = len(analysis['faces'])
            if face_count == 1:
                return 'selfie'
            else:
                return 'group'
        
        # Проверяем метки
        labels = [label['description'].lower() for label in analysis.get('labels', [])]
        
        # Еда
        food_keywords = ['food', 'meal', 'dish', 'restaurant', 'cooking', 'kitchen', 'pizza', 'burger', 'sandwich']
        if any(keyword in ' '.join(labels) for keyword in food_keywords):
            return 'food'
        
        # Животные
        pet_keywords = ['dog', 'cat', 'pet', 'animal', 'puppy', 'kitten', 'bird', 'fish']
        if any(keyword in ' '.join(labels) for keyword in pet_keywords):
            return 'pet'
        
        # Пейзажи
        landscape_keywords = ['landscape', 'nature', 'mountain', 'forest', 'beach', 'sky', 'tree', 'water']
        if any(keyword in ' '.join(labels) for keyword in landscape_keywords):
            return 'landscape'
        
        # Текст
        if analysis.get('text'):
            return 'text'
        
        return 'default'
    
    def get_analysis_details(self, analysis: Dict[str, Any]) -> str:
        """Возвращает детали анализа для комментария"""
        
        details = []
        
        # Метки
        if analysis.get('labels'):
            top_labels = [label['description'] for label in analysis['labels'][:3]]
            details.append(f"Вижу: {', '.join(top_labels)}")
        
        # Лица
        if analysis.get('faces'):
            face_count = len(analysis['faces'])
            if face_count == 1:
                details.append("Одно лицо на фото")
            else:
                details.append(f"{face_count} лиц на фото")
        
        # Текст
        if analysis.get('text'):
            text_preview = analysis['text'][0][:50] + "..." if len(analysis['text'][0]) > 50 else analysis['text'][0]
            details.append(f"Текст: '{text_preview}'")
        
        # Объекты
        if analysis.get('objects'):
            objects = [obj['name'] for obj in analysis['objects'][:3]]
            details.append(f"Объекты: {', '.join(objects)}")
        
        return " | ".join(details) if details else ""
