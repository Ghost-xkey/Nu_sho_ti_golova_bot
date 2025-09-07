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
        self.last_topic = {}    # chat_id -> {'topic': str, 'ts': unix}
        
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
        
        # Простые вызовы по имени - отвечаем на них
        simple_name_calls = ["гриша", "бот"]
        if message_lower in simple_name_calls:
            return True
        
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
    
    def get_target_user_info(self, message_text: str, author_username: Optional[str]) -> str:
        """Возвращает один факт строго о целевом пользователе:
        - если в сообщении есть @username — используем его
        - если запрос "про меня" — используем автора сообщения
        - в остальных случаях возвращаем пустую строку (не подмешиваем чужие факты)
        """
        try:
            import re
            from db import get_all_users
            
            text = (message_text or "").lower()
            target_username = None
            
            # 1) Явное упоминание @username
            mention = re.search(r"@(\w+)", message_text or "")
            if mention:
                target_username = mention.group(1)
            # 2) Запрос "про меня" — берём автора
            elif any(phrase in text for phrase in [
                "про меня", "расскажи про меня", "скажи про меня", "что ты знаешь обо мне",
                "что знаешь про меня", "расскажи обо мне"
            ]):
                if author_username:
                    # author_username приходит без @ из handlers
                    target_username = author_username.lstrip('@')
            
            if not target_username:
                return ""
            
            users = get_all_users()
            if not users:
                return ""
            
            # Ищем точное совпадение username
            user = next((u for u in users if (u.get('username') or "").lower() == target_username.lower()), None)
            if not user:
                return ""
            
            nickname = user.get('nickname') or "никнейм не указан"
            description = user.get('description') or "описание не указано"
            traits = user.get('traits') or "черты не указаны"
            jokes_about = user.get('jokes_about') or "шутки не указаны"
            
            # Формируем один факт о конкретном пользователе
            facts = [
                f"{nickname} - {description}",
                f"{nickname} известен тем, что: {traits}",
                f"Про {nickname} можно пошутить: {jokes_about}"
            ]
            # Выбираем первый информативный факт (приоритет: описание → черты → шутки)
            for fact in facts:
                if not any(x in fact for x in ["не указан", "не указано"]):
                    return f"Информация об участнике чата ({target_username}): {fact}"
            # Если все пустые — не подмешиваем
            return ""
        except Exception as e:
            logging.error(f"Error getting targeted user info: {e}")
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

    def update_topic(self, chat_id: str, message_text: str):
        """Обновляет текущую тему беседы на основе последнего сообщения пользователя"""
        try:
            import time
            key_phrases = ["про меня", "фильм", "кино", "работа", "учеба", "погода", "планы"]
            lowered = (message_text or "").lower()
            if any(k in lowered for k in key_phrases) or len(message_text) > 40:
                self.last_topic[chat_id] = {
                    'topic': message_text.strip()[:200],
                    'ts': int(time.time())
                }
        except Exception as e:
            logging.error(f"Error updating topic: {e}")

    def get_active_topic(self, chat_id: str) -> str:
        """Возвращает активную тему, если она моложе 15 минут"""
        import time
        info = self.last_topic.get(chat_id)
        if not info:
            return ""
        if time.time() - info['ts'] <= 15 * 60:
            return info['topic']
        return ""
    
    def generate_response(self, message_text: str, chat_id: str, username: str = None) -> Optional[str]:
        """
        Генерирует ответ AI на основе сообщения
        """
        try:
            # Добавляем сообщение в историю
            self.add_to_history(chat_id, message_text)
            
            # Получаем контекст
            context = self.get_chat_context(chat_id)
            # Обновляем и читаем активную тему (диалоговая инерция)
            self.update_topic(chat_id, message_text)
            active_topic = self.get_active_topic(chat_id)
            
            # Таргетная информация о пользователе (только если явно просят)
            users_info = self.get_target_user_info(message_text, username)
            
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
            
            # Проверяем простые вызовы по имени (без учета регистра)
            is_simple_name_call = message_text.strip().lower() in ["гриша", "бот"]
            
            # Фильтры для неинформативных сообщений
            short_messages = ["привет", "хай", "да", "нет", "ок", "окей", "понятно", "ясно", "спасибо", "спс"]
            meaningless_patterns = ["и все?", "и всё?", "всё?", "все?", "вот так", "ну да", "ага", "угу", "мм", "эм", "хм"]
            one_word_responses = ["круто", "понятно", "интересно", "классно", "отлично", "хорошо", "давай", "норм", "окей", "да"]
            
            # Проверяем на короткие и неинформативные сообщения
            # Исключаем простые вызовы по имени из фильтра коротких сообщений
            is_short_message = (message_text.strip() in short_messages and not is_simple_name_call) or (len(message_text.strip()) <= 3 and not is_simple_name_call)
            is_meaningless = any(pattern in message_lower for pattern in meaningless_patterns)
            is_emoji_only = len(message_text.strip()) <= 2 and any(char in "👍🤔😊😢😭😡😎🔥💯" for char in message_text)
            is_simple_response = is_short_message or is_meaningless or is_emoji_only
            
            # Проверяем на повторяющиеся сообщения
            is_repeated_message = self.check_repeated_message(chat_id, message_text)
            is_persistent_request = is_repeated_message and len(message_text) > 5  # Повторяющиеся сообщения длиннее 5 символов
            
            # Определяем нужна ли поддержка или дружеское участие
            # Исключаем простые и неинформативные сообщения, но учитываем настойчивые просьбы и простые вызовы по имени
            should_engage = (needs_support or wants_conversation or is_detailed_message or is_persistent_request or wants_movie_recommendation or is_simple_name_call) and not is_simple_response
            
            # Проверяем, отвечал ли бот в последних сообщениях (для продолжения диалога)
            recent_bot_messages = self.get_recent_bot_messages(chat_id, limit=3)
            is_continuing_conversation = len(recent_bot_messages) > 0
            
            # Вероятность включения в разговор (30% для поддержки, 20% для общения, 10% для детальных сообщений)
            base_engagement_probability = 0.3 if needs_support else 0.2 if wants_conversation else 0.1
            
            # Настойчивые просьбы получают высокую вероятность ответа
            if is_persistent_request:
                engagement_probability = 0.9  # 90% вероятность ответить на настойчивую просьбу
                response_type = "persistent_request"
            # Простые вызовы по имени получают высокую вероятность ответа
            elif is_simple_name_call:
                engagement_probability = 0.95  # 95% вероятность ответить на простой вызов
                response_type = "simple_name_call"
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
            
            # Мемы отключены
            is_meme_request = False
            
            # Дополнительная логика: продолжаем диалог если бот недавно отвечал
            # Но только если сообщение не является простым ответом
            if not should_auto_respond and not is_meme_request and is_continuing_conversation and not is_simple_response and message_text.strip().lower() not in ["гриша", "бот"]:
                # Если бот недавно отвечал, увеличиваем вероятность включения в обычные сообщения
                continue_probability = 0.3  # Снижаем до 30% для более качественных ответов
                if random.random() < continue_probability:
                    should_auto_respond = True
                    response_type = "continue_conversation"
            
            # Дополнительная логика: иногда включаемся в обычные разговоры (30% вероятность)
            if not should_auto_respond and not is_meme_request and message_text.strip().lower() not in ["гриша", "бот"] and random.random() < 0.3:
                should_auto_respond = True
                response_type = "casual_engagement"
            
            # Формируем промпт
            profanity_clause = "Умеренная крепкая лексика допустима, без оскорблений по признакам, угроз и явного NSFW." if ALLOW_PROFANITY else "Без мата."
            if ALLOW_PROFANITY and PROFANITY_LEVEL == "hard":
                profanity_clause = "Можешь использовать мат и крепкую лексику, ругаться как настоящий друг. Без хейта/дискриминации/угроз/NSFW."

            # Пользовательские предпочтения
            user_prefs = None
            try:
                if username:
                    from db import get_all_users, get_user_prefs
                    # Найдем user_id по username, если есть
                    users = get_all_users()
                    uid = next((u['user_id'] for u in users if (u.get('username') or '').lower() == username.lower()), None)
                    if uid:
                        user_prefs = get_user_prefs(uid)
            except Exception as e:
                logging.error(f"Error loading user prefs: {e}")

            # Если это запрос на мат - делаем промпт более агрессивным (с учетом предпочтений)
            allow_swear_now = ALLOW_PROFANITY and not (user_prefs and user_prefs.get('no_swear'))
            if is_profanity_request and allow_swear_now:
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
            elif response_type == "simple_name_call":
                context_prompt = """
Пользователь просто позвал тебя по имени! Будь живым и интересным:
- Это простое обращение типа "Гриша" или "Бот"
- Отвечай с юмором, шуткой или интересным вопросом
- НЕ отвечай односложно типа "Да?" или "Что?"
- Задай вопрос, пошути, или расскажи что-то интересное
- Будь в своем характере - саркастичным, но дружелюбным
- Развивай разговор, а не заканчивай его"""
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

