import requests
import random
import logging
from typing import List, Dict, Optional
from config import KINOPOISK_API_TOKEN

class MovieService:
    """Сервис для работы с API Кинопоиска"""
    
    def __init__(self):
        self.api_token = KINOPOISK_API_TOKEN
        self.base_url = "https://api.kinopoisk.dev"
        self.headers = {
            "X-API-KEY": self.api_token,
            "Content-Type": "application/json"
        }
        
        # Популярные жанры
        self.genres = {
            "комедия": "комедия",
            "драма": "драма", 
            "триллер": "триллер",
            "боевик": "боевик",
            "фантастика": "фантастика",
            "ужасы": "ужасы",
            "детектив": "детектив",
            "мелодрама": "мелодрама",
            "приключения": "приключения",
            "фэнтези": "фэнтези",
            "криминал": "криминал",
            "биография": "биография",
            "мультфильм": "мультфильм",
            "семейный": "семейный"
        }
        
        # Настроения и соответствующие жанры
        self.mood_genres = {
            "грустно": ["драма", "мелодрама", "биография"],
            "весело": ["комедия", "приключения", "мультфильм"],
            "хочется подумать": ["драма", "криминал", "детектив"],
            "хочется поспать": ["драма", "мелодрама", "биография"],
            "хочется адреналина": ["боевик", "триллер", "ужасы"],
            "романтично": ["мелодрама", "комедия", "семейный"],
            "с детьми": ["семейный", "мультфильм", "приключения"]
        }

    def search_movies(self, genre: str = None, year: int = None, rating_min: float = None, 
                     limit: int = 10) -> List[Dict]:
        """Поиск фильмов по параметрам"""
        try:
            url = f"{self.base_url}/v1.4/movie"
            params = {
                "limit": limit,
                "page": 1
            }
            
            if genre:
                params["genres.name"] = genre
            if year:
                params["year"] = year
            if rating_min:
                params["rating.kp"] = f"{rating_min}-10"
                
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("docs", [])
            else:
                logging.error(f"Kinopoisk API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Error searching movies: {e}")
            return []

    def get_random_movie(self, genre: str = None) -> Optional[Dict]:
        """Получить случайный фильм"""
        try:
            url = f"{self.base_url}/v1.4/movie/random"
            params = {}
            
            if genre:
                params["genres.name"] = genre
                
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Kinopoisk API error: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting random movie: {e}")
            return None

    def search_by_name(self, name: str) -> List[Dict]:
        """Поиск фильма по названию"""
        try:
            url = f"{self.base_url}/v1.4/movie/search"
            params = {
                "query": name,
                "limit": 5,
                "page": 1
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("docs", [])
            else:
                logging.error(f"Kinopoisk API error: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Error searching movie by name: {e}")
            return []

    def get_recommendations_by_mood(self, mood: str) -> List[Dict]:
        """Получить рекомендации по настроению"""
        try:
            # Определяем жанры по настроению
            mood_genres = self.mood_genres.get(mood, ["драма", "комедия"])
            
            # Выбираем случайный жанр из подходящих
            genre = random.choice(mood_genres)
            
            # Ищем фильмы с хорошим рейтингом
            movies = self.search_movies(genre=genre, rating_min=7.0, limit=5)
            
            # Если мало фильмов, берем без ограничения по рейтингу
            if len(movies) < 3:
                movies = self.search_movies(genre=genre, limit=5)
                
            return movies
            
        except Exception as e:
            logging.error(f"Error getting mood recommendations: {e}")
            return []

    def format_movie_info(self, movie: Dict) -> str:
        """Форматировать информацию о фильме"""
        try:
            name = movie.get("name", "Неизвестно")
            name_en = movie.get("alternativeName", "")
            year = movie.get("year", "")
            rating_data = movie.get("rating", {})
            rating = rating_data.get("kp", 0) if rating_data else 0
            description = movie.get("description", "Описание отсутствует")
            poster_data = movie.get("poster", {})
            poster_url = poster_data.get("url", "") if poster_data else ""
            
            # Обрезаем описание если слишком длинное
            if description and len(description) > 200:
                description = description[:200] + "..."
                
            # Формируем строку
            info = f"🎬 **{name}**"
            if name_en:
                info += f" ({name_en})"
            if year:
                info += f" ({year})"
            if rating:
                info += f" ⭐ {rating}"
                
            info += f"\n📝 {description}"
            
            if poster_url:
                info += f"\n🖼️ {poster_url}"
                
            return info
            
        except Exception as e:
            logging.error(f"Error formatting movie info: {e}")
            return f"🎬 {movie.get('name', 'Неизвестный фильм')}"

    def get_genre_recommendations(self, genre: str) -> List[Dict]:
        """Получить рекомендации по жанру"""
        try:
            # Нормализуем жанр
            normalized_genre = self.genres.get(genre.lower(), genre)
            
            # Ищем фильмы с хорошим рейтингом
            movies = self.search_movies(genre=normalized_genre, rating_min=7.0, limit=5)
            
            # Если мало фильмов, берем без ограничения по рейтингу
            if len(movies) < 3:
                movies = self.search_movies(genre=normalized_genre, limit=5)
                
            return movies
            
        except Exception as e:
            logging.error(f"Error getting genre recommendations: {e}")
            return []

    def get_popular_movies(self, year: int = None) -> List[Dict]:
        """Получить популярные фильмы"""
        try:
            movies = self.search_movies(year=year, rating_min=7.5, limit=5)
            return movies
            
        except Exception as e:
            logging.error(f"Error getting popular movies: {e}")
            return []
