# data_saver.py

from datetime import datetime
from pathlib import Path
from typing import Union

import numpy as np
import xarray as xr


class WeatherDataSaver:
    """Класс для сохранения метеорологических данных в формате NetCDF.
    
    Обеспечивает сохранение временных рядов температуры для различных городов
    в формате NetCDF с поддержкой добавления новых данных к существующему файлу.
    
    Attributes:
        netcdf_path (Path): Путь к файлу NetCDF для сохранения данных
    """

    def __init__(self, netcdf_path: str):
        """
        Args:
            netcdf_path: Путь к файлу NetCDF
        """
        self.netcd_path = netcdf_path

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
            # попытка открыть существующий файл
            ds = xr.open_dataset(self.netcd_path)
            temperature_data = ds.temperature.values
            times = ds.time.values
            cities = ds.city.values
        except FileNotFoundError:
            # создание нового датасета
            temperature_data = np.array([[temperature]])
            times = np.array([timestamp])
            cities = np.array([city_name])
        else:
            ds.close()
            # добавление новых данных
            if city_name not in cities:
                temperature_data = np.vstack([temperature_data, [temperature]])
                cities = np.append(cities, city_name)
            else:
                city_idx = np.where(cities == city_name)[0][0]
                if timestamp not in times:
                    temperature_data = np.column_stack(
                        [temperature_data, [temperature]]
                    )
                    times = np.append(times, timestamp)
        # создание и сохранение датасета
        ds_new = xr.Dataset(
            data_vars={
                'temperature': (['city', 'time'], temperature_data)
            },
            coords={
                'city': cities,
                'time': times
            }
        )
        ds_new.to_netcdf(self.netcd_path)