АКТИВНАЯ ТЕМА (если есть): {active_topic or '—'}

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

            # Добавляем таргетную информацию о пользователе если есть
            if users_info:
                system_prompt += f"\n\n{users_info}"
                system_prompt += """
-- ОБЯЗАТЕЛЬНО упомяни хотя бы один конкретный факт о человеке из информации выше
-- Используй этот факт естественно в тексте, не как сухую справку
-- Шути и подколывай дружелюбно, без оскорблений и перехода на личности"""

            # Применяем предпочтения (имя обращения и любимые жанры)
            if user_prefs:
                pref_name = user_prefs.get('preferred_name')
                if pref_name:
                    system_prompt += f"\n\nОбращайся к пользователю как: {pref_name}"
                fav_genres = (user_prefs.get('favorite_genres') or '').strip()
                if fav_genres:
                    system_prompt += f"\n\nЕсли речь про фильмы — учитывай любимые жанры пользователя: {fav_genres}"

            user_prompt = f"Контекст последних сообщений:\n{context}\n\nТекущее сообщение: {message_text}"
            
            if username:
                user_prompt += f"\nОт пользователя: {username}"
            
            # Если это запрос на мат - добавляем специальное указание
            if is_profanity_request and ALLOW_PROFANITY:
                user_prompt += "\n\nВАЖНО: Пользователь просит тебя ругаться матом! ОБЯЗАТЕЛЬНО используй крепкую лексику в ответе!"
            
            # Генерируем ответ только если нужно (поддержка, общение или случайное включение)
            if not should_auto_respond:
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
