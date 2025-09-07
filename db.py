import sqlite3
from config import DB_PATH

# Таблицы будут созданы при запуске бота через on_startup

def get_db_connection():
    import os
    
    print(f"get_db_connection called with DB_PATH: {DB_PATH}")
    
    # Создаем директорию если не существует
    db_dir = os.path.dirname(DB_PATH)
    print(f"Database directory: {db_dir}")
    
    # Принудительно создаем папку /app/data если она не существует
    if db_dir and db_dir != '':
        try:
            print(f"Creating directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Directory created/verified: {db_dir}")
        except Exception as e:
            print(f"❌ Error creating directory {db_dir}: {e}")
            # Fallback: используем /tmp если не можем создать /app/data
            fallback_path = '/tmp/bot_database.db'
            print(f"🔄 Using fallback path: {fallback_path}")
            conn = sqlite3.connect(fallback_path)
            print(f"Database connection successful (fallback)")
            return conn
    else:
        print(f"Directory already exists: {db_dir}")
    
    print(f"Connecting to database: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Database connection successful")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        # Fallback: используем /tmp если не можем подключиться
        fallback_path = '/tmp/bot_database.db'
        print(f"🔄 Using fallback path: {fallback_path}")
        conn = sqlite3.connect(fallback_path)
        print(f"Database connection successful (fallback)")
        return conn

