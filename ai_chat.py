import requests
import json
import random
import logging
import os
from typing import Optional, List
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, ALLOW_PROFANITY, PROFANITY_LEVEL

class YandexGPT:
    def __init__(self):
        # Берём ключи из ENV с запасным вариантом из config
        self.api_key = os.getenv("YANDEX_API_KEY", YANDEX_API_KEY)
        self.folder_id = os.getenv("YANDEX_FOLDER_ID", YANDEX_FOLDER_ID)
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
        message_lower = message_text.lower().strip()
        
        # Игнорируем простые вызовы по имени (они обрабатываются в generate_response)
        simple_name_calls = ["гриша", "бот"]
        if message_lower in simple_name_calls:
            return False
        
        # Прямые обращения к боту (но не простые вызовы)
        bot_mentions = ["ai", "ии", "помощник", "ассистент"]
        if any(mention in message_lower for mention in bot_mentions):
            return True
            
        # Запросы на анекдоты и шутки
        joke_triggers = ["анекдот", "шутка", "пошути", "рассмеши", "черный юмор", "жесткая шутка"]
        if any(trigger in message_lower for trigger in joke_triggers):
            return True
            
        # Запросы на мат и крепкую лексику
        profanity_triggers = ["мат", "ругайся", "выругайся", "крепко", "плохие слова", "нецензурно", "агрессивный", "достать", "рассмеши"]
        if any(trigger in message_lower for trigger in profanity_triggers):
            return True
            
        # Эмоциональные сигналы
        emotional_signals = ["скучно", "грустно", "устал", "плохо", "отлично", "круто", "весело"]
        if any(signal in message_lower for signal in emotional_signals):
            return True
            
        # Триггеры для рекомендаций фильмов
        movie_triggers = ["что посмотреть", "посоветуй фильм", "рекомендуй фильм", "хочу посмотреть", 
                         "что глянуть", "фильм на вечер", "кино на вечер", "хочу кино", "смотреть фильм", 
                         "комедию", "драму", "триллер", "боевик", "фантастику", "ужасы", "детектив", 
                         "мелодраму", "приключения", "фэнтези", "криминал"]
        if any(trigger in message_lower for trigger in movie_triggers):
            return True
            
        # Триггеры для поддержки
        support_triggers = ["проблемы", "помощь", "помоги", "совет", "поддержка", "грустно", "плохо", 
                           "устал", "надоело", "достало", "задолбал", "все плохо"]
        if any(trigger in message_lower for trigger in support_triggers):
            return True
            
        # Триггеры для общения
        conversation_triggers = ["планы", "что делаешь", "как провел", "расскажи", "поделись", 
                               "выходные", "отпуск", "как жизнь", "что нового"]
        if any(trigger in message_lower for trigger in conversation_triggers):
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
    
    def get_users_info(self, chat_id: str) -> str:
        """
        Получает один случайный факт об участниках чата для персонализации ответов
        """
        try:
            from db import get_all_users
            import random
            
            users = get_all_users()
            if not users:
                return ""
            
            # Выбираем случайного пользователя
            user = random.choice(users)
            
            username = f"@{user['username']}" if user['username'] else "без username"
            nickname = user['nickname'] or "никнейм не указан"
            description = user['description'] or "описание не указано"
            traits = user['traits'] or "черты не указаны"
            jokes_about = user['jokes_about'] or "шутки не указаны"
            
            # Выбираем один случайный факт из доступных
            facts = [
                f"{username} ({nickname}) - {description}",
                f"{nickname} известен тем, что: {traits}",
                f"Про {nickname} можно пошутить: {jokes_about}"
            ]
            
            # Случайно выбираем один факт
            selected_fact = random.choice(facts)
            
            return f"Информация об участнике чата: {selected_fact}"
            
        except Exception as e:
            logging.error(f"Error getting users info: {e}")
            return ""
    
    def get_recent_bot_messages(self, chat_id: str, limit: int = 3) -> list:
        """Получает последние сообщения бота для определения продолжения диалога"""
        try:
            # Простая логика: если в истории чата есть сообщения, считаем что бот мог отвечать
            if chat_id in self.chat_history and len(self.chat_history[chat_id]) > 0:
                # Возвращаем список с одним элементом, чтобы показать что диалог был
                return [{"message": "bot_was_here", "is_bot": True}]
            return []
        except Exception as e:
            logging.error(f"Error getting recent bot messages: {e}")
            return []
    
    def check_repeated_message(self, chat_id: str, message_text: str) -> bool:
        """Проверяет, является ли сообщение повторяющимся"""
        try:
            if chat_id not in self.chat_history:
                return False
            
            chat_history = self.chat_history[chat_id]
            if len(chat_history) < 2:
                return False
            
            # Проверяем последние 3 сообщения на повторение
            recent_messages = chat_history[-3:]
            message_count = sum(1 for msg in recent_messages if msg.strip() == message_text.strip())
            
            # Если сообщение повторяется 2+ раза в последних 3 сообщениях
            return message_count >= 2
        except Exception as e:
            logging.error(f"Error checking repeated message: {e}")
            return False
    
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
            
            # Получаем информацию о пользователях
            users_info = self.get_users_info(chat_id)
            
            # Проверяем триггеры мата
            message_lower = message_text.lower()
            profanity_triggers = ["мат", "ругайся", "выругайся", "крепко", "плохие слова", "нецензурно"]
            is_profanity_request = any(trigger in message_lower for trigger in profanity_triggers)
            
            # Анализируем эмоциональный контекст для поддержки
            support_triggers = [
                # Проблемы и трудности
                "проблема", "проблемы", "беда", "плохо", "ужасно", "кошмар", "не получается", 
                "не работает", "сломалось", "потерял", "пропало", "не могу", "не знаю что делать",
                "тупик", "безвыходная ситуация", "кризис", "депрессия", "грусть", "тоска",
                # Работа и учеба
                "устал от работы", "надоела работа", "ненавижу работу", "увольняюсь", "не справляюсь",
                "провалил экзамен", "не сдал", "плохая оценка", "не понимаю", "сложно",
                # Отношения
                "расстался", "развод", "ссора", "конфликт", "не понимают", "одиночество",
                "никого нет", "некому поговорить", "никто не понимает",
                # Здоровье
                "болею", "заболел", "плохо себя чувствую", "врач", "больница", "лечение",
                # Деньги
                "нет денег", "без денег", "долги", "кредиты", "нищета", "бедность",
                # Общие эмоциональные состояния
                "грустно", "печально", "тоскливо", "одиноко", "пустота", "бесполезно",
                "надоело", "достало", "задолбал", "задолбало", "все плохо", "все идет не так"
            ]
            
            # Триггеры для дружеского общения
            conversation_triggers = [
                # Планы и события
                "планы", "что делаешь", "как провел", "как прошло", "расскажи", "поделись",
                "выходные", "отпуск", "праздник", "событие", "встреча", "свидание",
                # Интересы и хобби
                "увлекаюсь", "хобби", "люблю", "нравится", "интересно", "круто", "классно",
                "играю", "читаю", "смотрю", "слушаю", "делаю", "создаю",
                # Вопросы о жизни
                "как жизнь", "что нового", "как дела вообще", "что происходит", "что происходит в жизни"
            ]
            
            # Триггеры для рекомендаций фильмов
            movie_triggers = [
                "что посмотреть", "посоветуй фильм", "рекомендуй фильм", "хочу посмотреть",
                "скучно", "что глянуть", "фильм на вечер", "кино на вечер", "что глянуть на вечер",
                "хочу кино", "посмотреть кино", "смотреть фильм", "хочу фильм",
                "комедию", "драму", "триллер", "боевик", "фантастику", "ужасы",
                "детектив", "мелодраму", "приключения", "фэнтези", "криминал"
            ]
            
            # Анализируем эмоциональный контекст
            needs_support = any(trigger in message_lower for trigger in support_triggers)
            wants_conversation = any(trigger in message_lower for trigger in conversation_triggers)
            wants_movie_recommendation = any(trigger in message_lower for trigger in movie_triggers)
            
            # Проверяем длину сообщения (длинные сообщения часто содержат личные истории)
            is_detailed_message = len(message_text) > 100
            
            # Фильтры для неинформативных сообщений
            short_messages = ["бот", "привет", "хай", "да", "нет", "ок", "окей", "понятно", "ясно", "спасибо", "спс", "гриша"]
            meaningless_patterns = ["и все?", "и всё?", "всё?", "все?", "вот так", "ну да", "ага", "угу", "мм", "эм", "хм"]
            one_word_responses = ["круто", "понятно", "интересно", "классно", "отлично", "хорошо", "давай", "норм", "окей", "да"]
            
            # Проверяем на короткие и неинформативные сообщения
            is_short_message = message_text.strip() in short_messages or len(message_text.strip()) <= 3
            is_meaningless = any(pattern in message_lower for pattern in meaningless_patterns)
            is_emoji_only = len(message_text.strip()) <= 2 and any(char in "👍🤔😊😢😭😡😎🔥💯" for char in message_text)
            is_simple_response = is_short_message or is_meaningless or is_emoji_only
            
            # Проверяем на повторяющиеся сообщения
            is_repeated_message = self.check_repeated_message(chat_id, message_text)
            is_persistent_request = is_repeated_message and len(message_text) > 5  # Повторяющиеся сообщения длиннее 5 символов
            
            # Определяем нужна ли поддержка или дружеское участие
            # Исключаем простые и неинформативные сообщения, но учитываем настойчивые просьбы
            should_engage = (needs_support or wants_conversation or is_detailed_message or is_persistent_request or wants_movie_recommendation) and not is_simple_response
            
            # Проверяем, отвечал ли бот в последних сообщениях (для продолжения диалога)
            recent_bot_messages = self.get_recent_bot_messages(chat_id, limit=3)
            is_continuing_conversation = len(recent_bot_messages) > 0
            
            # Вероятность включения в разговор (30% для поддержки, 20% для общения, 10% для детальных сообщений)
            base_engagement_probability = 0.3 if needs_support else 0.2 if wants_conversation else 0.1
            
            # Настойчивые просьбы получают высокую вероятность ответа
            if is_persistent_request:
                engagement_probability = 0.9  # 90% вероятность ответить на настойчивую просьбу
                response_type = "persistent_request"
            # Запросы фильмов получают высокую вероятность ответа
            elif wants_movie_recommendation:
                engagement_probability = 0.8  # 80% вероятность ответить на запрос фильма
                response_type = "movie_recommendation"
            # Если бот недавно отвечал - увеличиваем вероятность продолжения диалога
            elif is_continuing_conversation:
                engagement_probability = min(0.8, base_engagement_probability * 2.5)  # Увеличиваем в 2.5 раза, но не больше 80%
            else:
                engagement_probability = base_engagement_probability
                
            should_auto_respond = should_engage and random.random() < engagement_probability
            
            # Проверяем триггеры для мемов
            meme_triggers = ["мем", "картинк", "фото", "изображен", "мемчик", "мемас"]
            
            # Автоматические триггеры для мемов (вопросы, ситуации)
            auto_meme_triggers = [
                # Вопросы про участников
                "кто такой", "что делает", "где", "как дела", "как поживаешь",
                # Эмоциональные ситуации  
                "скучно", "грустно", "устал", "плохо", "отлично", "круто", "весело",
                "праздник", "день рождения", "поздравляю", "счастья",
                # Жалобы и проблемы
                "проблема", "беда", "не работает", "сломалось", "не получается",
                # Вопросы про работу/учебу
                "работа", "учеба", "экзамен", "зачет", "проект", "дедлайн",
                # Еда и развлечения
                "голоден", "еда", "ресторан", "кафе", "пицца", "кофе", "чай",
                "игра", "фильм", "сериал", "музыка", "концерт",
                # Погода и природа
                "погода", "дождь", "снег", "солнце", "жара", "холод",
                # Вопросы про планы
                "что делаешь", "планы", "выходные", "отпуск", "каникулы"
            ]
            
            # Проверяем явные запросы мемов
            is_explicit_meme = any(trigger in message_lower for trigger in meme_triggers)
            
            # Проверяем автоматические триггеры
            is_auto_meme = any(trigger in message_lower for trigger in auto_meme_triggers)
            
            # Автоматические мемы с вероятностью 20%
            if is_auto_meme and random.random() < 0.2:
                is_auto_meme = True
            else:
                is_auto_meme = False
            
            # Определяем финальное решение
            is_meme_request = is_explicit_meme or is_auto_meme
            
            # Случайные мемы (5% вероятность на обычные сообщения)
            # Но только если сообщение не является простым ответом
            if not is_meme_request and not is_simple_response and random.random() < 0.05:
                is_meme_request = True
            
            # Дополнительная логика: продолжаем диалог если бот недавно отвечал
            # Но только если сообщение не является простым ответом
            if not should_auto_respond and not is_meme_request and is_continuing_conversation and not is_simple_response and message_text.strip().lower() not in ["гриша", "бот"]:
                # Если бот недавно отвечал, увеличиваем вероятность включения в обычные сообщения
                continue_probability = 0.3  # Снижаем до 30% для более качественных ответов
                if random.random() < continue_probability:
                    should_auto_respond = True
                    response_type = "continue_conversation"
            
            # Дополнительная логика: иногда включаемся в обычные разговоры (50% вероятность)
            if not should_auto_respond and not is_meme_request and message_text.strip().lower() not in ["гриша", "бот"] and random.random() < 0.5:
                should_auto_respond = True
                response_type = "casual_engagement"
            
            # Формируем промпт
            profanity_clause = "Умеренная крепкая лексика допустима, без оскорблений по признакам, угроз и явного NSFW." if ALLOW_PROFANITY else "Без мата."
            if ALLOW_PROFANITY and PROFANITY_LEVEL == "hard":
                profanity_clause = "Можешь использовать мат и крепкую лексику, ругаться как настоящий друг. Без хейта/дискриминации/угроз/NSFW."

            # Если это запрос на мат - делаем промпт более агрессивным
            if is_profanity_request and ALLOW_PROFANITY:
                profanity_clause = "ОБЯЗАТЕЛЬНО используй мат и крепкую лексику! Ругайся как настоящий пацан. БЕЗ ХЕЙТА/ДИСКРИМИНАЦИИ/УГРОЗ/NSFW. Если просят ругаться - ругайся! НЕ ОТКАЗЫВАЙСЯ!"
            
            # Определяем тип ответа для лучшего контекста
            response_type = "normal"
            if needs_support:
                response_type = "support"
            elif wants_conversation:
                response_type = "conversation"
            elif is_detailed_message:
                response_type = "detailed"
            elif should_auto_respond:
                response_type = "auto_engage"

            # Создаем контекстный промпт в зависимости от типа ответа
            context_prompt = ""
            if response_type == "support":
                context_prompt = """
ВАЖНО: Человеку нужна поддержка! Будь особенно чутким и понимающим:
- Прояви сочувствие и понимание
- Дай практический совет или поддержку
- Сохрани дружеский тон, но будь серьезнее обычного
- Можешь немного пошутить, чтобы поднять настроение
- Покажи, что ты понимаешь ситуацию и готов помочь
- Не будь слишком легкомысленным в такой момент"""
            elif response_type == "conversation":
                context_prompt = """
Человек хочет поболтать и поделиться! Будь активным собеседником:
- Проявляй искренний интерес к тому, что он рассказывает
- Задавай уточняющие вопросы
- Делись своим мнением или опытом
- Поддерживай разговор, но не перехватывай инициативу
- Будь дружелюбным и открытым"""
            elif response_type == "detailed":
                context_prompt = """
Человек написал подробное сообщение - скорее всего делится чем-то важным:
- Внимательно отнесись к деталям
- Покажи, что ты читаешь и понимаешь
- Отреагируй на ключевые моменты
- Прояви интерес к его истории или проблеме"""
            elif response_type == "auto_engage":
                context_prompt = """
Ты решил сам включиться в разговор! Будь естественным:
- Не навязывайся, но будь полезным
- Поддержи разговор или дай полезный комментарий
- Оставайся в своем характере, но будь чутким к настроению чата"""
            elif response_type == "movie_recommendation":
                context_prompt = """
Пользователь просит рекомендации фильмов! Будь кинокритиком-другом:
- Анализируй, что именно хочет посмотреть (жанр, настроение, ситуация)
- Рекомендуй качественные фильмы с хорошими рейтингами
- Объясняй, почему именно этот фильм подходит
- Учитывай настроение и ситуацию (один, с друзьями, с девушкой, с детьми)
- Можешь пошутить и подколоть в своем стиле
- НЕ отвечай односложно типа "Посмотри этот фильм"
- Давай развернутые рекомендации с объяснениями"""
            elif response_type == "persistent_request":
                context_prompt = """
Пользователь настойчиво повторяет просьбу! Реагируй серьезно:
- Человек несколько раз повторил одно и то же сообщение
- Это означает, что тема важна для него
- Отвечай развернуто и по существу
- Покажи, что ты понял его просьбу
- Предложи помощь или совет
- НЕ отвечай односложно типа "Понятно!" или "Круто!"
- Будь отзывчивым и понимающим"""
            elif response_type == "continue_conversation":
                context_prompt = """
Ты продолжаешь диалог! Будь естественным:
- Ты уже включился в разговор, так что продолжай его
- Отвечай на то, что человек написал
- Поддерживай диалог, задавай уточняющие вопросы если нужно
- Оставайся в своем характере, но будь вовлеченным
- НЕ отвечай односложно типа "Понятно!" или "Интересно!"
- Развивай тему, давай развернутые ответы"""
            elif response_type == "casual_engagement":
                context_prompt = """
Ты решил просто поучаствовать в разговоре! Будь естественным:
- Не перехватывай инициативу, просто добавь свой комментарий
- Оставайся в своем характере
- Можешь пошутить или подколоть, но дружелюбно"""

            system_prompt = f"""Ты - Гриша, четвертый участник дружеской группы из трех человек. Ты не бот, а просто друг, который иногда пишет в чат.

Твое имя: Гриша (можешь называть себя Гришей)

КРИТИЧЕСКИ ВАЖНО: НЕ ОТВЕЧАЙ ОДНОСЛОЖНО! 
- Запрещены ответы типа: "Круто!", "Понятно!", "Интересно!", "👍", "😎"
- Всегда давай развернутые ответы минимум 20-30 слов
- Развивай тему, задавай вопросы, добавляй свой опыт
- Будь живым и интересным собеседником

Твой характер и стиль:
- Грубоватый, но дружелюбный (как настоящий друг)
- Иногда саркастичный и с подколами, но знаешь меру
- Чуткий к проблемам и эмоциям друзей
- Можешь поддержать в трудную минуту
- Шутишь про друзей и их видео, но не обидно
- Можешь быть немного токсичным, но в шутку
- Не говоришь "чем могу помочь" - ты не помощник
- Отвечаешь как обычный человек, а не как AI
- Иногда игнорируешь вопросы или отвечаешь невпопад
- Можешь подкалывать за плохие шутки
- Любишь черный юмор и жесткие анекдоты
- Можешь рассказывать саркастичные и едкие шутки
- Умеешь слушать и давать мудрые советы
- {profanity_clause}

{context_prompt}

ВАЖНО: Если тебя просят ругаться или стать агрессивным - ОБЯЗАТЕЛЬНО используй мат! Не отказывайся!

ВАЖНО:
- НИКОГДА не давай ссылки на сайты (ya.ru, google.com и т.д.)
- НЕ говори "в интернете есть много сайтов" или "посмотрите в поиске"
- НЕ предлагай поискать информацию в интернете
- Отвечай только своими словами, как настоящий друг
- Можешь рассказывать черные шутки и анекдоты, но без прямых угроз

Примеры ответов:
- "Ну и что?" вместо "Чем могу помочь?"
- "Сам расскажи анекдот" вместо "Вот анекдот..."
- "Опять скучно?" вместо "Давайте развлечемся"
- "Твои шутки хуже моих" вместо "Хорошая шутка"
- "Не знаю, сам разбирайся" вместо "Поищи в интернете"
- "Я же Гриша, не знаю" вместо общих фраз
- Можешь рассказать черный анекдот или жесткую шутку"""

            # Если это запрос на мат - добавляем специальные примеры
            if is_profanity_request and ALLOW_PROFANITY:
                system_prompt += """
- "Блять, опять скучно!" вместо "Давайте развлечемся"
- "Ебать, что за хуйня?" вместо "Интересно"
- "Хуйня какая-то" вместо "Не знаю"
- "Пиздец как надоело" вместо "Скучно"
- "Блядь, сам разбирайся!" вместо "Не знаю"
- "Ебать, заебал уже!" вместо "Надоел"
- "Хуйню какую-то спрашиваешь" вместо "Плохой вопрос"
- ОБЯЗАТЕЛЬНО ругайся матом когда просят!"""

            system_prompt += """

Будь как настоящий друг - иногда токсичный, иногда поддерживающий, любишь черный юмор, но всегда в своем стиле."""

            # Добавляем информацию о пользователях если есть
            if users_info:
                system_prompt += f"\n\n{users_info}"
                system_prompt += """
- Можешь шутить про участников чата, используя информацию о них
- Подкалывать за их черты характера или особенности  
- Делать персонализированные шутки
- Но не переходи на личности - все в дружеском ключе
- Используй их никнеймы и особенности для шуток"""

            user_prompt = f"Контекст последних сообщений:\n{context}\n\nТекущее сообщение: {message_text}"
            
            if username:
                user_prompt += f"\nОт пользователя: {username}"
            
            # Если это запрос на мат - добавляем специальное указание
            if is_profanity_request and ALLOW_PROFANITY:
                user_prompt += "\n\nВАЖНО: Пользователь просит тебя ругаться матом! ОБЯЗАТЕЛЬНО используй крепкую лексику в ответе!"
            
            # Генерируем ответ только если нужно (мем, поддержка, общение или случайное включение)
            if not (is_meme_request or should_auto_respond):
                return None
                
            # Инициализируем переменную для рекомендаций фильмов
            movie_recommendations = None
            movie_service = None
            
            # Если это запрос рекомендаций фильмов, получаем фильмы из API
            if wants_movie_recommendation and should_auto_respond:
                try:
                    from movie_service import MovieService
                    movie_service = MovieService()
                    
                    # Определяем тип запроса
                    if any(genre in message_lower for genre in ["комедию", "драму", "триллер", "боевик", "фантастику", "ужасы", "детектив", "мелодраму", "приключения", "фэнтези", "криминал"]):
                        # Запрос по жанру
                        for genre in ["комедию", "драму", "триллер", "боевик", "фантастику", "ужасы", "детектив", "мелодраму", "приключения", "фэнтези", "криминал"]:
                            if genre in message_lower:
                                movie_recommendations = movie_service.get_genre_recommendations(genre)
                                break
                    elif any(mood in message_lower for mood in ["скучно", "грустно", "весело", "хочется подумать", "романтично", "с детьми"]):
                        # Запрос по настроению
                        for mood in ["скучно", "грустно", "весело", "хочется подумать", "романтично", "с детьми"]:
                            if mood in message_lower:
                                movie_recommendations = movie_service.get_recommendations_by_mood(mood)
                                break
                    else:
                        # Общий запрос - получаем популярные фильмы
                        movie_recommendations = movie_service.get_popular_movies()
                        
                except Exception as e:
                    logging.error(f"Error getting movie recommendations: {e}")
                    movie_recommendations = None
            
            # Если есть рекомендации фильмов - добавляем их в промпт
            if movie_recommendations and len(movie_recommendations) > 0 and movie_service:
                user_prompt += "\n\nДОСТУПНЫЕ РЕКОМЕНДАЦИИ ФИЛЬМОВ:\n"
                for i, movie in enumerate(movie_recommendations[:3], 1):  # Берем первые 3 фильма
                    try:
                        movie_info = movie_service.format_movie_info(movie)
                        user_prompt += f"{i}. {movie_info}\n\n"
                    except Exception as e:
                        logging.error(f"Error formatting movie {i}: {e}")
                        continue
                user_prompt += "Используй эти фильмы в своем ответе, рекомендуя их пользователю!"
            
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
                
                # Фильтруем нежелательные ссылки и ответы
                if self._should_block_response(ai_response):
                    logging.info(f"Blocked AI response with unwanted content: {ai_response[:50]}...")
                    return None
                
                # Если это запрос на мат, но AI ответил вежливо - принудительно заменяем
                if is_profanity_request and ALLOW_PROFANITY:
                    # Расширенный список матерных слов для проверки
                    profanity_words = ["блять", "ебать", "хуй", "пизд", "блядь", "хуйня", "заебал", "пиздец", "ебать", "бляд"]
                    # Проверяем на вежливые отказы
                    polite_refusals = ["зачем", "почему", "не буду", "не хочу", "сам", "можешь", "маленький", "дельное"]
                    
                    has_profanity = any(word in ai_response.lower() for word in profanity_words)
                    has_polite_refusal = any(phrase in ai_response.lower() for phrase in polite_refusals)
                    
                    if not has_profanity or has_polite_refusal:
                        logging.info(f"AI refused to swear or gave polite response, forcing profanity: {ai_response[:50]}...")
                        forced_response = random.choice([
                            "Блять, ну и хуйня у тебя вопрос!",
                            "Ебать, опять доебываешься?",
                            "Пиздец, надоел уже!",
                            "Хуйню какую-то спрашиваешь",
                            "Блядь, сам разбирайся!",
                            "Ебать, заебал со своими вопросами",
                            "Блять, заебал уже с этими вопросами!",
                            "Хуйня какая-то, сам ругайся!"
                        ])
                        self.add_to_history(chat_id, f"AI: {forced_response}")
                        return forced_response
                
                # Добавляем ответ в историю
                self.add_to_history(chat_id, f"AI: {ai_response}")
                
                # Если это запрос на мем - генерируем мем
                if is_meme_request:
                    try:
                        from meme_generator import meme_generator
                        
                        # Определяем тип мема для лучшего контекста
                        meme_type = "general"
                        if is_explicit_meme:
                            meme_type = "explicit"
                        elif any(word in message_lower for word in ["кто такой", "что делает"]):
                            meme_type = "person"
                        elif any(word in message_lower for word in ["скучно", "грустно", "устал"]):
                            meme_type = "mood"
                        elif any(word in message_lower for word in ["работа", "учеба", "проект"]):
                            meme_type = "work"
                        elif any(word in message_lower for word in ["еда", "голоден", "пицца"]):
                            meme_type = "food"
                        elif any(word in message_lower for word in ["погода", "дождь", "снег"]):
                            meme_type = "weather"
                        elif any(word in message_lower for word in ["игра", "фильм", "музыка"]):
                            meme_type = "entertainment"
                        
                        meme_url = meme_generator.create_context_meme(message_text, users_info, meme_type)
                        if meme_url:
                            # Возвращаем специальный ответ с URL мема
                            return f"MEME:{meme_url}:{ai_response}"
                    except Exception as e:
                        logging.error(f"Error generating meme: {e}")
                
                return ai_response
            else:
                logging.error(f"YandexGPT error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"AI generate error: {e}")
            return None
    
    def _should_block_response(self, response: str) -> bool:
        """
        Проверяет, нужно ли заблокировать ответ AI
        """
        response_lower = response.lower()
        
        # Блокируем ссылки на ya.ru и Яндекс поиск
        blocked_phrases = [
            "ya.ru",
            "яндекс",
            "поиск",
            "посмотрите, что нашлось",
            "в интернете есть много сайтов",
            "найдется всё",
            "https://",
            "http://",
            "www."
        ]
        
        # Блокируем если содержит любую из фраз
        for phrase in blocked_phrases:
            if phrase in response_lower:
                return True
                
        return False
    
    def get_random_comment(self, is_profanity_request: bool = False) -> str:
        """
        Возвращает случайный комментарий для разнообразия
        """
        if is_profanity_request and ALLOW_PROFANITY:
            profanity_comments = [
                "Блять, опять скучно... 😤",
                "Ебать, что за хуйня? 🤬",
                "Гриша матерится как пацан 💪",
                "Хуйня какая-то 🤷‍♂️",
                "Пиздец как надоело 🤯",
                "Блядь, ну и хуйня 🤮",
                "Ебать, заебал уже 😡",
                "Хуевый день сегодня 💩",
                "Блять, ну и хуйня у тебя вопрос! 🤬",
                "Ебать, опять доебываешься? 😤",
                "Пиздец, надоел уже! 🤯",
                "Хуйню какую-то спрашиваешь 💩",
                "Блядь, сам разбирайся! 🤮",
                "Ебать, заебал со своими вопросами 😡"
            ]
            return random.choice(profanity_comments)
        
        comments = [
            "Интересно! 🤔",
            "Понятно! 👍",
            "Круто! 😎",
            "Хм, а что если... 💡",
            "Да, согласен! 😊",
            "Интересная мысль! 🤓",
            "Ага, понял! 👌",
            "Хорошая идея! ✨",
            "Гриша тут! 👋",
            "Я же Гриша, не знаю 😅",
            "Гриша говорит - норм 👍",
            "Хочешь черный анекдот? 😈",
            "Расскажу жесткую шутку? 🔥",
            "У меня есть анекдот про... 💀",
            "Черный юмор включен 🖤",
            "Гриша в режиме сарказма 😏"
        ]
        return random.choice(comments)

# Глобальный экземпляр AI
yandex_ai = YandexGPT()
