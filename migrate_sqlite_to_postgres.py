import os
import logging
from sqlmodel import SQLModel, Session, create_engine, select
from database.filial import Filial  # модель, связанная с PostgreSQL
from dotenv import load_dotenv

load_dotenv()
# Настройка логирования
logging.basicConfig(
    filename="migration.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Подключение к SQLite
sqlite_engine = create_engine("sqlite:///data/filial_stats.db")
db_url = os.getenv("DB_URL_NO_ASYNC")
# Подключение к PostgreSQL
postgres_engine = create_engine(db_url)

def migrate_sqlite_to_postgres():
    logging.info("🚀 Старт миграции из SQLite в PostgreSQL")
    # Чтение данных из SQLite
    with Session(sqlite_engine) as sqlite_session:
        result = sqlite_session.exec(select(Filial))
        sqlite_filials = result.all()

    logging.info(f"📦 Найдено {len(sqlite_filials)} записей в SQLite")

    count = 0

    # Запись в PostgreSQL
    with Session(postgres_engine) as session:
        for record in sqlite_filials:
            try:
                new_record = Filial(**record.model_dump())
                session.add(new_record)
                count += 1
                logging.info(
                    f"✅ Добавлен: {new_record.report_date.date()} | {new_record.name} | "
                    f"доход: {new_record.income or 0}"
                )
            except Exception as e:
                logging.error(f"❌ Ошибка при добавлении записи: {record.name} | {e}")

        session.commit()
        logging.info(f"✅ Успешно добавлено {count} записей в PostgreSQL")
    logging.info("🏁 Миграция завершена")

migrate_sqlite_to_postgres()