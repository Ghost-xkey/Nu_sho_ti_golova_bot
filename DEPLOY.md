# 🚀 Инструкция по деплою Telegram бота

## 📋 Подготовка

### 1. Подготовка сервера
- Ubuntu 20.04+ или Debian 11+
- Минимум 1GB RAM
- 10GB свободного места
- Открытые порты (если нужен веб-интерфейс)

### 2. Подготовка файлов
Убедитесь, что у вас есть все файлы проекта:
- `main.py` - основной файл бота
- `requirements.txt` - зависимости Python
- `config.py` - конфигурация
- Все остальные файлы проекта

## 🐳 Способ 1: Docker (Рекомендуется)

### Шаг 1: Загрузка файлов на сервер
```bash
# Клонируем репозиторий или загружаем файлы
git clone <your-repo-url>
cd Nu_sho_ti_golova_bot

# Или загружаем через scp
scp -r . user@server:/home/user/Nu_sho_ti_golova_bot
```

### Шаг 2: Настройка переменных окружения
```bash
# Проверяем, что мы в правильной директории
pwd
ls -la | grep env

# Копируем пример конфигурации
cp env.example .env

# Редактируем конфигурацию
nano .env
```

**Если файл env.example не найден:**
```bash
# Создаем .env файл вручную
cat > .env << EOF
TOKEN=7255987995:AAGaXiV6oYBY1UCgizHPqVZuxVhsAKqIA94
CHAT_ID=-573460520
DB_PATH=bot_database.db
EOF
```

Заполните `.env` файл:
```env
TOKEN=7255987995:AAGaXiV6oYBY1UCgizHPqVZuxVhsAKqIA94
CHAT_ID=-573460520
DB_PATH=bot_database.db
```

### Шаг 3: Запуск через Docker
```bash
# Делаем скрипт исполняемым
chmod +x deploy-docker.sh

# Запускаем деплой
./deploy-docker.sh
```

### Управление Docker контейнером
```bash
# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose stop

# Запуск
docker-compose start

# Перезапуск
docker-compose restart

# Обновление
docker-compose pull
docker-compose up -d
```

## ⚙️ Способ 2: Systemd сервис

### Шаг 1: Загрузка и настройка
```bash
# Загружаем файлы на сервер
scp -r . user@server:/home/user/Nu_sho_ti_golova_bot

# Подключаемся к серверу
ssh user@server
cd /home/user/Nu_sho_ti_golova_bot
```

### Шаг 2: Автоматический деплой
```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем деплой
./deploy.sh
```

### Шаг 3: Ручная настройка (если нужно)
```bash
# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Настраиваем systemd сервис
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
```

### Управление systemd сервисом
```bash
# Запуск
sudo systemctl start telegram-bot

# Остановка
sudo systemctl stop telegram-bot

# Перезапуск
sudo systemctl restart telegram-bot

# Статус
sudo systemctl status telegram-bot

# Просмотр логов
sudo journalctl -u telegram-bot -f

# Автозапуск при загрузке
sudo systemctl enable telegram-bot
```

## 🔧 Способ 3: Ручной запуск

### Шаг 1: Установка зависимостей
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и pip
sudo apt install -y python3 python3-pip python3-venv

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### Шаг 2: Запуск бота
```bash
# Запускаем бота
python main.py
```

### Шаг 3: Запуск в фоне (screen/tmux)
```bash
# Устанавливаем screen
sudo apt install screen

# Создаем новую сессию
screen -S telegram-bot

# Запускаем бота
source venv/bin/activate
python main.py

# Отключаемся от сессии (Ctrl+A, затем D)
# Подключаемся обратно: screen -r telegram-bot
```

## 📊 Мониторинг и логи

### Docker
```bash
# Просмотр логов в реальном времени
docker-compose logs -f

# Просмотр логов за последний час
docker-compose logs --since=1h

# Статистика контейнера
docker stats
```

### Systemd
```bash
# Логи в реальном времени
sudo journalctl -u telegram-bot -f

# Логи за последний час
sudo journalctl -u telegram-bot --since=1h

# Статус сервиса
sudo systemctl status telegram-bot
```

## 🔄 Обновление бота

### Docker
```bash
# Останавливаем контейнер
docker-compose down

# Обновляем код
git pull  # или загружаем новые файлы

# Пересобираем и запускаем
docker-compose up -d --build
```

### Systemd
```bash
# Останавливаем сервис
sudo systemctl stop telegram-bot

# Обновляем код
git pull  # или загружаем новые файлы

# Запускаем сервис
sudo systemctl start telegram-bot
```

## 🛡️ Безопасность

### Рекомендации:
1. **Используйте переменные окружения** для токенов
2. **Настройте firewall** (ufw)
3. **Регулярно обновляйте** систему
4. **Используйте SSH ключи** вместо паролей
5. **Настройте логирование** для мониторинга

### Настройка firewall:
```bash
# Устанавливаем ufw
sudo apt install ufw

# Разрешаем SSH
sudo ufw allow ssh

# Разрешаем HTTP/HTTPS (если нужен веб-интерфейс)
sudo ufw allow 80
sudo ufw allow 443

# Включаем firewall
sudo ufw enable
```

## 🆘 Решение проблем

### Бот не запускается:
1. Проверьте логи: `docker-compose logs` или `sudo journalctl -u telegram-bot`
2. Проверьте токен в конфигурации
3. Убедитесь, что все зависимости установлены

### Ошибки подключения:
1. Проверьте интернет-соединение
2. Проверьте токен бота
3. Проверьте chat_id

### Проблемы с правами:
```bash
# Исправляем права на файлы
chmod +x deploy.sh
chmod +x deploy-docker.sh

# Для systemd сервиса
sudo chown -R $USER:$USER /home/$USER/Nu_sho_ti_golova_bot
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи
2. Убедитесь в правильности конфигурации
3. Проверьте доступность сервера
4. Обратитесь к документации aiogram
