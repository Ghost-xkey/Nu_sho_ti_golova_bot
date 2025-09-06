# Ручное обновление бота на сервере

## Проблема
Бот генерирует только простые мемы, потому что токен Hugging Face не загружается в контейнер.

## Решение

### Шаг 1: Подключиться к серверу
```bash
ssh root@92.63.100.172
```

### Шаг 2: Перейти в директорию бота
```bash
cd ~/Nu_sho_ti_golova_bot
```

### Шаг 3: Обновить код
```bash
git pull origin main
```

### Шаг 4: Остановить бота
```bash
docker-compose down
```

### Шаг 5: Запустить с новыми переменными
```bash
docker-compose up -d
```

### Шаг 6: Проверить переменные окружения
```bash
docker exec nu_sho_ti_golova_bot python -c "
import os
print('Hugging Face token:', 'SET' if os.getenv('HUGGINGFACE_API_TOKEN') else 'NOT SET')
print('Yandex API key:', 'SET' if os.getenv('YANDEX_API_KEY') else 'NOT SET')
"
```

### Шаг 7: Протестировать AI-генерацию
```bash
docker exec nu_sho_ti_golova_bot python -c "
from meme_generator import meme_generator
print('Testing Hugging Face...')
result = meme_generator.create_meme_with_huggingface('Гриша шутит про Вадика')
print('Success:', bool(result))
"
```

## Альтернативное решение

Если переменные все еще не загружаются, можно добавить токен прямо в код:

### 1. Отредактировать meme_generator.py
```bash
docker exec nu_sho_ti_golova_bot nano /app/meme_generator.py
```

### 2. Найти строку с токеном и заменить
```python
# Было:
hf_token = os.getenv("HUGGINGFACE_API_TOKEN")

# Стало:
hf_token = os.getenv("HUGGINGFACE_API_TOKEN") or "YOUR_HUGGINGFACE_TOKEN_HERE"
```

### 3. Перезапустить контейнер
```bash
docker restart nu_sho_ti_golova_bot
```

## Проверка работы

После обновления протестируй в Telegram:
- "покажи мем про Вадика"
- "сделай мем про Лёху"

Бот должен генерировать AI-мемы вместо простых текстовых!

## Логи для диагностики

Если не работает, проверь логи:
```bash
docker logs nu_sho_ti_golova_bot --tail 50
```

Ищи ошибки:
- `Hugging Face API error`
- `401 Unauthorized`
- `Token not configured`
