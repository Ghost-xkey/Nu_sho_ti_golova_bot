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
        # Наборы вариаций без эмодзи и без тех. деталей
        self.comment_variants = {
            'selfie': [
                "Лицо старается, а харизма — нет",
                "Селфи удалась, вот бы с характером так же",
                "Ты снова смотришь в камеру, как в бездну — и она отвечает взаимностью",
                "Грим, фильтр, надежды — а получилось все равно ты",
                "Снимок уверенный, как твои слабые оправдания",
                "Селфи приличное, хотя твой внутренний редактор опять прогулял",
                "Лицо в кадре одно, а эго на весь экран",
                "Портрет есть, портретности нет. Зато старание заметно",
                "Селфи бодрое, но обаяние еще грузится",
                "Хороший свет. Жаль, что на характер он не влияет",
                "Ракурс ищет тебя лучшего. Пока безуспешно",
                "Настроение на фото — как твой Wi‑Fi: то есть, то нет"
            ],
            'food': [
                "Еда выглядит так, будто ей страшно оказаться у тебя дома",
                "На тарелке праздник, на душе — студень",
                "Аппетитно. Главное — не испортить разговорами",
                "Красиво подано. Надеюсь, на вкус не как твои идеи",
                "Если это ты готовил — тогда респект тому, кто выжил",
                "Шик, блеск, калории. Твоя совесть уже вышла из чата",
                "Еда топ, репутация под вопросом",
                "Сфоткал, значит съел. Инстинкты сильнее эстетики",
                "Десерт милый. Почти как твои попытки быть серьезным",
                "Композиция сильная, диета сломалась ещё сильнее",
                "Это выглядит вкусно. Жаль, лайки не насыщают",
                "Кулинарный перфоманс уровня: спасайся кто может"
            ],
            'pet': [
                "Питомец хорош. Ты стараешься не мешать — и это мудро",
                "Животное милое. На его фоне ты почти человек",
                "Кот берет харизмой. Тебе пока не продают",
                "Собака верная. В отличие от твоего режима дня",
                "Зверь очарователен. Постарайся не учить его своим привычкам",
                "Это животное — главная причина, почему фото стоит смотреть",
                "Лапки прекрасные. Хозяин — рабочая версия",
                "Питомец фотогеничен. Ты рядом для масштаба",
                "Хозяин старался, но звезда — не он",
                "Вы оба милые. Он — по факту, ты — по заявке",
                "Пушистик — 10/10. Хозяин — попросим выйти из кадра",
                "Глазки у зверя умные. Возьми контакт тренера"
            ],
            'landscape': [
                "Природа постаралась. Ты пока только сфоткал",
                "Красиво. Даже ты это не испортил — уже достижение",
                "Пейзаж сильный, автор слабее, но амбициозен",
                "Горы держатся молодцом, а ты — за телефон",
                "Спокойный кадр. На твой характер не похоже",
                "Воздух чистый, мысли — посмотрим",
                "Тут красиво без фильтров. Заметил?",
                "Композиция сработала. Теперь бы с жизнью так же",
                "Природа — редактор лучше любого приложения",
                "Пейзаж вдохновляет. Тебе бы тоже начать",
                "Глазам приятно. Эго — помолчи",
                "Место мощное. Ты пока статист"
            ],
            'group': [
                "Толпа улыбается. Значит, кто-то уже сдался",
                "Групповое фото: все заняты тем, чтобы казаться лучше",
                "Лиц много, внимания мало. Особенно к сути",
                "Дружно стоите, дружно устаете",
                "Тут весело по сценарию. А вживую как?",
                "Команда есть. Теперь бы план",
                "Энергии много, синхронизации — как получится",
                "Группой вы выглядите смелее, чем по одному",
                "Кто-то на фото думает о еде. И это лучший план",
                "Людей много — объектив страдает",
                "Съёмка корпоративная по духу, даже если это не так",
                "Химия есть. Только не перегрейте"
            ],
            'text': [
                "Надпись на фото тонко намекает, что пора взять себя в руки",
                "Текст громкий, смысл в отпуске",
                "Надпись уверена, что это важно. Убедила?",
                "Лозунг бодрый. Привычки — нет",
                "Слова прямо в кадре. И все равно мимо сути",
                "Текст старается, читатель — как получится",
                "Подпись серьезная, жизнь — мем",
                "Если следовать написанному, сюрпризов будет меньше",
                "Текст на месте, выводов нет",
                "Надпись кричит, совесть шепчет",
                "Слова не плохие. Выполнение традиционно страдает",
                "Читается легко, выполняется тяжело"
            ],
            'default': [
                "Кадр уверенный, смысла в нем примерно как в твоих оправданиях",
                "Снято небездарно. Дальше будет сложнее",
                "Фото живое. Постарайся не заглушить",
                "Композиция пытается, ты мешаешь чуть меньше обычного",
                "Снимок норм. С характером поработаем позже",
                "В этом кадре есть настроение. Тебе бы такое",
                "Получилось на удивление сносно",
                "Неплохо. Неожиданно честно",
                "Слегка драматично. Как твоя самооценка по утрам",
                "Смотришь — и вроде хочется верить, что ты стараешься",
                "Дерзко сфоткал. Осталось жить в том же стиле",
                "Картинка дышит. Ты — попробуй тоже"
            ]
        }
    
    async def generate_comment(self, analysis: Dict[str, Any]) -> str:
        """Генерирует токсичный, но естественный комментарий по контексту фото.
        Без тех. деталей, только одна короткая реплика."""
        
        if not analysis:
            return "Не получилось понять, что на фото. Попробуй другое — и без ужасов, ладно"
        
        # Вычисляем тип кадра и семя для вариативности
        photo_type = self.determine_photo_type(analysis)
        seed = self._build_seed(analysis)
        
        # Подбираем основу
        base = self._pick_variant(self.comment_variants.get(photo_type) or self.comment_variants['default'], seed, 17)
        
        # Тонкие контекстные штрихи (без прямого раскрытия меток)
        tail = self._build_tail(analysis, seed)
        
        # Склеиваем аккуратно, без лишних символов
        result = base
        if tail:
            # Одна строка без лишних точек
            result = f"{base}; {tail}"
        
        # Фильтрация заезженных фраз
        banned = [
            "О, еще одно селфи",
            "Красиво, но не так красиво, как мой код",
            "Фильтры работают, а вот твоя логика - нет",
            "Текст есть, а смысла нет",
            "Текст на фото умнее тебя",
            "Групповое фото - это когда все притворяются, что им весело"
        ]
        lower = result.lower()
        if any(p.lower() in lower for p in banned):
            alt = self._pick_variant(self.comment_variants.get('default'), seed, 911)
            result = alt if alt else result
        return result
    
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

    def _build_seed(self, analysis: Dict[str, Any]) -> int:
        """Строит детерминированное семя на основе содержимого, чтобы разные фото давали разные фразы."""
        try:
            import hashlib
            parts = []
            for lbl in (analysis.get('labels') or [])[:5]:
                parts.append(lbl.get('description', ''))
            for obj in (analysis.get('objects') or [])[:5]:
                parts.append(obj.get('name', ''))
            if analysis.get('text'):
                parts.append((analysis['text'][0] or '')[:32])
            raw = '|'.join(parts) or 'fallback'
            h = hashlib.sha256(raw.encode('utf-8')).hexdigest()
            return int(h[:12], 16)
        except Exception:
            import time
            return int(time.time() * 1000) & 0xFFFFFFFF

    def _pick_variant(self, options, seed: int, salt: int) -> str:
        """Выбирает вариант из списка детерминированно от seed."""
        import random
        rnd = random.Random(seed + salt)
        return rnd.choice(options)

    def _build_tail(self, analysis: Dict[str, Any], seed: int) -> str:
        """Строит короткий хвост-комментарий по контексту (лица/текст/объекты), без тех. деталей."""
        phrases = []
        face_count = len(analysis.get('faces') or [])
        if face_count == 1:
            phrases.append("на фото один герой, и ему бы отдохнуть")
        elif face_count > 3:
            phrases.append("людей много — внимания мало")
        elif face_count > 1:
            phrases.append("компания дружная, но нервы у камеры на пределе")
        
        # Если есть текст — упомянуть без цитирования
        if analysis.get('text'):
            extra = [
                "надпись уверенно делает вид, что так и задумано",
                "текст обещает больше, чем реальность",
                "подпись старается звучать умно — пусть так и будет",
                "слова в кадре громкие, выводы — тише"
            ]
            phrases.append(self._pick_variant(extra, seed, 101))
        
        # Если найдены объекты/метки — намекнуть на насыщенность
        has_objects = bool(analysis.get('objects'))
        has_labels = bool(analysis.get('labels'))
        if has_objects and has_labels:
            phrases.append("в кадре деталей достаточно, осталось навести на смысл")
        elif has_objects:
            phrases.append("предметов хватает — а вот идеи бы добавить")
        elif has_labels:
            phrases.append("настроение считывается, даже если ты его не планировал")
        
        # Слегка перемешать и сократить до 1-2 фраз
        if phrases:
            import random
            rnd = random.Random(seed + 313)
            rnd.shuffle(phrases)
            return ' '.join(phrases[:2])
        return ""
    
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
