import logging

from app.core.decorators import cached_operation
from app.exceptions import (
    LocationNotFoundError,
    ParsingError,
    ScrapingError,
)
from app.lib.scraping import CalendariosIdealScraper
from app.lib.utils import fuzzy_match_from_dict
from app.schemas.scraping import ScrapedHolidaysDetail

logger = logging.getLogger(__name__)


@cached_operation(
    ttl=86400,
    cache_prefix="scraped",
    cache_key_params=["path", "year"],
    expected_model=ScrapedHolidaysDetail,
)
def get_holidays_detail(
    path: str, year: int, scraper: CalendariosIdealScraper
) -> ScrapedHolidaysDetail:
    scraped_holidays: ScrapedHolidaysDetail = None
    
    try:
        scraped_holidays = scraper.scrape_holidays(path, year)
    except ParsingError as e:
        logger.warning(
            "Parsing error occurred",
            exc_info=True,
            extra={"event_name": "scraping.parsing_error", "path": path, "year": year, "error": str(e), "error_code": e.code, "error_category": e.category},
        )
    except ScrapingError as e:
        logger.warning(
            "Scraping error occurred",
            exc_info=True,
            extra={"event_name": "scraping.fetch_error", "path": path, "year": year, "error": str(e), "error_code": e.code, "error_category": e.category, "retryable": e.retryable, "context":e.context},
        )
        raise
    except Exception:
        raise

    model_dump = scraped_holidays.model_dump()
    logger.debug(
        "Scraped holidays data fields",
        extra={"event_name": "scraping.data_parsed", "path": path, "year": year, "data_fields": list(model_dump.keys())},
    )
    for field in model_dump:
        if not model_dump[field]:
            logger.warning(
                "Field is empty or None",
                extra={"event_name": "scraping.empty_field", "path": path, "year": year, "field": field, "value": model_dump[field]},
            )

    return scraped_holidays


def get_path_for_location(
    location: str, scraper: CalendariosIdealScraper
) -> tuple[str, str]:
    logger.info(
        "Finding scraping path for location",
        extra={"event_name": "location.lookup", "location": location},
    )
    path_dict = scraper.sitemap
    fuzzy_result = fuzzy_match_from_dict(location, path_dict)
    path = fuzzy_result["best_match_value"]
    matched_location = fuzzy_result["best_match_key"]
    if path is None:
        raise LocationNotFoundError(location)
    return path, matched_location
