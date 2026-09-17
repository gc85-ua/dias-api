import logging

from app.lib.scraping import CalendariosIdealScraper
from app.schemas.scraping import ScrapedHolidaysDetail
from app.schemas.services import Festivo, FestivosResponse
from app.services.internal.scraping_service import (
    get_holidays_detail,
    get_path_for_location,
)

logger = logging.getLogger(__name__)

def get_festivos(
    year: int,
    location: str,
    scraper: CalendariosIdealScraper | None = None,
) -> FestivosResponse:
    
    if scraper is None:
        scraper = CalendariosIdealScraper()

    path, best_match = get_path_for_location(location, scraper)
   
    scraped_holidays:ScrapedHolidaysDetail = get_holidays_detail(path, year, scraper)     
    
    festivos = [Festivo(**holiday.model_dump()) for holiday in scraped_holidays.data] if scraped_holidays.data else []
    
    return FestivosResponse(
        festivos=festivos,
        año=year,
        municipio=best_match,
        fuente=scraped_holidays.source,
    )
