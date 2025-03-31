"""Модуль анализа температурных данных.

Этот модуль предоставляет функциональность для анализа температурных данных
и определения необходимости отправки уведомлений
при достижении пороговых значений.

Основные компоненты:
    - TemperatureThresholds: Структура данных для хранения пороговых значений
    - TemperatureAnalyzer: Класс для анализа температурных данных

Пример использования:
    thresholds = {'high': 30.0, 'low': -10.0}
    analyzer = TemperatureAnalyzer(thresholds)

    # Проверка необходимости уведомления
    if analyzer.should_notify(weather_record):
        threshold = analyzer.get_threshold(weather_record)
        # Отправка уведомления

Attributes:
    logger: Logger для записи информации об ошибках

Note:
    Пороговые значения задаются в конфигурационном файле.
    Уведомления отправляются в следующих случаях:
    - Первое измерение для города
    - Температура ниже нижнего порога
    - Температура выше верхнего порога
    - Температура пересекла пороговое значение
"""

import logging
from dataclasses import dataclass
from typing import Dict

from weather_monitor.data_collection.data_saver import WeatherRecord

logger = logging.getLogger(__name__)


@dataclass
class TemperatureThresholds:
    """Структура данных для хранения пороговых значений температур.

    Attributes:
        high: Верхнее пороговое значение
        low: Нижнее пороговое значение
    """

    high: float
    low: float


class TemperatureAnalyzer:
    """Анализатор температурных данных.

    Отвечает за анализ температурных данных и определение
    необходимости отправки уведомлений.
    """
    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = TemperatureThresholds(
            high=thresholds['high'],
            low=thresholds['low']
        )
        self.last_temperatures: Dict[str, float] = {}

    def get_threshold(self, record: WeatherRecord) -> float:
        """Возвращает текущее пороговое значение для записи.

        Args:
            record: Запись с погодными данными

        Returns:
            float: Пороговое значение (верхнее или нижнее)
        """
        return (
            self.thresholds.high
            if record.temperature > self.thresholds.high
            else self.thresholds.low
        )

    def should_notify(self, record: WeatherRecord) -> bool:
        """Определяет, нужно ли отправлять уведомление.

            Уведомление отправляется в случаях:
            1. Первое измерение для города
            2. Температура ниже порогового значения
            3. Температура выше порогового значения
            4. Температура пересекла пороговое значение
            """
        current_temp = record.temperature
        last_temp = self.last_temperatures.get(record.city_name)

        if last_temp is None:
            # Первое измерение для города
            should_notify = True
        else:
            # Проверяем текущее состояние и пересечение порогов
            is_too_cold = current_temp < self.thresholds.low
            is_too_hot = current_temp > self.thresholds.high
            crossed_high = (
                current_temp > self.thresholds.high
                and last_temp <= self.thresholds.high
            )
            crossed_low = (
                current_temp < self.thresholds.low
                and last_temp >= self.thresholds.low
            )
            should_notify = (
                is_too_cold or is_too_hot or crossed_high or crossed_low
            )

        # Сохраняем текущую температуру для следующего сравнения
        self.last_temperatures[record.city_name] = current_temp
        return should_notify

    async def update_statistics(self):
        """Обновляет статистику температур. TODO: реализовать"""
