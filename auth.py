import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

load_dotenv()

login = os.getenv("LOGIN")
password = os.getenv("PASS")
today = datetime.today()
date_to = today.strftime("%d.%m.%Y")
date_from = (today - timedelta(days=29)).strftime("%d.%m.%Y")


def get_date_range():
    return date_from, date_to


def authorize_user():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    date_from, date_to = get_date_range()

    try:
        driver.get(
            f"https://yclients.com/group_analytics/filial/search/127929/?date_from={date_from}&date_to={date_to}"
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        driver.find_element(By.NAME, "email").send_keys(login)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(
            password
        )
        driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
        time.sleep(5)
        cookies = driver.get_cookies()
        with open("data/cookies.json", "w") as f:
            json.dump(cookies, f)
        print("✅ Куки сохранены в data/cookies.json")
    except Exception as e:
        print("❌ Ошибка во время логина:", e)
    finally:
        driver.quit()


def fetch_statistics_json():
    date_from, date_to = get_date_range()
    url = f"https://yclients.com/group_analytics/filial/search/127929/?date_from={date_from}&date_to={date_to}"

    with open("data/cookies.json", "r") as f:
        raw_cookies = json.load(f)

    session = requests.Session()
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "X-Yclients-Application-Name": "biz.erp.web",
        "X-Yclients-Application-Platform": "legacy JS-1.0",
        "X-Yclients-Application-Version": "1.0.0",
        "Referer": url,
    }

    for cookie in raw_cookies:
        session.cookies.set(cookie["name"], cookie["value"])

    response = session.get(url, headers=headers)
    content_type = response.headers.get("Content-Type", "")

    if response.status_code == 200:
        if "application/json" in content_type:
            try:
                data = response.json()
                with open("data/response.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("✅ JSON сохранён в: data/response.json")
            except json.JSONDecodeError:
                print("❌ Ошибка при разборе JSON.")
        elif "text/html" in content_type:
            with open("data/response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ HTML сохранён в: data/response.html")
        else:
            with open("data/response.txt", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ Сохранено в: data/response.txt")
    else:
        print("❌ Ошибка запроса:", response.status_code)
        print(response.text)


def convert_json_to_csv():
    with open("data/response.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
    html = raw["content"]
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        cells = [
            td.get_text(strip=True).replace("\xa0", " ") for td in tr.find_all("td")
        ]
        if cells:
            rows.append(cells)
    df = pd.DataFrame(rows, columns=headers)
    df.to_csv("data/filial_stats.csv", index=False, encoding="utf-8-sig")
    print("✅ CSV сохранён в: data/filial_stats.csv")


def convert_html_to_json():
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
    df.to_json("data/response_out.json", orient="records", force_ascii=False, indent=2)
    print("✅ JSON сохранён в: data/response_out.json")


def run_pipeline():
    authorize_user()
    # fetch_statistics_json()
    # convert_json_to_csv()
    # convert_html_to_json()
    # date_to_print = f'Дата начала{date_to}'
    # date_from_print = f'Дата окончания{date_from}'
    # return date_to_print, date_from_print
    # print(f'Дата начала{date_to}')
    # print(f'Дата окончания{date_from}')


# if __name__ == "__main__":
#     run_pipeline()
