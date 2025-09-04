# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем системные зависимости и ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем папку для данных и пользователя для безопасности
RUN mkdir -p /app/data && \
    useradd --create-home --shell /bin/bash bot && \
    chown -R bot:bot /app
USER bot

# Запускаем бота
CMD ["python", "main.py"]