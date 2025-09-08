#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест веб-интерфейса
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Гриша Bot - Тест</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white">
                            <h1 class="h3 mb-0">
                                <i class="fas fa-robot me-2"></i>Гриша Bot - Веб-интерфейс
                            </h1>
                        </div>
                        <div class="card-body text-center">
                            <div class="mb-4">
                                <i class="fas fa-check-circle fa-5x text-success"></i>
                            </div>
                            <h2 class="text-success">✅ Веб-интерфейс работает!</h2>
                            <p class="lead">Веб-интерфейс для бота Гриша успешно запущен</p>
                            
                            <div class="row mt-4">
                                <div class="col-md-4">
                                    <div class="card border-primary">
                                        <div class="card-body">
                                            <h5 class="card-title text-primary">📊 Dashboard</h5>
                                            <p class="card-text">Статистика и аналитика</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-success">
                                        <div class="card-body">
                                            <h5 class="card-title text-success">🎬 Видео</h5>
                                            <p class="card-text">Галерея видео</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card border-info">
                                        <div class="card-body">
                                            <h5 class="card-title text-info">👥 Пользователи</h5>
                                            <p class="card-text">Управление пользователями</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <a href="/api/test" class="btn btn-primary btn-lg">
                                    <i class="fas fa-plug me-2"></i>Тест API
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    </body>
    </html>
    ''')

@app.route('/api/test')
def api_test():
    return {
        'status': 'success',
        'message': 'API работает!',
        'data': {
            'bot_name': 'Гриша',
            'version': '2.0',
            'web_interface': 'Активен'
        }
    }

if __name__ == '__main__':
    print("🚀 Запуск тестового веб-интерфейса...")
    print("📱 Откройте браузер: http://92.63.100.172:5001")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
