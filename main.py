
import asyncio
import logging
from datetime import datetime
from pathlib import Path


import yaml

from weather_monitor.notifications.telegram_notifier import TelegramNotifier
from weather_monitor.data_collection.data_saver import (
    WeatherDataSaver,
    WeatherRecord
)
from weather_monitor.data_collection.weather_api import WeatherAPI
from weather_monitor.analysis.temperature_analyzer import TemperatureAnalyzer

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
    """

    def __init__(self, config_path: Path) -> None:
        self.config = self._load_config(config_path)
        self.weather_api = WeatherAPI(config_path)
        self.data_saver = WeatherDataSaver(
            Path(self.config['data_storage']['netcdf_path'])
        )
        self.notifier = TelegramNotifier(
            self.config['telegram']['bot_token'],
            self.config['telegram']['chat_id']
        )
        self.analyzer = TemperatureAnalyzer(
            self.config['temperature_thresholds']
        )
        # self.plotter = WeatherPlotter(
        #     self.config['data_storage']['netcdf_path']
        # )

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        """Загружает конфигурацию из YAML файла."""
        return yaml.safe_load(config_path.read_text())

    def process_city_weather(self, city: dict) -> WeatherRecord:
        """Обработка погоды для одного города"""
        weather_data = self.weather_api.get_weather(city['id'])
        return WeatherRecord(
            city_name=city['name'],
            temperature=weather_data['main']['temp'],
            timestamp=datetime.now()
        )

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

    def process_cities(self) -> Generator[WeatherRecord, None, None]:
        """Генератор для обработки городов"""
        for city in self.config['cities']:
            try:
                record = self.process_city_weather(city)
                yield record
            except Exception as e:
                logger.error("Error processing city: %s", city['name'], e)

    async def run(self):
        while True:
            try:
                for record in self.process_cities():
                    self.data_saver.save_weather_data(record)
                    self.check_temperature_thresholds(record)

                self.plotter.plot_temperature_history('temperature_history.png')
                await asyncio.sleep(3600)  # Асинхронное ожидание
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Короткая пауза при ошибке


if __name__ == "__main__":
    monitor = WeatherMonitor(Path("config/config.yml"))
    asyncio.run(monitor.run())
