#!/usr/bin/env python3
"""Тест TTS функциональности"""

from gtts import gTTS
import os

def test_tts():
    """Тестирует генерацию TTS"""
    text = "Жизнь как зебра — полосатая,\nты как старая батарейка,\nжить — дело святое,\nполучилось — вот это да!"
    
    print(f"Генерируем TTS для текста: {text}")
    
    try:
        # Создаем TTS
        tts = gTTS(text=text, lang='ru', slow=False)
        
        # Сохраняем в файл
        output_file = "test_voice.mp3"
        tts.save(output_file)
        
        if os.path.exists(output_file):
            print(f"✅ TTS успешно создан: {output_file}")
            print(f"Размер файла: {os.path.getsize(output_file)} байт")
            
            # Удаляем тестовый файл
            os.remove(output_file)
            print("✅ Тестовый файл удален")
        else:
            print("❌ Файл не был создан")
            
    except Exception as e:
        print(f"❌ Ошибка TTS: {e}")

if __name__ == "__main__":
    test_tts()
