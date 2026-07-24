from app.schemas.services import Festivo, FestivosResponse
from app.lib.scraping import CalendariosIdealScraper
from app.lib.exceptions import ResourceNotFoundException

from app.services.internal.scraping_service import (
    get_holidays_detail,
    get_path_for_location,
)


def get_festivos(
    year: int,
    location: str,
    scraper: CalendariosIdealScraper = CalendariosIdealScraper(),
) -> FestivosResponse:
    path, best_match = get_path_for_location(location, scraper)

    if not path:
        raise ResourceNotFoundException(f"Path not found for location: {location}")

    scraped_holidays = get_holidays_detail(path, year, scraper)
    festivos = [Festivo(**holiday.dict()) for holiday in scraped_holidays.data] if scraped_holidays.data else []
    return FestivosResponse(
        festivos=festivos,
        año=year,
        municipio=best_match,
        fuente=scraped_holidays.source,
    )
