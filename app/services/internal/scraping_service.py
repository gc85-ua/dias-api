from app.core.decorators import cached_operation
from app.lib.exceptions import ResourceNotFoundException
from app.schemas.scraping import ScrapedHolidaysDetail
from app.lib.scraping import CalendariosIdealScraper
from app.lib.utils import fuzzy_match_from_dict


@cached_operation(
    ttl=86400,
    cache_prefix="holidays",
    cache_key_params=["path", "year"],
    expected_model=ScrapedHolidaysDetail,
)
def get_holidays_detail(
    path: str, year: int, scraper: CalendariosIdealScraper
) -> ScrapedHolidaysDetail:

    scraped_holidays: ScrapedHolidaysDetail = scraper.scrape_holidays(path, year)

    return scraped_holidays


def get_path_for_location(
    location: str, scraper: CalendariosIdealScraper
) -> tuple[str, str]:

    path_dict = scraper.sitemap
    fuzzy_result = fuzzy_match_from_dict(location, path_dict)
    path = fuzzy_result["best_match_value"]
    matched_location = fuzzy_result["best_match"]

    if not path:
        raise ResourceNotFoundException(f"Path not found for location: {location}")

    return path, matched_location
