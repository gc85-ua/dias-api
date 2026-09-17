import logging

from app.core.decorators import cached_operation
from app.exceptions import (
    ParsingException,
    ResourceNotFoundException,
    ScrapingException,
)
from app.lib.scraping import CalendariosIdealScraper
from app.lib.utils import fuzzy_match_from_dict
from app.schemas.scraping import ScrapedHolidaysDetail

logger = logging.getLogger(__name__)


@cached_operation(
    ttl=86400,
    cache_prefix="holidays",
    cache_key_params=["path", "year"],
    expected_model=ScrapedHolidaysDetail,
)
def get_holidays_detail(
    path: str, year: int, scraper: CalendariosIdealScraper
) -> ScrapedHolidaysDetail:
    scraped_holidays: ScrapedHolidaysDetail = ScrapedHolidaysDetail(year=year, source=None, data=[])
    
    try:
        scraped_holidays = scraper.scrape_holidays(path, year)
    except ParsingException as e:
        logger.error("Parsing error occurred", extra={"path": path, "year": year, "error": str(e)})
    except ScrapingException as e:
        logger.error("Scraping error occurred", extra={"path": path, "year": year, "error": str(e)})
    except Exception:
        raise

    model_dump = scraped_holidays.model_dump()
    logger.debug("Scraped holidays data fields", extra={"path": path, "year": year, "data_fields": list(model_dump.keys())})
    for field in model_dump:
        if not model_dump[field]:
            logger.warning("Field is empty or None", extra={"path": path, "year": year, "field": field, "value": model_dump[field]})

    return scraped_holidays


def get_path_for_location(
    location: str, scraper: CalendariosIdealScraper
) -> tuple[str, str]:
    logger.info("Finding scraping path for location", extra={"location": location})
    path_dict = scraper.sitemap
    fuzzy_result = fuzzy_match_from_dict(location, path_dict)
    path = fuzzy_result["best_match_value"]
    matched_location = fuzzy_result["best_match_key"]
    if path is None:
        raise ResourceNotFoundException(f"No path found for location: {location}")
    return path, matched_location
