import sqlite3
from config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS video_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id TEXT UNIQUE NOT NULL,
                        file_unique_id TEXT UNIQUE NOT NULL,
                        message_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        username TEXT,
                        caption TEXT,
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def save_video_message(file_id, file_unique_id, message_id, user_id, username, caption=None):
    """Сохраняет видеосообщение в базу данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT OR IGNORE INTO video_messages 
                         (file_id, file_unique_id, message_id, user_id, username, caption)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (file_id, file_unique_id, message_id, user_id, username, caption))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving video message: {e}")
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
