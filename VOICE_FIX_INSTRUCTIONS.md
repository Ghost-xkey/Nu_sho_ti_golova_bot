# 🎤 Исправление голосовых сообщений

## 🔧 **Проблема была найдена и исправлена!**

**Проблема:** Обработчик голосовых сообщений был размещен **ПОСЛЕ** общего обработчика, поэтому общий обработчик перехватывал все сообщения, включая голосовые.

**Решение:** Переместили обработчик голосовых **ПЕРЕД** общим обработчиком.

## 📋 **Что нужно сделать на сервере:**

### **1. Обновите handlers.py:**
```bash
nano handlers.py
```

### **2. Найдите строку 1326 (общий обработчик):**
```python
# AI-чат обработчик текстовых сообщений
@router.message()
async def handle_ai_message(message: types.Message):
```

### **3. Добавьте ПЕРЕД этой строкой:**
```python
# AI-чат обработчик голосовых сообщений
@router.message(lambda message: message.voice is not None)
async def handle_voice_message(message: types.Message):
    """
    Обработчик для AI-чата - отвечает на голосовые сообщения
    """
    try:
        # Проверяем, включен ли AI и голосовые сообщения
        if not AI_ENABLED or not VOICE_ENABLED:
            return
            
        # Получаем информацию о пользователе
        username = message.from_user.username or message.from_user.first_name or "Пользователь"
        chat_id = str(message.chat.id)
        
        logging.info(f"Processing voice message from {username}")
        
        # Скачиваем голосовое сообщение
        voice_file = await message.bot.get_file(message.voice.file_id)
        voice_data = await message.bot.download_file(voice_file.file_path)
        
        # Преобразуем голос в текст
        text_from_voice = speech_kit.voice_to_text(voice_data.read())
        
        if not text_from_voice:
            logging.warning("Failed to convert voice to text")
            return
            
        logging.info(f"Voice converted to text: {text_from_voice[:50]}...")
        
        # Проверяем, должен ли AI ответить
        if yandex_ai.should_respond(text_from_voice, chat_id):
            logging.info(f"AI responding to voice message from {username}")
            
            # Генерируем ответ
            ai_response = yandex_ai.generate_response(text_from_voice, chat_id, username)
            
            if ai_response:
                # Преобразуем ответ в голос
                voice_response = speech_kit.text_to_voice(ai_response)
                
                if voice_response:
                    # Отправляем голосовой ответ
                    await message.answer_voice(
                        voice=voice_response,
                        caption=f"🎤 {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}"
                    )
                    logging.info(f"AI voice response sent: {ai_response[:50]}...")
                else:
                    # Если не удалось создать голос, отправляем текстом
                    await message.answer(f"🎤 {ai_response}")
                    logging.info(f"AI text response sent (voice failed): {ai_response[:50]}...")
            else:
                # Fallback ответ
                fallback_response = yandex_ai.get_random_comment()
                voice_fallback = speech_kit.text_to_voice(fallback_response)
                
                if voice_fallback:
                    await message.answer_voice(voice=voice_fallback)
                else:
                    await message.answer(fallback_response)
                    
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")

```

### **4. Сохраните файл:**
- Нажмите `Ctrl + X`
- Нажмите `Y`
- Нажмите `Enter`

### **5. Перезапустите бота:**
```bash
docker-compose down
docker-compose up --build -d
```

## 🎯 **После исправления в логах должно появиться:**
```
INFO:root:Processing voice message from username
INFO:root:Voice converted to text: ...
INFO:root:AI voice response sent: ...
```

## 🎤 **Готово!**

Теперь бот будет:
- 🎤 **Слушать голосовые** и преобразовывать их в текст
- 🤖 **Отвечать AI** на основе распознанного текста
- 🗣️ **Отправлять голосовые ответы** грубым мужским голосом
- 📝 **Отвечать текстом** на текстовые сообщения

**Протестируйте, отправив голосовое сообщение в группу!** 🚀✨
