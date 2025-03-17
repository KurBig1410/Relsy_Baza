import logging
import asyncio
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from setings import y
from database.orm_query import orm_add_file, orm_add_folder
from sqlalchemy.ext.asyncio import AsyncSession


default_excel_img = "https://avatars.mds.yandex.net/i?id=6727fb378e9838a0f5d6452703b6330e267d40cb-9652646-images-thumbs&n=13"
default_doc_img = "https://avatars.mds.yandex.net/i?id=6727fb378e9838a0f5d6452703b6330e267d40cb-9652646-images-thumbs&n=13"
default_folder_img = (
    "https://img.icons8.com/?size=100&id=1e4bYxePiOFA&format=png&color=000000"
)

# Словарь для соответствия расширений и их иконок
EXTENSION_ICONS = {
    ".xlsx": "https://avatars.mds.yandex.net/i?id=6727fb378e9838a0f5d6452703b6330e267d40cb-9652646-images-thumbs&n=13",  # Ссылка на иконку Excel
    ".docx": "https://img.icons8.com/?size=100&id=pGHcje298xSl&format=png&color=000000",  # Ссылка на иконку Word
    ".pdf": "https://img.icons8.com/?size=100&id=d2H6kHCiPSIg&format=png&color=000000",  # Ссылка на иконку PDF
    # Добавьте другие расширения и их ссылки по необходимости
}


# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Функция для получения списка файлов с Яндекс.Диска
def fetch_yandex_disk_files(
    path="ФРАНШИЗА1/ФРАНШИЗА",
):
    files = []
    try:
        logging.info(f"Начало обработки каталога: {path}")
        for item in y.listdir(path):  # Здесь мы ждем результат выполнения
            if item["type"] == "dir":
                logging.info(
                    f"Это папка {item['path']}, начинаю проверку внутренних каталогов"
                )
                files.extend(fetch_yandex_disk_files(item["path"]))
                logging.info(f"Проверка внутренних папок в {item['path']} окончена")
            else:
                # Обработка даты создания файла
                created_date = None
                try:
                    if "created" in item and item["created"]:
                        created_date = item["created"]
                except ValueError as ve:
                    logging.warning(
                        f"Ошибка при разборе даты для файла {item['name']}: {ve}"
                    )
                # Добавляем файл в список с нужными атрибутами
                files.append(
                    {
                        "folder": path,
                        "name": item["name"],
                        "size": item["size"]
                        / (1024 * 1024),  # Конвертация размера в мегабайты
                        "created": created_date,
                        "extension": item["name"].split(".")[-1],
                        "link": y.get_download_link(item["path"]),
                    }
                )
        logging.info(f"Обработка каталога {path} завершена")
    except Exception as e:
        logging.error(f"Ошибка обработки каталога {path}: {e}", exc_info=True)
    print(f"\n\n\n\n{files}\n\n\n\n")
    return files


def fetch_yandex_disk_folders(path="ФРАНШИЗА1/ФРАНШИЗА"):
    folders = []
    try:
        logging.info(f"Начало обработки каталога: {path}")
        # Получаем список содержимого папки на указанном пути
        items = y.listdir(path)
        for item in items:
            if item["type"] == "dir":
                # Формируем корректный путь для ссылки
                encoded_path = item["path"].replace("disk:/", "").replace("/", "%2F")
                folders.append(
                    {
                        "name": item["name"],
                        "link": f"https://disk.yandex.ru/client/disk/{encoded_path}",
                    }
                )
                # Рекурсивный вызов для вложенных папок
                subfolders = fetch_yandex_disk_folders(item["path"])
                # Добавляем вложенные папки в общий список
                folders.extend(subfolders)
    except Exception as e:
        logging.error(f"Ошибка при сканировании папки {path}: {e}", exc_info=True)
    return folders


def is_image_file(file_name: str) -> bool:
    """
    Проверяет, является ли файл изображением по расширению.
    """
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    return any(file_name.lower().endswith(ext) for ext in image_extensions)


def get_icon_or_image_for_file(file_name: str, file_link: str) -> str:
    """
    Определяет, использовать ссылку на файл с Яндекс.Диска или иконку.
    """
    print(f'\n\n\n\n\n\nСсылка на файл: {file_link}\n\n\n\n\n\n')
    if is_image_file(file_name):
        # Если файл изображение, возвращаем ссылку на файл с Яндекс.Диска
        return file_link
    # Для других типов файлов используем соответствующую иконку
    for ext, icon_link in EXTENSION_ICONS.items():
        if file_name.lower().endswith(ext):
            return icon_link
    # Если расширение неизвестно, возвращаем дефолтную иконку
    return "https://img.icons8.com/?size=100&id=d2H6kHCiPSIg&format=png&color=000000"


async def scan_and_notify(session: AsyncSession):
    try:
        # Получаем список файлов и папок с Яндекс.Диска
        files = await asyncio.to_thread(fetch_yandex_disk_files)
        folders = await asyncio.to_thread(fetch_yandex_disk_folders)
        new_files = []

        for file in files:
            # Определяем ссылку на иконку или изображение
            file_icon = get_icon_or_image_for_file(file["name"], file["link"])
            if await orm_add_file(
                data={
                    "name": file["name"],
                    "download_path": file["link"],
                    "img": file_icon,  # Используем ссылку на иконку или изображение
                },
                session=session,
            ):
                # Если файл новый, добавляем его в список новых файлов
                new_files.append(file)

        for folder in folders:
            if await orm_add_folder(
                data={
                    "name": folder["name"],
                    "path": folder["link"],
                    "img": default_folder_img,  # Для папок используется дефолтный значок
                },
                session=session,
            ):
                new_files.append(folder)
    except Exception as e:
        logging.error(f"Ошибка при сканировании Яндекс.Диска: {e}")


# Функция для инициализации планировщика
def setup_scheduler(bot: Bot):
    # Создаём планировщик
    scheduler = AsyncIOScheduler()

    # Сразу выполняем проверку файлов на Яндекс.Диске
    asyncio.create_task(scan_and_notify(bot))

    # Настройка регулярного сканирования
    scheduler.add_job(scan_and_notify, "cron", hour="8,20", args=(bot,))
    scheduler.start()
