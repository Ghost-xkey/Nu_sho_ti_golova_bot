#!/bin/bash

# Скрипт для создания .env файла

echo "🔧 Создаем .env файл для Telegram бота..."

# Проверяем, есть ли env.example
if [ -f env.example ]; then
    echo "📋 Копируем из env.example..."
    cp env.example .env
    echo "✅ Файл .env создан из env.example"
else
    echo "📝 Создаем .env файл вручную..."
    cat > .env << EOF
# Telegram Bot Configuration
TOKEN=7255987995:AAGaXiV6oYBY1UCgizHPqVZuxVhsAKqIA94
CHAT_ID=-573460520
DB_PATH=bot_database.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
EOF
    echo "✅ Файл .env создан вручную"
fi

echo ""
echo "📋 Содержимое .env файла:"
cat .env

echo ""
echo "⚠️  Если нужно изменить настройки, отредактируйте файл:"
echo "   nano .env"
echo "   или"
echo "   vim .env"