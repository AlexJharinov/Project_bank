import json
from datetime import datetime
from unittest.mock import patch, Mock

import pandas as pd
import pytest
import requests

from src import utils
from src.utils import (
    get_date,
    get_period,
    get_card_with_spend,
    get_top,
    get_currency,
    get_stock,
)


@pytest.mark.parametrize(
    "fake_hour, expected",
    [
        (6, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (3, "Доброй ночи"),
    ],
)
@patch("src.utils.datetime")
def test_get_time_for_greeting_all_periods(
    mock_datetime, fake_hour, expected
):  # тест на функцию приветствие
    mock_datetime.now.return_value = datetime(2023, 10, 15, fake_hour, 0, 0)
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    result = utils.get_time_for_greeting()
    assert result == expected


def test_get_date_standard_format():
    """
    Тест на функцию get_date
    """
    input_str = "2025-08-05 10:15:30"
    result = get_date(input_str)
    assert result == ["01.08.2025 10:15:30", "05.08.2025 10:15:30"]


def test_get_date_invalid_format():
    """
    Тест на функцию get_date с неправильным форматом
    """
    input_str = "08/05/2025 10:15:30"
    with pytest.raises(ValueError):
        get_date(input_str)


def test_get_period_filters_correctly(sample_excel_file):
    """
    Тест на функцию get_period
    """
    period = ["02.08.2025 00:00:00", "15.08.2025 23:59:59"]

    result_df = get_period(str(sample_excel_file), period)

    # Проверка строк
    expected_dates = ["03.08.2025", "10.08.2025", "15.08.2025"]
    expected_dates = pd.to_datetime(expected_dates, dayfirst=True)

    assert len(result_df) == 3
    assert list(result_df["Дата операции"]) == list(expected_dates)

    assert result_df["Дата операции"].is_monotonic_increasing


def test_get_card_with_spent_correct_data(df_data):
    # Вызов функции
    result = get_card_with_spend(df_data)

    # Ожидаемый результат
    expected_result = [{"last_digits": "7197", "total_spent": 296.8, "cashback": 2.0}]

    # Проверка результата
    assert result == expected_result


def test_get_top_transactions_correct_data(df_data):

    result = get_top(df_data, pass_value=5)

    # Ожидаемый результат
    expected_result = [
        {
            "date": "04.05.2018",
            "amount": -58.0,
            "category": "Фастфуд",
            "description": "McDonald's",
        },
        {
            "date": "03.05.2018",
            "amount": -69.9,
            "category": "Фастфуд",
            "description": "Бургер Кинг",
        },
        {
            "date": "02.05.2018",
            "amount": -208.0,
            "category": "Ж/д билеты",
            "description": "Московский метрополитен",
        },
        {
            "date": "04.05.2018",
            "amount": -221.27,
            "category": "Супермаркеты",
            "description": "Пятёрочка",
        },
        {
            "date": "05.05.2018",
            "amount": -250.0,
            "category": "Связь",
            "description": "МТС",
        },
    ]

    # Проверка результата
    assert result == expected_result


def test_get_currency(mocker):
    # Мокируем открытие файла и чтение JSON
    mock_json_data = {"user_currencies": ["USD"]}
    mock_file = mocker.mock_open(read_data=json.dumps(mock_json_data))
    mocker.patch("builtins.open", mock_file)

    # Мокируем requests.get
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"query": {"from": "USD"}, "result": 75.50}
    mocker.patch("requests.get", return_value=mock_response)

    # Вызов функции
    result = get_currency("../data/user_settings.json")

    # Ожидаемый результат
    expected_result = [
        {"currency": "USD", "rate": 79.19},
    ]

    # Проверка результата
    assert result == expected_result


def test_get_stock_correct_data(mocker):
    # Мокируем открытие файла и чтение JSON
    mock_json_data = {"user_stocks": ["AAPL"]}
    mock_file = mocker.mock_open(read_data=json.dumps(mock_json_data))
    mocker.patch("builtins.open", mock_file)

    # Мокируем requests.get
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "pagination": {"limit": 100, "offset": 0, "count": 100, "total": 9944},
        "data": [
            {
                "open": 129.8,
                "high": 133.04,
                "low": 129.47,
                "close": 132.995,
                "volume": 106686703.0,
                "adj_high": 133.04,
                "adj_low": 129.47,
                "adj_close": 132.995,
                "adj_open": 129.8,
                "adj_volume": 106686703.0,
                "split_factor": 1.0,
                "dividend": 0.0,
                "symbol": "AAPL",
                "exchange": "XNAS",
                "date": "2021-04-09T00:00:00+0000",
            },
        ],
    }
    mocker.patch("requests.get", return_value=mock_response)

    # Вызов функции
    result = get_stock("fake_path.json")

    # Ожидаемый результат
    expected_result = [
        {"stock": "AAPL", "price": 132.995},
    ]

    # Проверка результата
    assert result == expected_result


def test_get_stock_http_error(mocker):
    # Мокаем файл с данными
    mock_json_data = {"user_stocks": ["AAPL", "GOOGL"]}
    mock_file = mocker.mock_open(read_data=json.dumps(mock_json_data))
    mocker.patch("builtins.open", mock_file)

    # Мокаем ошибку сети
    mocker.patch(
        "requests.get", side_effect=requests.exceptions.RequestException("Ошибка сети")
    )

    # Ожидаем, что функция выбросит исключение
    with pytest.raises(requests.exceptions.RequestException):
        get_stock("fake_path.json")
