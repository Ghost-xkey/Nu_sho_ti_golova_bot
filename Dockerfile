# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем системные зависимости и ffmpeg (без лишних рекомендаций и с очисткой кэша)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg ca-certificates && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

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