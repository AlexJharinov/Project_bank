import json
from datetime import datetime

import pandas as pd
from pandas import DataFrame
import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_1 = os.getenv("API_KEY_1")

url = "https://api.apilayer.com/currency_data/convert"


def get_time_for_greeting():
    """
    Функция возвращает время дня от текущего времени пользователя.
    """

    user_time = datetime.now().hour
    if 5 <= user_time < 12:
        return "Доброе утро"
    elif 12 <= user_time < 18:
        return "Добрый день"
    elif 18 <= user_time < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_date(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    dt = datetime.strptime(date_time, date_format)
    start_of_month = dt.replace(day=1)
    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S"),
    ]


def get_period(path_fo_file: str, period: list) -> DataFrame:
    """
    Функция принимает путь к файлу и диапазон дат и возвращает
    таблицу данных в заданом диапазоне
    """
    df = pd.read_excel(path_fo_file)
    # print(df['Дата операции']) #проверка чтения файла

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

    start_day = datetime.strptime(period[0], "%d.%m.%Y %H:%M:%S")
    end_day = datetime.strptime(period[1], "%d.%m.%Y %H:%M:%S")

    filtered_df = df[
        (df["Дата операции"] >= start_day) & (df["Дата операции"] <= end_day)
    ]
    sorted_df = filtered_df.sort_values(by="Дата операции")
    return sorted_df


def get_card_with_spend(sorted_df: DataFrame) -> list[dict]:
    """
    Функция принимает отфильтрованную таблицу и возвращает: последние 4 цифры карты;
    общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей).
    """
    transactions_card = []

    card_sorted = sorted_df[
        ["Номер карты", "Сумма операции", "Кэшбэк", "Сумма операции с округлением"]
    ]
    for i, v in card_sorted.iterrows():

        if v["Сумма операции"] < 0:
            last_digits = str(v["Номер карты"]).replace("*", "")
            total_spend = v["Сумма операции с округлением"]
            cashback = total_spend // 100
            v = {
                "last_digits": last_digits,
                "total_spent": total_spend,
                "cashback": cashback,
            }

            transactions_card.append(v)

        return transactions_card


def get_top(
    sorted_df: DataFrame,
    pass_value,
):
    """
    Функция принимает таблицу и возвращает топ транзакций по сумме платежа
    """

    top_pay = []
    sorted_pay = sorted_df.sort_values(by="Сумма операции", ascending=False)
    top_transactions = sorted_pay.head(pass_value)
    top_transactions_carted = top_transactions[
        ["Дата платежа", "Сумма операции", "Категория", "Описание"]
    ]
    for i, r in top_transactions_carted.iterrows():
        transaction = {
            "date": f"{r['Дата платежа']}",
            "amount": r["Сумма операции"],
            "category": f"{r['Категория']}",
            "description": f"{r['Описание']}",
        }
        top_pay.append(transaction)

    return top_pay


def get_currency(path_to_json: str) -> list[dict]:
    """
    Функция принимает файл с исходными данными и вовращает курс валют
    """
    currency_rates = []
    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        currencies = data["user_currencies"]
        for currency in currencies:
            params = {"amount": 1, "from": f"{currency}", "to": "RUB"}
            headers = {"apikey": API_KEY}
            response = requests.request("GET", url, headers=headers, params=params)

            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                result_response = result["query"]["from"]
                currency_amount = round(result["result"], 2)
                currency_rates.append(
                    {"currency": result_response, "rate": currency_amount}
                )
    return currency_rates


def get_stock(path_to_json: str) -> list[dict]:
    """
    Функция, которая принимает путь к файлу с настройками и возвращает словарь с
    текущим курсом акций
    """
    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        stocks = data.get("user_stocks", [])

    if not stocks:
        return []

    # Формируем URL запроса
    symbols = ",".join(stocks)
    url = f"http://api.marketstack.com/v1/eod?access_key={API_KEY_1}&symbols={symbols}"

    # Отправляем запрос
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Обрабатываем ответ
    stock_prices = []
    if "data" in data:
        for stock_data in data["data"]:
            if "symbol" in stock_data and "close" in stock_data:
                stock_prices.append(
                    {"stock": stock_data["symbol"], "price": stock_data["close"]}
                )

    return stock_prices
