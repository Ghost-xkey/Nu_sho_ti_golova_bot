#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-интерфейс для бота Гриша
Красивый dashboard с современным дизайном
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import logging

# Добавляем путь к основному проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модули бота
try:
    from db import get_all_users, get_user_prefs
    from config import DB_PATH
    DATABASE_PATH = DB_PATH
except ImportError as e:
    logging.error(f"Ошибка импорта модулей бота: {e}")
    # Fallback для тестирования
    DATABASE_PATH = "bot.db"

app = Flask(__name__)
app.secret_key = 'grisha_web_interface_secret_key_2024'

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Подключение к базе данных"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return None

@app.route('/')
def dashboard():
    """Главная страница - Dashboard"""
    try:
        # Получаем статистику
        stats = get_dashboard_stats()
        recent_videos = get_recent_videos_data()
        users_data = get_users_data()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_videos=recent_videos,
                             users_data=users_data)
    except Exception as e:
        logger.error(f"Ошибка в dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/videos')
def videos():
    """Страница с видео-галереей"""
    try:
        videos = get_all_videos()
        return render_template('videos.html', videos=videos)
    except Exception as e:
        logger.error(f"Ошибка в videos: {e}")
        return render_template('error.html', error=str(e))

@app.route('/users')
def users():
    """Страница с пользователями"""
    try:
        users_data = get_users_data()
        return render_template('users.html', users=users_data)
    except Exception as e:
        logger.error(f"Ошибка в users: {e}")
        return render_template('error.html', error=str(e))

@app.route('/settings')
def settings():
    """Страница настроек"""
    try:
        settings_data = get_settings_data()
        return render_template('settings.html', settings=settings_data)
    except Exception as e:
        logger.error(f"Ошибка в settings: {e}")
        return render_template('error.html', error=str(e))

# API endpoints
@app.route('/api/stats')
def api_stats():
    """API для получения статистики"""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos')
def api_videos():
    """API для получения видео"""
    try:
        videos = get_all_videos()
        return jsonify(videos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
def api_users():
    """API для получения пользователей"""
    try:
        users = get_users_data()
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video/<int:video_id>')
def api_video_detail(video_id):
    """API для получения деталей видео"""
    try:
        video = get_video_detail(video_id)
        if video:
            return jsonify(video)
        else:
            return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Функции для работы с данными
def get_dashboard_stats():
    """Получение статистики для dashboard"""
    conn = get_db_connection()
    if not conn:
        return {
            'total_videos': 0,
            'total_users': 0,
            'total_chats': 0,
            'videos_today': 0,
            'videos_this_week': 0,
            'videos_this_month': 0
        }
    
    try:
        cursor = conn.cursor()
        
        # Общее количество видео
        cursor.execute("SELECT COUNT(*) as count FROM video_messages")
        total_videos = cursor.fetchone()['count']
        
        # Общее количество пользователей
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM video_messages")
        total_users = cursor.fetchone()['count']
        
        # Общее количество чатов
        cursor.execute("SELECT COUNT(DISTINCT chat_id) as count FROM video_messages")
        total_chats = cursor.fetchone()['count']
        
        # Видео за сегодня
        today = datetime.now().date()
        cursor.execute("SELECT COUNT(*) as count FROM video_messages WHERE DATE(created_at) = ?", (today,))
        videos_today = cursor.fetchone()['count']
        
        # Видео за неделю
        week_ago = (datetime.now() - timedelta(days=7)).date()
        cursor.execute("SELECT COUNT(*) as count FROM video_messages WHERE DATE(created_at) >= ?", (week_ago,))
        videos_this_week = cursor.fetchone()['count']
        
        # Видео за месяц
        month_ago = (datetime.now() - timedelta(days=30)).date()
        cursor.execute("SELECT COUNT(*) as count FROM video_messages WHERE DATE(created_at) >= ?", (month_ago,))
        videos_this_month = cursor.fetchone()['count']
        
        return {
            'total_videos': total_videos,
            'total_users': total_users,
            'total_chats': total_chats,
            'videos_today': videos_today,
            'videos_this_week': videos_this_week,
            'videos_this_month': videos_this_month
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            'total_videos': 0,
            'total_users': 0,
            'total_chats': 0,
            'videos_today': 0,
            'videos_this_week': 0,
            'videos_this_month': 0
        }
    finally:
        conn.close()

def get_recent_videos_data():
    """Получение последних видео"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT vm.*, u.username, u.first_name, u.last_name
            FROM video_messages vm
            LEFT JOIN users u ON vm.user_id = u.user_id
            ORDER BY vm.created_at DESC
            LIMIT 10
        """)
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row['id'],
                'file_id': row['file_id'],
                'username': row['username'] or 'Unknown',
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'chat_id': row['chat_id'],
                'created_at': row['created_at'],
                'file_size': row.get('file_size', 0),
                'duration': row.get('duration', 0)
            })
        
        return videos
    except Exception as e:
        logger.error(f"Ошибка получения последних видео: {e}")
        return []
    finally:
        conn.close()

def get_all_videos():
    """Получение всех видео"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT vm.*, u.username, u.first_name, u.last_name
            FROM video_messages vm
            LEFT JOIN users u ON vm.user_id = u.user_id
            ORDER BY vm.created_at DESC
        """)
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row['id'],
                'file_id': row['file_id'],
                'username': row['username'] or 'Unknown',
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'chat_id': row['chat_id'],
                'created_at': row['created_at'],
                'file_size': row.get('file_size', 0),
                'duration': row.get('duration', 0)
            })
        
        return videos
    except Exception as e:
        logger.error(f"Ошибка получения всех видео: {e}")
        return []
    finally:
        conn.close()

def get_users_data():
    """Получение данных пользователей"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, 
                   COUNT(vm.id) as video_count,
                   MAX(vm.created_at) as last_video_date
            FROM users u
            LEFT JOIN video_messages vm ON u.user_id = vm.user_id
            GROUP BY u.user_id
            ORDER BY video_count DESC, last_video_date DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'video_count': row['video_count'],
                'last_video_date': row['last_video_date'],
                'created_at': row['created_at']
            })
        
        return users
    except Exception as e:
        logger.error(f"Ошибка получения пользователей: {e}")
        return []
    finally:
        conn.close()

def get_video_detail(video_id):
    """Получение деталей конкретного видео"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT vm.*, u.username, u.first_name, u.last_name
            FROM video_messages vm
            LEFT JOIN users u ON vm.user_id = u.user_id
            WHERE vm.id = ?
        """, (video_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'file_id': row['file_id'],
                'username': row['username'] or 'Unknown',
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'chat_id': row['chat_id'],
                'created_at': row['created_at'],
                'file_size': row.get('file_size', 0),
                'duration': row.get('duration', 0)
            }
        return None
    except Exception as e:
        logger.error(f"Ошибка получения деталей видео: {e}")
        return None
    finally:
        conn.close()

def get_settings_data():
    """Получение настроек"""
    return {
        'bot_name': 'Гриша',
        'version': '2.0',
        'database_path': DATABASE_PATH,
        'web_interface_port': 5000
    }

if __name__ == '__main__':
    print("🚀 Запуск веб-интерфейса для бота Гриша...")
    print("📱 Откройте браузер и перейдите по адресу: http://localhost:5001")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
