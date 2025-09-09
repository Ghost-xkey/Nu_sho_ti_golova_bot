#!/usr/bin/env python3
"""
Скрипт для создания тестовых гармошечных подложек
Использует ffmpeg для генерации простых музыкальных лупов
"""

import subprocess
import os
from pathlib import Path

def create_garmon_backing():
    """Создает простую гармошечную подложку"""
    assets_dir = Path("assets/backing")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = assets_dir / "garmon_test.mp3"
    
    # Создаем простую гармошечную мелодию с помощью ffmpeg
    # Генерируем синусоидальные волны на разных частотах для имитации гармошки
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'sine=frequency=220:duration=15',  # Ля (A3)
        '-f', 'lavfi', 
        '-i', 'sine=frequency=277:duration=15',  # До# (C#4)
        '-f', 'lavfi',
        '-i', 'sine=frequency=330:duration=15',  # Ми (E4)
        '-filter_complex',
        '[0][1][2]amix=inputs=3:duration=15:weights=0.3 0.4 0.3[out]',
        '-map', '[out]',
        '-c:a', 'libmp3lame',
        '-b:a', '128k',
        '-ar', '44100',
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Создана гармошечная подложка: {output_file}")
            return str(output_file)
        else:
            print(f"❌ Ошибка создания подложки: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при создании подложки")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_balalaika_backing():
    """Создает простую балалаечную подложку"""
    assets_dir = Path("assets/backing")
    output_file = assets_dir / "balalaika_test.mp3"
    
    # Балалаечная мелодия - более высокие частоты
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'sine=frequency=440:duration=12',  # Ля (A4)
        '-f', 'lavfi',
        '-i', 'sine=frequency=554:duration=12',  # До# (C#5)
        '-f', 'lavfi',
        '-i', 'sine=frequency=659:duration=12',  # Ми (E5)
        '-filter_complex',
        '[0][1][2]amix=inputs=3:duration=12:weights=0.4 0.3 0.3[out]',
        '-map', '[out]',
        '-c:a', 'libmp3lame',
        '-b:a', '128k',
        '-ar', '44100',
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Создана балалаечная подложка: {output_file}")
            return str(output_file)
        else:
            print(f"❌ Ошибка создания подложки: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_beat_backing():
    """Создает простую битовую подложку"""
    assets_dir = Path("assets/backing")
    output_file = assets_dir / "beat_test.mp3"
    
    # Простой бит - бас + хай-хэт
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'sine=frequency=60:duration=10',   # Низкий бас
        '-f', 'lavfi',
        '-i', 'sine=frequency=8000:duration=10', # Хай-хэт
        '-filter_complex',
        '[0][1]amix=inputs=2:duration=10:weights=0.7 0.3[out]',
        '-map', '[out]',
        '-c:a', 'libmp3lame',
        '-b:a', '128k',
        '-ar', '44100',
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Создана битовая подложка: {output_file}")
            return str(output_file)
        else:
            print(f"❌ Ошибка создания подложки: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def main():
    """Создает все тестовые подложки"""
    print("🎵 Создаем тестовые музыкальные подложки...")
    
    # Проверяем наличие ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ffmpeg не найден. Установите ffmpeg для создания подложек.")
        return
    
    # Создаем подложки
    garmon = create_garmon_backing()
    balalaika = create_balalaika_backing()
    beat = create_beat_backing()
    
    print("\n📁 Созданные файлы:")
    if garmon:
        print(f"  - {garmon}")
    if balalaika:
        print(f"  - {balalaika}")
    if beat:
        print(f"  - {beat}")
    
    print("\n🎉 Готово! Теперь можно тестировать частушки.")

if __name__ == "__main__":
    main()
