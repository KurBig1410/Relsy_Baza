import json
import re
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from data_base.engine import session_maker
from data_base.filial import Filial
from data_base.crud.filial_crud import create_filial, get_filial_by_name
# from run import authorize_user, fetch_statistics_json


async_session = session_maker


def clean_float(value):
    try:
        if not value or value == "—":
            return None
        # Оставляем только часть до скобки, убираем пробелы, заменяем запятую на точку
        numeric_part = value.split("(")[0].replace(" ", "").replace(",", ".")
        return float(numeric_part)
    except Exception:
        return None


async def parse_and_store():
    # Читаем файл
    with open("data/response.json", "r", encoding="utf-8") as f:
        raw_json = json.load(f)
        html = raw_json["content"]

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

    for row in table.find_all("tbody")[0].find_all("tr"):
        cols = row.find_all("td")
        if not cols:
            continue
        cleaned = [
            re.sub(r"\s+", " ", col.get_text(strip=True)).strip() for col in cols
        ]

        filial_data = dict(zip(headers, cleaned))

        # Теперь создаём модель филиала
        filial = Filial(
            name=filial_data.get("Филиал", ""),
            income=clean_float(filial_data.get("Доход, ₽")),
            service_sum=clean_float(filial_data.get("Сумма по услугам, ₽")),
            goods_sum=clean_float(filial_data.get("Сумма по товарам, ₽")),
            avg_check_total=clean_float(filial_data.get("Общий средний чек, ₽")),
            avg_check_service=clean_float(filial_data.get("Средний чек по услугам, ₽")),
            avg_filling=clean_float(filial_data.get("Средняя заполненность")),
            new_clients=int(clean_float(filial_data.get("Новых клиентов")) or 0),
            repeat_clients=int(clean_float(filial_data.get("Повторных клиентов")) or 0),
            lost_clients=int(clean_float(filial_data.get("Потерянных клиентов")) or 0),
            total_appointments=int(clean_float(filial_data.get("Всего записей")) or 0),
            canceled_appointments=int(
                clean_float(filial_data.get("Отменённых записей")) or 0
            ),
            finished_appointments=int(
                clean_float(filial_data.get("Завершённых записей")) or 0
            ),
            unfinished_appointments=int(
                clean_float(filial_data.get("Незавершённых записей")) or 0
            ),
            owner=None,
            population_category=None,
        )

        async with async_session() as session:
            async with session.begin():
                existing = await get_filial_by_name(session, filial.name)
        
                if existing:
                    # обновляем поля вручную
                    existing.income = filial.income
                    existing.service_sum = filial.service_sum
                    existing.goods_sum = filial.goods_sum
                    existing.avg_check_total = filial.avg_check_total
                    existing.avg_check_service = filial.avg_check_service
                    existing.avg_filling = filial.avg_filling
                    existing.new_clients = filial.new_clients
                    existing.repeat_clients = filial.repeat_clients
                    existing.lost_clients = filial.lost_clients
                    existing.total_appointments = filial.total_appointments
                    existing.canceled_appointments = filial.canceled_appointments
                    existing.finished_appointments = filial.finished_appointments
                    existing.unfinished_appointments = filial.unfinished_appointments
                    existing.population_category = filial.population_category
                    existing.owner = filial.owner
                else:
                    session.add(filial)


async def run_pipeline():
    # authorize_user()
    # fetch_statistics_json()
    await parse_and_store()


if __name__ == "__main__":
    asyncio.run(run_pipeline())
