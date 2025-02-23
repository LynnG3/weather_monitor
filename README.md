# weather_monitor

Система мониторинга погоды с уведомлениями в Telegram и визуализацией данных.

## Возможности

- Сбор данных о погоде для настраиваемого списка городов
- Сохранение исторических данных в формате NetCDF
- Отправка уведомлений в Telegram при достижении пороговых значений температуры
- Визуализация изменений температуры 

## Установка

### Клонировать репозиторий
'''git clone https://github.com/LynnG3/weather-monitor.git'''
'''cd weather-monitor'''
### Создать и активировать виртуальное окружение
'''python -m venv venv'''
'''source venv/bin/activate''' для Linux/Mac
или
'''venv\Scripts\activate''' для  Windows
### Установить зависимости
'''pip install -r requirements.txt'''

## Настройка
- Создать файл `.env` в корневой директории:
plaintext
OPENWEATHERMAP_KEY=your_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

- Настроить список городов и пороговые значения в `config/config.yml`

### Использование
- TODO

