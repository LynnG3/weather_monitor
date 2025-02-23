# data_saver.py

from datetime import datetime
from pathlib import Path

import numpy as np
import xarray as xr


class WeatherDataSaver:
    """Класс для сохранения метеорологических данных в формате NetCDF.

    Обеспечивает сохранение временных рядов температуры для различных городов
    в формате NetCDF с поддержкой добавления новых данных
    к существующему файлу.

    Attributes:
        netcdf_path (Path): Путь к файлу NetCDF для сохранения данных
    """

    def __init__(self, netcdf_path: str):
        """
        Args:
            netcdf_path: Путь к файлу NetCDF
        """
        self.netcdf_path = Path(netcdf_path)

    def save_weather_data(
        self, city_name: str, temperature: float,
        timestamp: datetime
    ) -> None:
        """Сохраняет данные о температуре для указанного города.
        Args:
            city_name: Название города
            temperature: Значение температуры
            timestamp: Временная метка измерения
        Returns:
            None
        """
        try:
            ds = self._read_existing_data()
        except FileNotFoundError:
            ds = self._create_new_dataset(city_name, temperature, timestamp)
        else:
            ds = self._update_dataset(ds, city_name, temperature, timestamp)
        self._save_dataset(ds)

    def _read_existing_data(self) -> xr.Dataset:
        """Читает существующий файл данных."""
        return xr.open_dataset(self.netcdf_path)

    def _create_new_dataset(
        self,
        city_name: str,
        temperature: float,
        timestamp: datetime
    ) -> xr.Dataset:
        """Создает новый набор данных."""
        return xr.Dataset(
            data_vars={
                'temperature': (['city', 'time'], np.array([[temperature]]))
            },
            coords={
                'city': [city_name],
                'time': [timestamp]
            }
        )

    def _update_dataset(
        self,
        ds: xr.Dataset,
        city_name: str,
        temperature: float,
        timestamp: datetime
    ) -> xr.Dataset:
        """Обновляет существующий набор данных."""
        # Получаем numpy массивы из датасета
        temperature_data = ds.temperature.values
        times = ds.time.values
        cities = ds.city.values

        if city_name not in cities:
            # Добавляем новый город: вертикальное добавление строки
            temperature_data = np.vstack([temperature_data, [temperature]])
            cities = np.append(cities, city_name)
        else:
            if timestamp not in times:
                # Добавляем новый временной срез: гориз. добавление столбца
                temperature_data = np.column_stack(
                    [temperature_data, np.full(len(cities), temperature)]
                )
                times = np.append(times, timestamp)
        # создание и сохранение датасета
        return xr.Dataset(
            data_vars={
                'temperature': (['city', 'time'], temperature_data)
            },
            coords={
                'city': cities,
                'time': times
            }
        )

    def _save_dataset(self, ds: xr.Dataset) -> None:
        """Сохраняет набор данных в файл."""
        ds.to_netcdf(self.netcdf_path)
