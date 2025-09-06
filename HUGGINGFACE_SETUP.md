# Настройка Hugging Face для бесплатной AI-генерации мемов

## Шаг 1: Регистрация на Hugging Face

1. Переходим на [huggingface.co](https://huggingface.co)
2. Нажимаем "Sign Up"
3. Регистрируемся через Google, GitHub или email
4. Подтверждаем email

## Шаг 2: Получение API ключа

1. После входа в аккаунт, переходим в **Settings**
2. Выбираем вкладку **Access Tokens**
3. Нажимаем **"New token"**
4. Выбираем **"Read"** права
5. Копируем полученный токен (начинается с `hf_`)

## Шаг 3: Настройка переменной окружения

### На сервере:
```bash
# Добавляем токен в .env файл
echo "HUGGINGFACE_API_TOKEN=hf_your-token-here" >> .env

# Перезапускаем контейнер
docker restart nu_sho_ti_golova_bot
```

### Локально:
```bash
# В файле .env добавляем:
HUGGINGFACE_API_TOKEN=hf_your-token-here
```

## Шаг 4: Обновляем код

Нужно заменить заглушку в `meme_generator.py`:

```python
# Было:
"Authorization": "Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Стало:
import os
hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
"Authorization": f"Bearer {hf_token}"
```

## Особенности Hugging Face

### ✅ Преимущества:
- **Полностью бесплатный** - без лимитов
- **Высокое качество** - Stable Diffusion модель
- **Быстрая генерация** - 10-30 секунд
- **Без регистрации** - можно использовать без токена (с ограничениями)

### ⚠️ Ограничения:
- **Без токена**: медленнее, может быть очередь
- **С токеном**: быстрее, приоритет в очереди

### 🚀 Модели:
- **Stable Diffusion v1.5** - основная модель
- **Stable Diffusion XL** - лучшее качество
- **DALL-E Mini** - быстрая генерация

## Альтернативные бесплатные сервисы

### 1. **Replicate API**
```python
# Бесплатный тир: 1000 запросов/месяц
url = "https://api.replicate.com/v1/predictions"
headers = {"Authorization": "Token r8_xxxxxxxxxxxxxxxxxxxxxxxx"}
```

### 2. **Stability AI**
```python
# Бесплатный API с регистрацией
url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
headers = {"Authorization": "Bearer sk-xxxxxxxxxxxxxxxxxxxxxxxx"}
```

### 3. **OpenAI DALL-E**
```python
# $5 кредитов при регистрации
url = "https://api.openai.com/v1/images/generations"
headers = {"Authorization": "Bearer sk-xxxxxxxxxxxxxxxxxxxxxxxx"}
```

## Проверка работы

```bash
# Тестируем генерацию мема
docker exec nu_sho_ti_golova_bot python -c "
from meme_generator import meme_generator
print('Testing Hugging Face meme generation...')
result = meme_generator.create_meme_with_huggingface('Гриша шутит про Вадика')
if result:
    print('✅ Hugging Face meme generated successfully!')
    print('Result length:', len(result))
else:
    print('❌ Failed to generate meme')
"
```

## Troubleshooting

### Ошибка 401 (Unauthorized):
- Проверьте правильность API ключа
- Убедитесь, что токен начинается с `hf_`

### Ошибка 503 (Model Loading):
- Модель загружается, подождите 1-2 минуты
- Попробуйте еще раз

### Ошибка 429 (Rate Limit):
- Превышен лимит запросов
- Подождите или получите токен

### Медленная генерация:
- Без токена может быть очередь
- С токеном генерация быстрее

## Готовые промпты для мемов

Система автоматически создает промпты:

```python
# Про Вадика
"funny meme style, cartoon character, fisherman character, fishing rod, beer, funny expression, high quality, detailed, meme format"

# Про Лёху  
"meme format, funny character, character with hookah, relaxed pose, funny expression, internet humor, cartoon style"

# Про Гришу
"viral meme style, robot character, AI, funny expression, tech humor, text overlay, internet meme, cartoon"
```

## Fallback система

Если Hugging Face не работает, система автоматически переключается на:
1. **Craiyon** - бесплатный AI
2. **Простые мемы** - локальная генерация  
3. **Imgflip** - готовые шаблоны

**Все бесплатно и без лимитов!** 🎉
