"""Модуль для взаимодействия с API погоды.

Этот модуль предоставляет функциональность для получения данных о погоде
через OpenWeatherMap API. Поддерживает асинхронные запросы и обработку ошибок.

Основные компоненты:
    - WeatherAPI: Класс для взаимодействия с API погоды

Пример использования:
    api = WeatherAPI(config_path)
    weather_data = await api.get_weather(city_id=123456)
    temperature = weather_data['main']['temp']

Attributes:
    logger: Logger для записи информации о запросах и ошибках

Note:
    Для работы требуется API ключ OpenWeatherMap.
    Ключ должен быть указан в конфигурационном файле.
"""

import os

from pathlib import Path
from typing import Dict
from functools import lru_cache

import requests
import yaml
import aiohttp

from weather_monitor.exceptions import WeatherAPIError


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
        self.session = requests.Session()  # Переиспользование сессии

    @staticmethod
    @lru_cache  # Кэширование конфига
    def _load_config(config_path: Path) -> Dict:
        """Загружает и кэширует конфигурацию из yaml файла.
        Args:
            config_path (Path): Путь к файлу конфигурации
        Returns:
            Dict: Загруженная конфигурация
        """
        return yaml.safe_load(config_path.read_text())

    async def get_weather(self, city_id: int) -> dict:
        """Получение данных о погоде для конкретного города.
        Args:
            city_id (int): ID города в системе OpenWeatherMap
        Returns:
            dict: Данные о погоде
        Raises:
            WeatherAPIError: При ошибке получения данных.
        """
        try:
            params = {
                'id': city_id,
                'appid': self.api_key,
                'units': 'metric'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise WeatherAPIError(
                f"Error fetching weather data for city ID {city_id}: {e}"
            ) from e
