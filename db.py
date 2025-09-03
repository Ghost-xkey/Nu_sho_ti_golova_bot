import sqlite3
from config import DB_PATH

# Создаем таблицы сразу при импорте модуля
try:
    create_tables()
except Exception as e:
    print(f"Error creating tables on import: {e}")

def get_db_connection():
    import os
    
    # Создаем директорию если не существует
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}")
    
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("Creating users table...")
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT)''')
        
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
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
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

def get_total_users():
    """Возвращает количество уникальных пользователей"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM video_messages')
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting total users: {e}")
        return 0
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
