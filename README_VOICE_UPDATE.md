# 🎤 Обновление голосовых сообщений

## ✅ **Все готово! Нужно только обновить API ключ.**

### **📋 Инструкция для сервера:**

### **1. Обновите бота:**
```bash
git pull origin main
```

### **2. Обновите API ключ:**
```bash
nano config.py
```

Найдите строку:
```python
YANDEX_API_KEY = "YOUR_YANDEX_API_KEY_HERE"
```

Замените на ваш ключ:
```python
YANDEX_API_KEY = "YOUR_YANDEX_API_KEY_HERE"
```

### **3. Перезапустите бота:**
```bash
docker-compose down
docker-compose up --build -d
```

## 🎯 **Готово!**

Бот будет отвечать на голосовые сообщения грубым мужским голосом! 🗣️✨
