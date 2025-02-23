from pathlib import Path
from typing import Dict, Any
from functools import lru_cache
import os

import requests
import yaml
# from dotenv import load_dotenv


class WeatherAPI:
    """Класс для взаимодействия с OpenWeatherMap API.

    Предоставляет методы для получения данных о погоде для заданных городов.
    Использует кэширование конфигурации и
    переиспользование сессии для оптимизации.

    Attributes:
        config (Dict): Конфигурационные данные из yaml файла
        session (requests.Session): Сессия для HTTP-запросов
    """

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('OPENWEATHERMAP_KEY')
        self.base_url = self.config['base_url']
        self.session = requests.Session()  # Переиспользование сессии

    @staticmethod
    @lru_cache  # Кэширование конфига
    def _load_config(config_path: Path) -> Dict:
        """Загружает и кэширует конфигурацию из yaml файла.
        Args:
            config_path (Path): Путь к файлу конфигурации
        Returns:
            Dict: Загруженная конфигурация
        """
        return yaml.safe_load(config_path.read_text())

    def get_weather(self, city_id: int) -> Dict[str, Any]:
        """Получение данных о погоде для конкретного города.
        Args:
            city_id (int): ID города в системе OpenWeatherMap
        Returns:
            Dict[str, Any]: Данные о погоде в формате JSON
        Raises:
            requests.exceptions.HTTPError: При ошибке запроса к API. """
        params = {
            'id': city_id,
            'appid': self.api_key,
            'units': 'metric'  # Использование метрической системы
        }
        # response = requests.get(self.base_url, params=params)
        with self.session.get(self.base_url, params=params) as response:
            response.raise_for_status()
        return response.json()
