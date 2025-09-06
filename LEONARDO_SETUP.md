# Настройка Leonardo.ai для генерации мемов

## Шаг 1: Регистрация на Leonardo.ai

1. Переходим на [leonardo.ai](https://leonardo.ai)
2. Нажимаем "Sign Up" или "Get Started"
3. Регистрируемся через Google, Discord или email
4. Подтверждаем email (если нужно)

## Шаг 2: Получение API ключа

1. После входа в аккаунт, переходим в **Settings**
2. Выбираем вкладку **API Keys**
3. Нажимаем **"Create API Key"**
4. Копируем полученный токен (начинается с `sk-`)

## Шаг 3: Настройка переменной окружения

### На сервере:
```bash
# Добавляем токен в .env файл
echo "LEONARDO_API_TOKEN=sk-your-token-here" >> .env

# Перезапускаем контейнер
docker restart nu_sho_ti_golova_bot
```

### Локально:
```bash
# В файле .env добавляем:
LEONARDO_API_TOKEN=sk-your-token-here
```

## Шаг 4: Проверка работы

```bash
# Тестируем генерацию мема
docker exec nu_sho_ti_golova_bot python -c "
from meme_generator import meme_generator
print('Testing Leonardo.ai meme generation...')
result = meme_generator.create_meme_with_leonardo('Гриша шутит про Вадика')
if result:
    print('✅ Leonardo.ai meme generated successfully!')
    print('Result length:', len(result))
else:
    print('❌ Failed to generate meme')
"
```

## Особенности Leonardo.ai

### ✅ Преимущества:
- **Высокое качество** - профессиональные AI модели
- **Быстрая генерация** - 10-30 секунд
- **Уникальные мемы** - каждый раз разные
- **Персонализация** - учитывает контекст чата

### ⚠️ Ограничения:
- **Бесплатный план**: 150 токенов в день
- **Требует регистрацию** - нужно подтвердить email
- **API ключ** - нужно получить токен

### 💰 Тарифы:
- **Free**: 150 токенов/день (достаточно для тестов)
- **Starter**: $10/месяц - 8500 токенов/день
- **Growth**: $24/месяц - 25000 токенов/день

## Готовые промпты для мемов

Система автоматически создает промпты на основе контекста:

- **Про Вадика**: "fisherman character, fishing rod, beer, funny expression"
- **Про Лёху**: "character with hookah, relaxed pose, funny expression"  
- **Про Гришу**: "robot character, AI, funny expression, tech humor"

## Troubleshooting

### Ошибка 401 (Unauthorized):
- Проверьте правильность API ключа
- Убедитесь, что токен добавлен в .env

### Ошибка 429 (Rate Limit):
- Превышен лимит токенов
- Подождите до следующего дня или обновите план

### Ошибка 500 (Server Error):
- Проблемы на стороне Leonardo.ai
- Попробуйте позже

### Медленная генерация:
- Leonardo.ai может занимать 10-60 секунд
- Это нормально для AI генерации

## Альтернативы

Если Leonardo.ai не работает, система автоматически переключается на:
1. **Craiyon** - бесплатный AI
2. **Простые мемы** - локальная генерация
3. **Imgflip** - готовые шаблоны