def create_tables():
    print("create_tables function called")
    conn = None
    try:
        print("Getting database connection...")
        conn = get_db_connection()
        print("Database connection obtained")
        cursor = conn.cursor()
        print("Creating users table...")
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT,
                            first_name TEXT,
                            last_name TEXT,
                            nickname TEXT,
                            description TEXT,
                            traits TEXT,
                            jokes_about TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        print("Creating video_messages table...")
        cursor.execute('''CREATE TABLE IF NOT EXISTS video_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT UNIQUE NOT NULL,
            file_unique_id TEXT UNIQUE NOT NULL,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            caption TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        print("Creating yearly_events table...")
        cursor.execute('''CREATE TABLE IF NOT EXISTS yearly_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            day INTEGER NOT NULL,
            month INTEGER NOT NULL,
            hour INTEGER DEFAULT 10,
            minute INTEGER DEFAULT 0,
            message TEXT NOT NULL,
            music_url TEXT,
            photo_file_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # Предпочтения пользователей
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_prefs (
            user_id INTEGER PRIMARY KEY,
            preferred_name TEXT,
            favorite_genres TEXT,
            no_swear INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        print("Tables created successfully")
        
        # Проверим, что таблицы создались
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_messages'")
        result = cursor.fetchone()
        if result:
            print("video_messages table exists")
        else:
            print("ERROR: video_messages table not found!")
            
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yearly_events'")
        result = cursor.fetchone()
        if result:
            print("yearly_events table exists")
        else:
            print("ERROR: yearly_events table not found!")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_prefs'")
        result = cursor.fetchone()
        if result:
            print("user_prefs table exists")
        else:
            print("ERROR: user_prefs table not found!")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

def save_video_message(file_id, file_unique_id, message_id, user_id, username, caption=None):
    """Сохраняет видеосообщение в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print(f"Attempting to save video: file_id={file_id}, user_id={user_id}, username={username}")
        
        # Проверяем, существует ли таблица
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_messages'")
        if not cursor.fetchone():
            print("Table video_messages does not exist, creating it...")
            create_tables()
        
        cursor.execute('''INSERT OR IGNORE INTO video_messages 
                         (file_id, file_unique_id, message_id, user_id, username, caption)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (file_id, file_unique_id, message_id, user_id, username, caption))
        
        rows_affected = cursor.rowcount
        print(f"Rows affected: {rows_affected}")
        
        conn.commit()
        
        if rows_affected > 0:
            print(f"Video saved successfully: {file_id}")
            return True
        else:
            print(f"Video already exists or failed to save: {file_id}")
            return False
            
    except Exception as e:
        print(f"Error saving video message: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def get_random_video():
    """Получает случайное видеосообщение из базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT file_id, file_unique_id, username, caption 
                         FROM video_messages 
                         ORDER BY RANDOM() 
                         LIMIT 1''')
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error getting random video: {e}")
        return None
    finally:
        conn.close()

def get_video_count():
    """Возвращает количество сохраненных видеосообщений"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM video_messages')
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting video count: {e}")
        return 0
    finally:
        conn.close()

def get_user_stats():
    """Возвращает статистику по пользователям"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT username, COUNT(*) as video_count 
                         FROM video_messages 
                         GROUP BY user_id, username 
                         ORDER BY video_count DESC''')
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return []
    finally:
        conn.close()

def save_user(user_id, username=None, first_name=None, last_name=None):
    """Сохраняет пользователя в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)''',
                      (user_id, username, first_name, last_name))
        conn.commit()
        print(f"User saved: {user_id}, username: {username}")
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False
    finally:
        conn.close()

def update_user_info(user_id, nickname=None, description=None, traits=None, jokes_about=None):
    """Обновляет информацию о пользователе"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Формируем запрос обновления
        updates = []
        values = []
        
        if nickname is not None:
            updates.append("nickname = ?")
            values.append(nickname)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if traits is not None:
            updates.append("traits = ?")
            values.append(traits)
        if jokes_about is not None:
            updates.append("jokes_about = ?")
            values.append(jokes_about)
            
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
            cursor.execute(query, values)
            conn.commit()
            print(f"User {user_id} updated successfully")
            return True
        else:
            print("No updates provided")
            return False
            
    except Exception as e:
        print(f"Error updating user info: {e}")
        return False
    finally:
        conn.close()

def get_user_info(user_id):
    """Получает информацию о пользователе"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT user_id, username, first_name, last_name, nickname, 
                         description, traits, jokes_about 
                         FROM users WHERE user_id = ?''', (user_id,))
        result = cursor.fetchone()
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'nickname': result[4],
                'description': result[5],
                'traits': result[6],
                'jokes_about': result[7]
            }
        return None
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None
    finally:
        conn.close()

def get_all_users():
    """Получает информацию о всех пользователях"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''SELECT user_id, username, first_name, last_name, nickname, 
                         description, traits, jokes_about 
                         FROM users ORDER BY username''')
        results = cursor.fetchall()
        users = []
        for result in results:
            users.append({
                'user_id': result[0],
                'username': result[1],
                'first_name': result[2],
                'last_name': result[3],
                'nickname': result[4],
                'description': result[5],
                'traits': result[6],
                'jokes_about': result[7]
            })
        return users
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []
    finally:
        conn.close()

def get_total_users():
    """Возвращает количество уникальных пользователей"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Считаем пользователей из video_messages (кто отправлял видео)
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM video_messages')
        video_users = cursor.fetchone()
        video_count = video_users[0] if video_users else 0
        
        # Также считаем пользователей из таблицы users (если она используется)
        cursor.execute('SELECT COUNT(*) FROM users')
        users_result = cursor.fetchone()
        users_count = users_result[0] if users_result else 0
        
        # Возвращаем максимальное значение
        return max(video_count, users_count)
    except Exception as e:
        print(f"Error getting total users: {e}")
        return 0
    finally:
        conn.close()

def get_user_prefs(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_id, preferred_name, favorite_genres, no_swear FROM user_prefs WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            'user_id': row[0],
            'preferred_name': row[1],
            'favorite_genres': row[2],
            'no_swear': bool(row[3])
        }
    except Exception as e:
        print(f"Error getting user prefs: {e}")
        return None
    finally:
        conn.close()

def upsert_user_prefs(user_id: int, preferred_name: str = None, favorite_genres: str = None, no_swear: bool = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT 1 FROM user_prefs WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone() is not None
        if not exists:
            cursor.execute('INSERT INTO user_prefs (user_id, preferred_name, favorite_genres, no_swear) VALUES (?,?,?,?)', (
                user_id,
                preferred_name,
                favorite_genres,
                1 if no_swear else 0 if no_swear is not None else 0
            ))
        else:
            fields = []
            values = []
            if preferred_name is not None:
                fields.append('preferred_name = ?')
                values.append(preferred_name)
            if favorite_genres is not None:
                fields.append('favorite_genres = ?')
                values.append(favorite_genres)
            if no_swear is not None:
                fields.append('no_swear = ?')
                values.append(1 if no_swear else 0)
            if fields:
                fields.append('updated_at = CURRENT_TIMESTAMP')
                sql = f"UPDATE user_prefs SET {', '.join(fields)} WHERE user_id = ?"
                values.append(user_id)
                cursor.execute(sql, tuple(values))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error upserting user prefs: {e}")
        return False
    finally:
        conn.close()
def init_default_users():
    """Инициализирует пользователей по умолчанию"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Вадик
        vadik_info = {
            'user_id': 1210990768,
            'username': 'vadik7k',
            'nickname': 'Вадик',
            'description': 'Калмык, халя, рыбак, пенсия. Любит рыбалку и пиво по вечерам. Косоглазый, работает связистом, живет в Выборге, ездит на октахе, мечтает купить катер. Ловит судаков, играет в футбол. Есть брат Саша. Купил дом, но не сделал ремонт. Бросает курить, переобувается, иногда теряется от друзей. Добрый и помогает друзьям.',
            'traits': 'Косоглазый, добрый, помогает друзьям, иногда теряется',
            'jokes_about': 'Шутит про его косоглазие, рыбалку, пиво, дом без ремонта, попытки бросить курить, мечты о катере'
        }
        
        # Лёха
        leha_info = {
            'user_id': 5166587439,
            'username': 'perfomers',
            'nickname': 'Лёха',
            'description': 'Перформер, брат. Любит кальяны и играть в плойку. Иногда ездит на рыбалку. Живет в Никеле, не был на сверхглубокой. Зимой не видит солнца, иногда видит Норвегию, но не может туда съездить. Любит BMW, но ходит пешком. Иногда парит девчонок в бане, забивает елки с малиной в кальян. Любит вискарь с колой, играет с Диманом в плойку и пьет виски. Лечит зубы, иногда ранимый, иногда тяжелый на подъем.',
            'traits': 'Ранимый, тяжелый на подъем, любит кальяны и виски',
            'jokes_about': 'Шутит про его жизнь в Никеле без солнца, мечты о BMW при ходьбе пешком, кальянную зависимость, лечение зубов, ранимость'
        }
        
        # Добавляем пользователей
        for user_info in [vadik_info, leha_info]:
            cursor.execute('''INSERT OR REPLACE INTO users 
                             (user_id, username, first_name, last_name, nickname, description, traits, jokes_about, updated_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                          (user_info['user_id'], user_info['username'], None, None, 
                           user_info['nickname'], user_info['description'], 
                           user_info['traits'], user_info['jokes_about']))
        
        conn.commit()
        print("✅ Default users initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing default users: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

# Функции для работы с ежегодными событиями
def add_yearly_event(name, day, month, hour=10, minute=0, message="", music_url="", photo_file_id=""):
    """Добавляет новое ежегодное событие"""
    print(f"add_yearly_event called with: name={name}, day={day}, month={month}, hour={hour}, minute={minute}, message={message}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Проверим, что таблица существует
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yearly_events'")
        result = cursor.fetchone()
        if not result:
            print("ERROR: yearly_events table does not exist! Creating tables...")
            create_tables()
            # Проверим еще раз
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='yearly_events'")
            result = cursor.fetchone()
            if not result:
                print("ERROR: Failed to create yearly_events table!")
                return False
        
        print("Executing INSERT query...")
        cursor.execute('''INSERT INTO yearly_events 
                         (name, day, month, hour, minute, message, music_url, photo_file_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (name, day, month, hour, minute, message, music_url, photo_file_id))
        
        print("Committing transaction...")
        conn.commit()
        print(f"Yearly event added successfully: {name}")
        return True
    except Exception as e:
        print(f"Error adding yearly event: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def get_yearly_events():
    """Возвращает все активные ежегодные события"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM yearly_events WHERE is_active = 1 ORDER BY month, day')
        events = cursor.fetchall()
        return events
    except Exception as e:
        print(f"Error getting yearly events: {e}")
        return []
    finally:
        conn.close()

def get_yearly_event_by_date(day, month):
    """Возвращает событие по дате"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM yearly_events WHERE day = ? AND month = ? AND is_active = 1', (day, month))
        event = cursor.fetchone()
        return event
    except Exception as e:
        print(f"Error getting yearly event by date: {e}")
        return None
    finally:
        conn.close()

def update_yearly_event(event_id, **kwargs):
    """Обновляет ежегодное событие"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Формируем запрос обновления
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [event_id]
        
        cursor.execute(f'UPDATE yearly_events SET {set_clause} WHERE id = ?', values)
        
        conn.commit()
        print(f"Yearly event {event_id} updated")
        return True
    except Exception as e:
        print(f"Error updating yearly event: {e}")
        return False
    finally:
        conn.close()

def delete_yearly_event(event_id):
    """Удаляет ежегодное событие (деактивирует)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE yearly_events SET is_active = 0 WHERE id = ?', (event_id,))
        
        conn.commit()
        print(f"Yearly event {event_id} deleted")
        return True
    except Exception as e:
        print(f"Error deleting yearly event: {e}")
        return False
    finally:
        conn.close()
