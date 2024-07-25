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
    conn.commit()
    conn.close()
