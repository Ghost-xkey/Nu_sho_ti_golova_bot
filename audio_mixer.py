import os
import subprocess
import tempfile
import random
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AudioMixer:
    """Миксер для создания частушек с подложкой и даккингом"""
    
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = Path(assets_dir)
        self.backing_dir = self.assets_dir / "backing"
        self.temp_dir = self.assets_dir / "temp"
        
        # Создаем папки если их нет
        self.backing_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройки по умолчанию
        self.default_backing_type = "garmon"  # гармошка
        self.default_ducking = "soft"  # мягкий даккинг
        self.default_backing_volume = -10  # -10 dB относительно голоса
        
        # Настройки даккинга
        self.ducking_settings = {
            "soft": {
                "threshold": -20,
                "ratio": 3,
                "attack": 50,
                "release": 200
            },
            "medium": {
                "threshold": -15,
                "ratio": 5,
                "attack": 30,
                "release": 150
            },
            "strong": {
                "threshold": -10,
                "ratio": 8,
                "attack": 20,
                "release": 100
            }
        }

    def create_chastushka_audio(
        self, 
        text: str, 
        backing_type: str = None,
        ducking: str = None,
        backing_volume: int = None
    ) -> Optional[str]:
        """
        Создает аудио частушки с подложкой
        
        Args:
            text: Текст частушки
            backing_type: Тип подложки (garmon, balalaika, beat)
            ducking: Уровень даккинга (soft, medium, strong)
            backing_volume: Громкость подложки в dB
            
        Returns:
            Путь к созданному аудио файлу или None при ошибке
        """
        try:
            # Используем настройки по умолчанию если не указаны
            backing_type = backing_type or self.default_backing_type
            ducking = ducking or self.default_ducking
            backing_volume = backing_volume or self.default_backing_volume
            
            logger.info(f"Создаем частушку: текст={text[:50]}..., подложка={backing_type}, даккинг={ducking}")
            
            # 1. Генерируем TTS
            voice_file = self._generate_tts(text)
            if not voice_file:
                logger.error("Не удалось сгенерировать TTS")
                return None
            
            # 2. Получаем подложку
            backing_file = self._get_backing_track(backing_type)
            if not backing_file:
                logger.error(f"Не найдена подложка типа {backing_type}")
                return None
            
            # 3. Создаем финальный микс
            output_file = self._mix_audio(voice_file, backing_file, ducking, backing_volume)
            
            # 4. Очищаем временные файлы
            self._cleanup_temp_files([voice_file])
            
            return output_file
            
        except Exception as e:
            logger.error(f"Ошибка при создании аудио частушки: {e}")
            return None

    def _generate_tts(self, text: str) -> Optional[str]:
        """Генерирует TTS из текста с поддержкой специальных обозначений"""
        try:
            from gtts import gTTS
            
            # Создаем временный файл
            temp_file = self.temp_dir / f"voice_{random.randint(1000, 9999)}.mp3"
            
            # Обрабатываем специальные обозначения
            processed_text = self._process_speech_marks(text)
            
            # Генерируем TTS
            tts = gTTS(text=processed_text, lang='ru', slow=False)
            tts.save(str(temp_file))
            
            logger.info(f"TTS сохранен в {temp_file} (обработанный текст: {processed_text[:50]}...)")
            return str(temp_file)
            
        except Exception as e:
            logger.error(f"Ошибка генерации TTS: {e}")
            return None

    def _process_speech_marks(self, text: str) -> str:
        """Обрабатывает специальные обозначения для управления речью"""
        import re
        
        # Убираем специальные символы для TTS, но сохраняем их эффект
        processed = text
        
        # Обрабатываем ударения (+Ехал -> Ехал с ударением)
        # gTTS не поддерживает SSML, поэтому просто убираем +
        processed = re.sub(r'\+([аеёиоуыэюя])', r'\1', processed, flags=re.IGNORECASE)
        
        # Обрабатываем тайминг начала (- и --)
        # Убираем дефисы в начале
        processed = re.sub(r'^-+', '', processed)
        
        # Обрабатываем ускорение (!)
        # Убираем восклицательные знаки в начале
        processed = re.sub(r'^!+', '', processed)
        
        # Обрабатываем паузы - заменяем на более длинные паузы
        # Точка = короткая пауза, запятая = очень короткая пауза
        processed = processed.replace('.', '...')  # Увеличиваем паузы после точек
        processed = processed.replace(',', '..')   # Увеличиваем паузы после запятых
        
        # Убираем лишние пробелы
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        return processed

    def _get_backing_track(self, backing_type: str) -> Optional[str]:
        """Получает файл подложки"""
        # Приоритетно ищем пользовательский файл Sample [music].mp3
        sample_file = self.backing_dir / "Sample [music].mp3"
        if sample_file.exists():
            logger.info(f"Используем пользовательский файл: {sample_file}")
            return str(sample_file)
        
        # Если нет пользовательского файла, ищем по типу
        backing_files = list(self.backing_dir.glob(f"{backing_type}*.mp3"))
        backing_files.extend(list(self.backing_dir.glob(f"{backing_type}*.wav")))
        backing_files.extend(list(self.backing_dir.glob(f"{backing_type}*.ogg")))
        
        if not backing_files:
            logger.warning(f"Не найдены файлы подложки для типа {backing_type}")
            # Возвращаем первый доступный файл
            all_backing = list(self.backing_dir.glob("*"))
            if all_backing:
                return str(all_backing[0])
            return None
        
        # Выбираем случайный файл
        return str(random.choice(backing_files))

    def _mix_audio(
        self, 
        voice_file: str, 
        backing_file: str, 
        ducking: str, 
        backing_volume: int
    ) -> Optional[str]:
        """Смешивает голос с подложкой используя ffmpeg"""
        try:
            output_file = self.temp_dir / f"chastushka_{random.randint(1000, 9999)}.ogg"
            
            # Получаем длительность голоса
            voice_duration = self._get_audio_duration(voice_file)
            if not voice_duration:
                logger.error("Не удалось получить длительность голоса")
                return None
            
            # Настройки даккинга
            duck_settings = self.ducking_settings[ducking]
            
            # Фиксированная длительность: 21 секунда (длительность аудио файла)
            total_duration = 21.0
            
            # Команда ffmpeg для микширования с даккингом, задержкой голоса и фиксированной длительностью
            cmd = [
                'ffmpeg', '-y',  # -y для перезаписи без подтверждения
                '-i', voice_file,  # Входной голос
                '-i', backing_file,  # Входная подложка
                '-filter_complex', 
                f'[0]adelay=7000|7000[voice_delayed];'  # Задержка голоса на 7 секунд
                f'[voice_delayed]loudnorm,atempo=1.1[voice];'  # Нормализация + ускорение голоса 1.1x
                f'[1]volume={backing_volume}dB,aloop=loop=-1:size=2e+09[backing];'  # Подложка с громкостью и зацикливанием
                f'[backing]acompressor=threshold={duck_settings["threshold"]}dB:ratio={duck_settings["ratio"]}:attack={duck_settings["attack"]}:release={duck_settings["release"]}[ducked];'  # Даккинг
                f'[voice][ducked]amix=inputs=2:dropout_transition=0[out]',  # Микширование без ограничения длительности
                '-map', '[out]',
                '-t', str(total_duration),  # Ограничиваем длительность на уровне ffmpeg
                '-c:a', 'libopus',  # Кодек Opus для Telegram
                '-b:a', '64k',  # Битрейт
                '-ar', '48000',  # Частота дискретизации
                '-ac', '1',  # Моно
                str(output_file)
            ]
            
            logger.info(f"Выполняем ffmpeg команду с задержкой голоса на 7 секунд: {' '.join(cmd)}")
            
            # Выполняем команду
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60  # Таймаут 60 секунд
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg ошибка: {result.stderr}")
                return None
            
            logger.info(f"Аудио частушка создана с 7-секундным вступлением: {output_file}")
            return str(output_file)
            
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg превысил таймаут")
            return None
        except Exception as e:
            logger.error(f"Ошибка микширования аудио: {e}")
            return None

    def _get_audio_duration(self, audio_file: str) -> Optional[float]:
        """Получает длительность аудио файла"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                logger.error(f"Ошибка получения длительности: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при получении длительности аудио: {e}")
            return None

    def _cleanup_temp_files(self, files: list):
        """Удаляет временные файлы"""
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Удален временный файл: {file_path}")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {file_path}: {e}")

    def create_simple_mix(self, voice_file: str, backing_file: str) -> Optional[str]:
        """Простое микширование без даккинга (для тестов)"""
        try:
            output_file = self.temp_dir / f"simple_mix_{random.randint(1000, 9999)}.ogg"
            
            cmd = [
                'ffmpeg', '-y',
                '-i', voice_file,
                '-i', backing_file,
                '-filter_complex',
                f'[0]loudnorm[voice];'
                f'[1]volume=-12dB,aloop=loop=-1:size=2e+09[backing];'
                f'[voice][backing]amix=inputs=2:duration=first[out]',
                '-map', '[out]',
                '-c:a', 'libopus',
                '-b:a', '64k',
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return str(output_file)
            else:
                logger.error(f"Простое микширование не удалось: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка простого микширования: {e}")
            return None

    def create_voice_only(self, text: str) -> Optional[str]:
        """Создает только голос без подложки (для тестирования)"""
        try:
            # Генерируем TTS
            voice_file = self._generate_tts(text)
            if not voice_file:
                return None
            
            # Конвертируем в формат для Telegram
            output_file = self.temp_dir / f"voice_only_{random.randint(1000, 9999)}.ogg"
            
            cmd = [
                'ffmpeg', '-y',
                '-i', voice_file,
                '-filter:a', 'atempo=1.1',  # Ускоряем голос до 1.1x
                '-c:a', 'libopus',
                '-b:a', '64k',
                '-ar', '48000',
                '-ac', '1',
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Очищаем временный TTS файл
            self._cleanup_temp_files([voice_file])
            
            if result.returncode == 0:
                return str(output_file)
            else:
                logger.error(f"Конвертация голоса не удалась: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка создания голоса: {e}")
            return None

    def get_available_backing_tracks(self) -> dict:
        """Возвращает список доступных подложек"""
        tracks = {}
        
        for file_path in self.backing_dir.glob("*"):
            if file_path.is_file():
                # Определяем тип по имени файла
                name = file_path.stem.lower()
                if "sample" in name and "music" in name:
                    track_type = "user_music"  # Пользовательская музыка
                elif "garmon" in name or "гармон" in name:
                    track_type = "garmon"
                elif "balalaika" in name or "балалайк" in name:
                    track_type = "balalaika"
                elif "beat" in name or "бит" in name:
                    track_type = "beat"
                else:
                    track_type = "unknown"
                
                if track_type not in tracks:
                    tracks[track_type] = []
                tracks[track_type].append(str(file_path))
        
        return tracks


# Пример использования
if __name__ == "__main__":
    mixer = AudioMixer()
    
    # Проверяем доступные подложки
    tracks = mixer.get_available_backing_tracks()
    print("Доступные подложки:", tracks)
    
    # Тестируем создание частушки
    test_text = "Жизнь как зебра — полосатая,\nты как старая батарейка,\nжить — дело святое,\nполучилось — вот это да!"
    
    print(f"\nСоздаем тестовую частушку...")
    result = mixer.create_chastushka_audio(test_text)
    
    if result:
        print(f"Частушка создана: {result}")
    else:
        print("Не удалось создать частушку")
