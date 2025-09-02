#!/bin/bash

# Скрипт для деплоя Telegram бота на сервер

set -e

echo "🚀 Начинаем деплой Telegram бота..."

# Проверяем, что мы на сервере
if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then
    echo "❌ Этот скрипт должен запускаться на сервере!"
    exit 1
fi

# Создаем директорию для бота
BOT_DIR="/home/ubuntu/Nu_sho_ti_golova_bot"
mkdir -p $BOT_DIR
cd $BOT_DIR

# Обновляем систему
echo "📦 Обновляем систему..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
echo "🔧 Устанавливаем зависимости..."
sudo apt install -y python3 python3-pip python3-venv git

# Создаем виртуальное окружение
echo "🐍 Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости Python
echo "📚 Устанавливаем Python зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# Создаем директорию для данных
mkdir -p data

# Устанавливаем systemd сервис
echo "⚙️ Настраиваем systemd сервис..."
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot

echo "✅ Деплой завершен!"
echo "📋 Для запуска бота выполните:"
echo "   sudo systemctl start telegram-bot"
echo "   sudo systemctl status telegram-bot"
echo ""
echo "📋 Для просмотра логов:"
echo "   sudo journalctl -u telegram-bot -f"