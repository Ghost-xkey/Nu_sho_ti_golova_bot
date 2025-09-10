import random
import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FactsGenerator:
    def __init__(self, db_path: str = "/app/data/bot_database.db"):
        self.db_path = db_path
        self.facts_db = self._load_facts_database()
        self._init_database()
    
    def _load_facts_database(self) -> Dict[str, List[Dict]]:
        """Загружаем базу фактов с подколами"""
        return {
            "animals": [
                {
                    "fact": "Осьминоги имеют три сердца и голубую кровь",
                    "roast": "А у тебя одно сердце и красная кровь, но ты всё равно не умеешь любить",
                    "category": "biology"
                },
                {
                    "fact": "Коалы спят 18-22 часа в сутки",
                    "roast": "Ты тоже много спишь, но хотя бы коалы милые",
                    "category": "biology"
                },
                {
                    "fact": "Пингвины могут прыгать на высоту до 2 метров",
                    "roast": "А ты не можешь даже прыгнуть выше своих амбиций",
                    "category": "biology"
                },
                {
                    "fact": "Слоны помнят всё на протяжении 60 лет",
                    "roast": "А ты забываешь, где оставил ключи от квартиры",
                    "category": "biology"
                },
                {
                    "fact": "Дельфины дают друг другу имена",
                    "roast": "А тебя зовут просто 'тот парень с плохими шутками'",
                    "category": "biology"
                },
                {
                    "fact": "Бегемоты бегают быстрее человека",
                    "roast": "Даже бегемот быстрее тебя, а ты думаешь, что в хорошей форме",
                    "category": "biology"
                },
                {
                    "fact": "Крокодилы не могут высовывать язык",
                    "roast": "А ты не можешь держать язык за зубами",
                    "category": "biology"
                },
                {
                    "fact": "Улитки могут спать до 3 лет",
                    "roast": "Ты тоже много спишь, но улитки хотя бы полезны",
                    "category": "biology"
                }
            ],
            "science": [
                {
                    "fact": "Солнце весит в 333,000 раз больше Земли",
                    "roast": "А твой мозг весит в 333,000 раз меньше, чем у нормального человека",
                    "category": "physics"
                },
                {
                    "fact": "Человеческий мозг на 75% состоит из воды",
                    "roast": "У тебя, видимо, остальные 25% - это пустота",
                    "category": "biology"
                },
                {
                    "fact": "Бананы радиоактивны из-за калия-40",
                    "roast": "А ты токсичен из-за своей личности",
                    "category": "chemistry"
                },
                {
                    "fact": "В космосе нет звука",
                    "roast": "А в твоей голове тоже тишина",
                    "category": "physics"
                },
                {
                    "fact": "Свет от Солнца до Земли идёт 8 минут",
                    "roast": "А твоя мысль до мозга идёт 8 часов",
                    "category": "physics"
                },
                {
                    "fact": "Вода кипит при 100°C",
                    "roast": "А ты закипаешь от любой критики",
                    "category": "chemistry"
                },
                {
                    "fact": "Золото не ржавеет",
                    "roast": "А твоя репутация ржавеет каждый день",
                    "category": "chemistry"
                },
                {
                    "fact": "Чёрные дыры поглощают всё, включая свет",
                    "roast": "А ты поглощаешь всё, включая чужую еду",
                    "category": "physics"
                }
            ],
            "history": [
                {
                    "fact": "Наполеон был ростом 168 см",
                    "roast": "Он завоевал пол-Европы, а ты не можешь даже завоевать сердце соседки",
                    "category": "historical"
                },
                {
                    "fact": "Пирамиды строили 20 лет",
                    "roast": "А ты 20 лет строишь из себя умного",
                    "category": "historical"
                },
                {
                    "fact": "Римская империя просуществовала 1000 лет",
                    "roast": "А твоя мотивация длится 5 минут",
                    "category": "historical"
                },
                {
                    "fact": "Колумб думал, что открыл Индию",
                    "roast": "А ты думаешь, что открыл Америку, сидя на диване",
                    "category": "historical"
                },
                {
                    "fact": "Викинги были отличными мореплавателями",
                    "roast": "А ты не можешь даже переплыть бассейн",
                    "category": "historical"
                },
                {
                    "fact": "Древние египтяне изобрели папирус",
                    "roast": "А ты изобрёл способ тратить время впустую",
                    "category": "historical"
                },
                {
                    "fact": "Великая Китайская стена видна из космоса",
                    "roast": "А твои достижения не видны даже в микроскоп",
                    "category": "historical"
                },
                {
                    "fact": "Стоунхендж построили 5000 лет назад",
                    "roast": "А ты до сих пор не можешь собрать мебель из ИКЕА",
                    "category": "historical"
                }
            ],
            "technology": [
                {
                    "fact": "Первый компьютер весил 27 тонн",
                    "roast": "А твой мозг весит как перышко",
                    "category": "tech"
                },
                {
                    "fact": "Интернет изобрели в 1969 году",
                    "roast": "А ты до сих пор не умеешь им пользоваться",
                    "category": "tech"
                },
                {
                    "fact": "Первый iPhone появился в 2007 году",
                    "roast": "А ты до сих пор пользуешься кнопочным телефоном",
                    "category": "tech"
                },
                {
                    "fact": "Google обрабатывает 8.5 миллиардов запросов в день",
                    "roast": "А ты обрабатываешь 8.5 глупых мыслей в минуту",
                    "category": "tech"
                },
                {
                    "fact": "Wi-Fi изобрели в 1991 году",
                    "roast": "А ты до сих пор не можешь подключиться к жизни",
                    "category": "tech"
                },
                {
                    "fact": "Первый сайт создали в 1991 году",
                    "roast": "А ты до сих пор не можешь создать профиль в соцсетях",
                    "category": "tech"
                }
            ],
            "food": [
                {
                    "fact": "Мёд никогда не портится",
                    "roast": "А твои шутки портятся с каждой секундой",
                    "category": "food"
                },
                {
                    "fact": "Шоколад был валютой у ацтеков",
                    "roast": "А ты используешь валюту, чтобы купить шоколад",
                    "category": "food"
                },
                {
                    "fact": "Морковь изначально была фиолетовой",
                    "roast": "А ты изначально был нормальным",
                    "category": "food"
                },
                {
                    "fact": "Пиццу изобрели в Италии",
                    "roast": "А ты изобрёл способ заказывать её каждый день",
                    "category": "food"
                },
                {
                    "fact": "Кофе - второй по популярности напиток в мире",
                    "roast": "А ты - первый по непопулярности в своём районе",
                    "category": "food"
                },
                {
                    "fact": "Бананы - это ягоды",
                    "roast": "А ты - это разочарование",
                    "category": "food"
                }
            ]
        }
    
    def _init_database(self):
        """Инициализируем таблицы в базе данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Таблица для хранения отправленных фактов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    fact_id TEXT NOT NULL,
                    fact_text TEXT NOT NULL,
                    roast_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    sent_date DATE NOT NULL,
                    sent_time TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица для хранения всех фактов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facts_library (
                    id TEXT PRIMARY KEY,
                    fact_text TEXT NOT NULL,
                    roast_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Заполняем библиотеку фактов, если она пустая
            cursor.execute('SELECT COUNT(*) FROM facts_library')
            if cursor.fetchone()[0] == 0:
                self._populate_facts_library(cursor)
            
            conn.commit()
            conn.close()
            logger.info("Facts database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing facts database: {e}")
    
    def _populate_facts_library(self, cursor):
        """Заполняем библиотеку фактов"""
        fact_id = 1
        for subcategory, facts in self.facts_db.items():
            for fact in facts:
                cursor.execute('''
                    INSERT INTO facts_library (id, fact_text, roast_text, category, subcategory)
                    VALUES (?, ?, ?, ?, ?)
                ''', (f"fact_{fact_id}", fact["fact"], fact["roast"], fact["category"], subcategory))
                fact_id += 1
    
    def get_random_fact(self, user_id: int, category: Optional[str] = None) -> Optional[Dict]:
        """Получаем случайный факт, который пользователь ещё не видел"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем все факты, которые пользователь уже видел сегодня
            today = date.today()
            cursor.execute('''
                SELECT fact_id FROM sent_facts 
                WHERE user_id = ? AND sent_date = ?
            ''', (user_id, today))
            seen_facts = {row[0] for row in cursor.fetchall()}
            
            # Получаем доступные факты
            if category:
                cursor.execute('''
                    SELECT id, fact_text, roast_text, category, subcategory 
                    FROM facts_library 
                    WHERE subcategory = ? AND id NOT IN ({})
                '''.format(','.join('?' * len(seen_facts))), [category] + list(seen_facts))
            else:
                cursor.execute('''
                    SELECT id, fact_text, roast_text, category, subcategory 
                    FROM facts_library 
                    WHERE id NOT IN ({})
                '''.format(','.join('?' * len(seen_facts))), list(seen_facts))
            
            available_facts = cursor.fetchall()
            
            if not available_facts:
                # Если все факты показаны, сбрасываем счётчик для этого пользователя
                logger.info(f"All facts shown to user {user_id} today, resetting...")
                cursor.execute('''
                    DELETE FROM sent_facts 
                    WHERE user_id = ? AND sent_date = ?
                ''', (user_id, today))
                conn.commit()
                
                # Повторяем запрос
                if category:
                    cursor.execute('''
                        SELECT id, fact_text, roast_text, category, subcategory 
                        FROM facts_library 
                        WHERE subcategory = ?
                    ''', (category,))
                else:
                    cursor.execute('''
                        SELECT id, fact_text, roast_text, category, subcategory 
                        FROM facts_library
                    ''')
                available_facts = cursor.fetchall()
            
            if available_facts:
                fact_data = random.choice(available_facts)
                conn.close()
                return {
                    "id": fact_data[0],
                    "fact": fact_data[1],
                    "roast": fact_data[2],
                    "category": fact_data[3],
                    "subcategory": fact_data[4]
                }
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting random fact: {e}")
            return None
    
    def mark_fact_as_sent(self, user_id: int, fact_data: Dict, sent_time: str):
        """Отмечаем факт как отправленный"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sent_facts (user_id, fact_id, fact_text, roast_text, category, sent_date, sent_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                fact_data["id"],
                fact_data["fact"],
                fact_data["roast"],
                fact_data["category"],
                date.today(),
                sent_time
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Fact {fact_data['id']} marked as sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error marking fact as sent: {e}")
    
    def get_user_facts_stats(self, user_id: int) -> Dict:
        """Получаем статистику фактов пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Общее количество прочитанных фактов
            cursor.execute('''
                SELECT COUNT(*) FROM sent_facts WHERE user_id = ?
            ''', (user_id,))
            total_read = cursor.fetchone()[0]
            
            # Факты за сегодня
            cursor.execute('''
                SELECT COUNT(*) FROM sent_facts 
                WHERE user_id = ? AND sent_date = ?
            ''', (user_id, date.today()))
            today_read = cursor.fetchone()[0]
            
            # Любимая категория
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM sent_facts 
                WHERE user_id = ? 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 1
            ''', (user_id,))
            favorite_result = cursor.fetchone()
            favorite_category = favorite_result[0] if favorite_result else "Нет данных"
            
            conn.close()
            
            return {
                "total_read": total_read,
                "today_read": today_read,
                "favorite_category": favorite_category
            }
            
        except Exception as e:
            logger.error(f"Error getting user facts stats: {e}")
            return {"total_read": 0, "today_read": 0, "favorite_category": "Ошибка"}
    
    def get_all_active_users(self) -> List[int]:
        """Получаем список всех активных пользователей"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Сначала пробуем получить из таблицы пользователей
            try:
                cursor.execute('''
                    SELECT user_id FROM users
                ''')
                users = [row[0] for row in cursor.fetchall()]
                if users:
                    conn.close()
                    return users
            except:
                # Если таблица users не существует, получаем из sent_facts
                pass
            
            # Получаем всех пользователей, которые когда-либо получали факты
            cursor.execute('''
                SELECT DISTINCT user_id FROM sent_facts
            ''')
            users = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
