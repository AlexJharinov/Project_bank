import json
from typing import Any, Dict

from src.utils import get_time_for_greeting, get_date, get_period, get_card_with_spend, get_top, get_currency, get_stock


def date_t(date_time: str) -> Dict[str, Any]:
    """
        функцию, принимающую на вход строку с датой и временем в формате
        YYYY-MM-DD HH:MM:SSи возвращающую JSON-ответ
    """

    greeting = get_time_for_greeting() # Приветствие

    period = get_date(date_time)

    sorted_exel = get_period("../data/operations.xlsx",period)

    cards = get_card_with_spend(sorted_exel) # По каждой карте

    top_transactions = get_top(sorted_exel, 5) # Топ-5 транзакций по сумме платежа

    currency_rates = get_currency("../data/user_settings.json" )# Курс валют

    stock_prices = get_stock("../data/user_settings.json") # Стоимость акций

    date = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency": currency_rates,
        "stock_prices": stock_prices
    }

    json_data = json.dumps(date, ensure_ascii=False, indent=4)
    return json_data

