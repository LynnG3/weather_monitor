"""Модуль с кастомными исключениями для weather_monitor."""


class WeatherMonitorError(Exception):
    """Базовое исключение для всех ошибок в weather_monitor.

    Attributes:
        message: Сообщение об ошибке
        details: Дополнительные детали ошибки
    """
    def __init__(self, message: str, details: dict = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class WeatherAPIError(WeatherMonitorError):
    """Исключение при ошибках в работе с API погоды.

    Attributes:
        message: Сообщение об ошибке
        status_code: HTTP статус код (если применимо)
        response: Ответ от API (если применимо)
    """
    def __init__(
        self,
        message: str,
        status_code: int = None,
        response: dict = None
    ) -> None:
        details = {
            'status_code': status_code,
            'response': response
        }
        super().__init__(message, details)
