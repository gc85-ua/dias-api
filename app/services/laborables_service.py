from datetime import date, timedelta
from app.schemas.services import LaborablesResponse, Laborables
from app.lib.scraping import CalendariosIdealScraper
from app.services.internal.scraping_service import (
    get_holidays_detail,
    get_path_for_location,
)


def calculate_working_days(year: int, holidays: list[date]) -> Laborables:
    working_days = {}

    current_date = date(year, 1, 1)
    while current_date <= date(year, 12, 31):
        if (
            current_date not in holidays and current_date.weekday() < 5
        ):  # Monday(0) to Friday(4) are considered working days
            current_month = str(current_date.month)
            working_days[current_month] = working_days.get(current_month, 0) + 1
        current_date += timedelta(days=1)
    working_days["total"] = sum(working_days.values())

    return Laborables(**working_days)


def get_laborables(
    year: int,
    location: str,
    scraper: CalendariosIdealScraper = CalendariosIdealScraper(),
) -> LaborablesResponse:
    path, matched_location = get_path_for_location(location, scraper)

    scraped_holidays = get_holidays_detail(path, year, scraper)
    holidays_dates = [holiday.date for holiday in scraped_holidays.data]


    return LaborablesResponse(
        laborables=calculate_working_days(year, holidays_dates),
        año=year,
        municipio=matched_location,
        fuente=scraped_holidays.source,
    )
