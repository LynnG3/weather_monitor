"""Основной модуль системы мониторинга погоды.

Этот модуль координирует работу всех компонентов системы:
- Сбор данных о погоде через OpenWeatherMap API
- Сохранение данных в формате NetCDF
- Анализ температурных данных
- Отправка уведомлений через Telegram

Пример использования:
    monitor = WeatherMonitor(Path("config/config.yml"))
    asyncio.run(monitor.run())

Note:
    Требуется наличие файла конфигурации и настроенных переменных окружения.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict

import os
import yaml
from dotenv import load_dotenv

from weather_monitor.notifications.telegram_notifier import TelegramNotifier
from weather_monitor.data_collection.data_saver import (
    WeatherDataSaver,
    WeatherRecord
)
from weather_monitor.data_collection.weather_api import WeatherAPI
from weather_monitor.analysis.temperature_analyzer import TemperatureAnalyzer
from weather_monitor.exceptions import WeatherAPIError
# Загрузка переменных окружения
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeatherMonitor:
    """Основной класс мониторинга погоды .

    Координирует работу компонентов: сбор данных,
    сохранение, анализ и отправку уведомлений.

    Attributes:
        config: Конфигурация системы
        weather_api: Клиент API погоды
        data_saver: Компонент сохранения данных
        notifier: Компонент отправки уведомлений
        analyzer: Компонент анализа температуры
    """

    def __init__(self, config_path: Path) -> None:
        """Инициализация монитора погоды.

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config = self._load_config(config_path)
        # Создаем директорию для данных, если она не существует
        data_path = Path(self.config['data_storage']['netcdf_path'])
        data_path.parent.mkdir(parents=True, exist_ok=True)

        self.weather_api = WeatherAPI(config_path)
        self.data_saver = WeatherDataSaver(data_path)

        # Получаем токен и ID чата напрямую из переменных окружения
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        self.notifier = TelegramNotifier(
            bot_token=bot_token,
            chat_id=chat_id
        )
        self.analyzer = TemperatureAnalyzer(
            self.config['temperature_thresholds']
        )

    @staticmethod
    def _load_config(config_path: Path) -> Dict:
        """Загружает конфигурацию из YAML файла.

        Args:
            config_path: Путь к файлу конфигурации

        Returns:
            Dict: Загруженная конфигурация

        Raises:
            yaml.YAMLError: При ошибке парсинга YAML
            FileNotFoundError: Если файл не найден
        """
        try:
            return yaml.safe_load(config_path.read_text())
        except (yaml.YAMLError, FileNotFoundError) as e:
            logger.error("Failed to load config: %s", e)
            raise

    async def process_city_weather(self, city: dict) -> WeatherRecord:
        """Обработка погоды для одного города.

            Args:
            city: Словарь с данными города

        Returns:
            WeatherRecord: Запись с погодными данными

        Raises:
            WeatherAPIError: При ошибке получения данных
            KeyError: При неверном формате данных
        """
        try:
            weather_data = await self.weather_api.get_weather(city['id'])
            return WeatherRecord(
                city_name=city['name'],
                temperature=weather_data['main']['temp'],
                timestamp=datetime.now()
            )
        except WeatherAPIError as e:
            logger.error("Error processing city %s: %s", city['name'], e)
            raise
        except KeyError as e:
            logger.error(
                "Invalid weather data format for city %s: %s",
                city['name'], e
            )
            raise

    def check_temperature_thresholds(self, record: WeatherRecord) -> None:
        """Проверка пороговых значений температуры"""
        thresholds = self.config['temperature_thresholds']
        if record.temperature > thresholds['high']:
            self.notifier.send_temperature_notification(
                record.city_name, record.temperature, thresholds['high'], True
            )
        elif record.temperature < thresholds['low']:
            self.notifier.send_temperature_notification(
                record.city_name, record.temperature, thresholds['low'], False
            )

    async def process_cities(self) -> AsyncGenerator[WeatherRecord, None]:
        """Генератор для обработки городов.

        Yields:
            WeatherRecord: Записи с погодными данными
        """
        for city in self.config['cities']:
            try:
                record = await self.process_city_weather(city)
                yield record
            except Exception as e:
                logger.error("Error processing city: %s", e)

    async def run(self):
        """Основной цикл работы монитора."""
        while True:
            try:
                async for record in self.process_cities():
                    # Сохраняем данные
                    self.data_saver.save_weather_data(
                        city_name=record.city_name,
                        temperature=record.temperature,
                        timestamp=record.timestamp
                    )
                    # Проверяем необходимость уведомления
                    if self.analyzer.should_notify(record):
                        threshold = self.analyzer.get_threshold(record)
                        is_high = (
                            record.temperature > self.analyzer.thresholds.high
                        )
                        await self.notifier.send_temperature_notification(
                            city=record.city_name,
                            temp=record.temperature,
                            threshold=threshold,
                            is_high=is_high
                        )

                await asyncio.sleep(3600)  # Ожидание 1 час

            except (WeatherAPIError, KeyError) as e:
                logger.error("Error processing weather data: %s", e)
                await asyncio.sleep(60)
            except ValueError as e:
                logger.error("Error processing values: %s", e)
                await asyncio.sleep(60)
            except IOError as e:
                logger.error("Error saving data: %s", e)
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                logger.info("Weather monitoring stopped")
                raise
            except Exception as e:
                logger.critical(
                    "Unexpected critical error: %s.", e,
                    exc_info=True
                )
                await asyncio.sleep(60)  # Короткая пауза при ошибке


if __name__ == "__main__":
    monitor = WeatherMonitor(Path("config/config.yml"))
    asyncio.run(monitor.run())
