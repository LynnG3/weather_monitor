"""Модуль для отправки уведомлений через Telegram Bot API.

Этот модуль предоставляет функциональность для отправки уведомлений
о погодных условиях через Telegram бота. Использует библиотеку aiogram 3.x
для асинхронного взаимодействия с Telegram Bot API.

Основные компоненты:
    - TelegramNotifier: Класс для отправки уведомлений

Пример использования:
    notifier = TelegramNotifier(bot_token="your_token", chat_id="your_chat_id")
    await notifier.send_temperature_notification(
        city="Moscow",
        temp=25.5,
        threshold=30,
        is_high=True
    )

Attributes:
    logger: Logger для записи информации об ошибках

Note:
    Для работы требуется валидный токен бота и ID чата.
    Токен можно получить у @BotFather в Telegram.
"""
import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import AiogramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram.

    Использует aiogram 3.x для асинхронного взаимодействия с Telegram Bot API.
    """
    def __init__(self, bot_token: str, chat_id: str) -> None:
        """Инициализация нотификатора.

        Args:
            bot_token: Токен Telegram бота
            chat_id: ID чата для отправки сообщений
        """
        default = DefaultBotProperties(parse_mode=ParseMode.HTML)
        self.bot = Bot(token=bot_token, default=default)
        self.chat_id = chat_id

    async def send_alert(self, message: str) -> None:
        """Отправляет сообщение в Telegram.

        Args:
            message: Текст сообщения
        Raises:
            TelegramError: При ошибке отправки сообщения
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
        except AiogramError as e:
            logger.error("Failed to send Telegram message: %s", e)
            raise

    async def send_temperature_notification(
        self, city: str, temp: float, threshold: float, is_high: bool
    ) -> None:
        """Отправляет уведомление о температуре.

        Args:
            city: Название города
            temp: Текущая температура
            threshold: Пороговое значение
            is_high: True если превышен верхний порог, False если нижний
        """
        message = (
            f"Город: {city}\n"
            f"Текущая температура: {temp}°C\n"
            f"{'Превышен верхний' if is_high else 'Достигнут нижний'} "
            f"порог: {threshold}°C"
        )
        await self.send_alert(message)
