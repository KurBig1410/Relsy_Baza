import requests
import json
import os
import re
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from sqlmodel import Field, SQLModel, Session, create_engine, select
from typing import Optional
from auth import authorize_user
import argparse
import sys
from database.engine import session_maker


class Filial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    report_date: datetime

    name: str
    income: Optional[float] = None
    service_sum: Optional[float] = None
    goods_sum: Optional[float] = None
    avg_check_total: Optional[float] = None
    avg_check_service: Optional[float] = None
    avg_filling: Optional[float] = None
    new_clients: Optional[int] = None
    repeat_clients: Optional[int] = None
    lost_clients: Optional[int] = None
    total_appointments: Optional[int] = None
    canceled_appointments: Optional[int] = None
    finished_appointments: Optional[int] = None
    unfinished_appointments: Optional[int] = None
    population_category: Optional[str] = None
    owner: Optional[str] = None


COLUMN_MAP = {
    "Филиал": "name",
    "Доход, ₽": "income",
    "Сумма по услугам, ₽": "service_sum",
    "Сумма по товарам, ₽": "goods_sum",
    "Общий средний чек, ₽": "avg_check_total",
    "Средний чек по услугам, ₽": "avg_check_service",
    "Средняя заполненность": "avg_filling",
    "Новых клиентов": "new_clients",
    "Повторных клиентов": "repeat_clients",
    "Потерянных клиентов": "lost_clients",
    "Всего записей": "total_appointments",
    "Отмененных записей": "canceled_appointments",
    "Завершенных записей": "finished_appointments",
    "Незавершенных записей": "unfinished_appointments",
}


def parse_float(value):
    try:
        if not value:
            return None
        # удаляем всё в скобках: (63.18%)
        cleaned = re.sub(r"\(.*?\)", "", value)
        # удаляем неразрывные пробелы и обычные
        cleaned = cleaned.replace("\xa0", " ").replace(",", ".").strip()
        # убираем все пробелы между цифрами (например: "18 200")
        cleaned = cleaned.replace(" ", "")
        return float(cleaned)
    except Exception as e:
        print(f"[parse_float error] '{value}' → {e}")
        return None


def parse_int(value):
    try:
        return int(value.replace(" ", ""))
    except:  # noqa: E722
        return None


