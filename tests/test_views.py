import json
from unittest.mock import MagicMock, patch

from src.views import date_t


def test_date_t():  # Тест функции с мокированием зависимостей
    with (
        patch("src.views.get_time_for_greeting") as mock_greeting,
        patch("src.views.get_date") as mock_date,
        patch("src.views.get_period") as mock_period,
        patch("src.views.get_card_with_spend") as mock_card,
        patch("src.views.get_top") as mock_top,
        patch("src.views.get_currency") as mock_currency,
        patch("src.views.get_stock") as mock_stock,
    ):

        mock_greeting.return_value = "Добрый день"
        mock_date.return_value = ["01.03.2025", "30.07.2025"]
        mock_period.return_value = MagicMock()
        mock_card.return_value = [{"last_digits": "1234", "total_spend": -15}]
        mock_top.return_value = [{"amount": "300", "category": "Еда"}]
        mock_currency.return_value = [{"currency": "USD", "rate": "94"}]
        mock_stock.return_value = [{"stock": "AAPL", "price": 300}]

        result = date_t("2025-07-30 13:00:00")
        data = json.loads(result)

        assert data["greeting"] == "Добрый день"
        assert len(data["cards"]) == 1
        assert data["cards"][0]["last_digits"] == "1234"
        assert data["currency"][0]["currency"] == "USD"
        assert data["stock_prices"][0]["stock"] == "AAPL"
