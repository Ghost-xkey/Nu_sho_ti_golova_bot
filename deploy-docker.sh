#!/bin/bash

# Скрипт для деплоя через Docker

set -e

echo "🐳 Начинаем Docker деплой..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Перезайдите в систему для применения изменений."
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "📝 Создаем .env файл..."
    if [ -f env.example ]; then
        cp env.example .env
    else
        echo "⚠️  Файл env.example не найден, создаем .env вручную..."
        cat > .env << EOF
# Telegram Bot Configuration
TOKEN=7255987005:AAEMSy4B0zWvJcH5RoJas9o4pEYvPMA__0g
CHAT_ID=-573460520
DB_PATH=bot_database.db
EOF
    fi
    echo "⚠️  Отредактируйте .env файл с вашими настройками!"
    nano .env
fi

# Создаем директорию для данных
mkdir -p data

# Собираем и запускаем контейнер
echo "🔨 Собираем Docker образ..."
docker-compose build

echo "🚀 Запускаем бота..."
docker-compose up -d

echo "✅ Docker деплой завершен!"
echo "📋 Для управления ботом:"
echo "   docker-compose logs -f          # просмотр логов"
echo "   docker-compose stop             # остановка"
echo "   docker-compose start            # запуск"
echo "   docker-compose restart          # перезапуск"