def fetch_statistics_json_for_date(date_str):
    url = f"https://yclients.com/group_analytics/filial/search/127929/?date_from={date_str}&date_to={date_str}"

    with open("data/cookies.json", "r") as f:
        raw_cookies = json.load(f)

    session = requests.Session()
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": random.choice(USER_AGENTS),
        "X-Requested-With": "XMLHttpRequest",
        "X-Yclients-Application-Name": "biz.erp.web",
        "X-Yclients-Application-Platform": "legacy JS-1.0",
        "X-Yclients-Application-Version": "1.0.0",
        "Referer": url,
    }

    for cookie in raw_cookies:
        session.cookies.set(cookie["name"], cookie["value"])

    response = session.get(url, headers=headers)

    if response.status_code == 403:
        raise Exception("🚫 Доступ запрещён (403). Возможно, cookies протухли")

    content_type = response.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        with open(f"data/html_error_{date_str}.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        raise Exception(f"❌ Ожидался JSON, но получен {content_type}")

    try:
        data = response.json()
    except json.JSONDecodeError:
        with open(f"data/bad_json_{date_str}.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        raise Exception("❌ Не удалось распарсить JSON")

    with open("data/response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def convert_html_to_df():
    with open("data/response.json", "r", encoding="utf-8") as f:
        raw_json = json.load(f)
        html = raw_json["content"]
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    headers = [
        th.get_text(strip=True) for th in table.find_all("thead")[0].find_all("th")
    ]
    data = []
    for row in table.find_all("tbody")[0].find_all("tr"):
        cols = row.find_all("td")
        if not cols:
            continue
        cleaned = [
            re.sub(r"\s+", " ", col.get_text(strip=True)).strip() for col in cols
        ]
        data.append(cleaned)
    df = pd.DataFrame(data, columns=headers)
    return df


def log(message):
    print(message)
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {message}\n")


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
]


async def main():
    os.makedirs("data", exist_ok=True)
    start_date = datetime(2025, 5, 20)
    end_date = datetime.today()

    async with session_maker() as session:
        current = start_date
        day_count = 0
        while current <= end_date:
            date_str = current.strftime("%d.%m.%Y")
            log(f"📅 Обработка {date_str}")

            try:
                existing = session.exec(
                    select(Filial).where(Filial.report_date == current)
                ).first()

                if existing:
                    log(f"⏭ Пропускаем {date_str} — данные уже есть в БД")
                    current += timedelta(days=1)
                    continue
                fetch_statistics_json_for_date(date_str)
                df = convert_html_to_df()
                # print("\n🧩 Заголовки из таблицы:", df.columns.tolist(), "\n")

                for _, row in df.iterrows():
                    record = Filial(
                        report_date=datetime.strptime(date_str, "%d.%m.%Y"),
                        name=row["Филиал"],
                        income=parse_float(row.get("Доход, ₽")),
                        service_sum=parse_float(row.get("Сумма по услугам, ₽")),
                        goods_sum=parse_float(row.get("Сумма по товарам, ₽")),
                        avg_check_total=parse_float(row.get("Общий средний чек, ₽")),
                        avg_check_service=parse_float(
                            row.get("Средний чек по услугам, ₽")
                        ),
                        avg_filling=parse_float(row.get("Средняя заполненность")),
                        new_clients=parse_int(row.get("Новых клиентов")),
                        repeat_clients=parse_int(row.get("Повторных клиентов")),
                        lost_clients=parse_int(row.get("Потерянных клиентов")),
                        total_appointments=parse_int(row.get("Всего записей")),
                        canceled_appointments=parse_int(row.get("Отмененных записей")),
                        finished_appointments=parse_int(row.get("Завершенных записей")),
                        unfinished_appointments=parse_int(
                            row.get("Незавершенных записей")
                        ),
                    )
                    # print("\n🧩 Из таблицы:", record, "\n")
                    # raw_val = row.get("Сумма по услугам, ₽")
                    # print(f"[DEBUG] service_sum сырое значение: '{raw_val}'")
                    # print(f"[DEBUG] после parse_float: {parse_float(raw_val)}")
                    session.add(record)
                await session.commit()
                log(f"✅ Сохранено за {date_str}")

                day_count += 1
                if day_count % 30 == 0:
                    log("🍵 Длинная пауза после 30 дней просмотра...")
                    time.sleep(random.uniform(60, 180))

            except Exception as e:
                log(f"⚠️ Ошибка на {date_str}: {e}")
                if (
                    "cookies" in str(e).lower()
                    or "403" in str(e)
                    or "ожидался JSON" in str(e)
                ):
                    log("🔄 Попытка переавторизации...")
                    authorize_user()
                    continue  # пробуем тот же день заново

            # 💤 Пауза между днями (имитация просмотра вручную)
            slow_pause = random.uniform(10, 30)
            log(f"⏱ Пауза {int(slow_pause)} сек между днями")
            time.sleep(slow_pause)

            # 💤 Ночной сон (чтобы не спалиться)
            hour_now = datetime.now().hour
            if 2 <= hour_now <= 5:
                log("🌙 Ночной режим: пауза до утра")
                time.sleep(60 * 60 * random.uniform(2, 4))  # 2–4 часа
            current += timedelta(days=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Yclients парсер с авторизацией и режимами"
    )
    parser.add_argument(
        "--a",
        "--auth",
        dest="auth",
        action="store_true",
        help="Запуск только авторизации",
    )
    parser.add_argument(
        "--p",
        "--parse",
        dest="parse",
        action="store_true",
        help="Запуск только парсинга",
    )
    args = parser.parse_args()
    if not args.auth and not args.parse:
        print("❗ Укажи хотя бы один флаг: --a (авторизация) или --p (парсинг)")
        sys.exit(1)

    if args.auth:
        print("🔐 Режим авторизации...")
        authorize_user()

    if args.parse:
        print("📊 Режим парсинга...")
        main()
    # authorize_user()  # начальная авторизация
    # main()
