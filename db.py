import sqlite3
from config import DB_PATH

def get_db_connection():
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
        
        conn.commit()
        print("Tables created successfully")
        
        # Проверим, что таблица создалась
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_messages'")
        result = cursor.fetchone()
        if result:
            print("video_messages table exists")
        else:
            print("ERROR: video_messages table not found!")
            
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
