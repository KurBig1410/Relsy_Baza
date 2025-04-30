from aiogram import Bot, Dispatcher
import os

from dotenv import find_dotenv, load_dotenv
import yadisk
import logging


load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_API_TOKEN"))
dp = Dispatcher()

# Получаем токен для Яндекс.Диска из окружения
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
if not YANDEX_DISK_TOKEN:
    raise ValueError("Необходимо указать токен для Яндекс.Диска в .env")

# Инициализация клиента Яндекс.Диска
y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)
if y.check_token():
    logging.info("Подключение к Яндекс.Диску успешно")
else:
    logging.error("Ошибка: недействительный токен доступа к Яндекс.Диску")
