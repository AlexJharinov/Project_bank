import pandas as pd
from pandas import DataFrame

from src.reports import spending_by_category
from src.services import analyze_cashback
from src.views import date_t




if __name__ == "__main__":
    # Вызов функции main_str из модуля views
    date_request = "2018-05-20 15:30:00"
    result_views = date_t(date_request)
    print(result_views)

    # Вызов функции spending_by_category с декоратором report_decorator из модуля reports
    df: DataFrame = pd.read_excel("../data/operations.xlsx", sheet_name="Отчет по операциям")
    result_reports = spending_by_category(df, "Фастфуд", "2018-04-15")
    print(result_reports)

    # Вызов функции analyze_cashback из модуля services
    result_services = analyze_cashback("../data/operations.xlsx", 2018, 5)
    print(result_services)