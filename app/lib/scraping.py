import logging
import re
from datetime import date
from typing import Any

import requests
from bs4 import BeautifulSoup

from app.core.config import DATA_DIR
from app.exceptions import ParsingError, ScrapingError
from app.lib.constants.dictionaries import CAPITALIZED_MONTHS
from app.lib.utils import (
    export_to_json,
    get_property_values_from_leaves,
    import_from_json,
)
from app.schemas.scraping import Holiday, HolidayType, ScrapedHolidaysDetail

logger = logging.getLogger(__name__)

def try_get(
    url: str, retries: int = 3, timeout: int = 5
) -> requests.Response | None:
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(
                "Url fetching has failed",
                extra={"event_name": "http.request_failed", "url": url, "attempt": attempt + 1, "error": str(e)},
            )
    return None


def get_subpaths_dict_from(
    path: str,
    with_selector: str,
    with_position: int,
    with_pattern: str,
    base_url: str,
) -> dict[str, str]:
    url = f"{base_url}{path}"
    response = None
    path_dicts = {}

    response = try_get(url)
    if response is None:
        raise ScrapingError("Error fetching data from external source", url=url)

    soup = BeautifulSoup(response.text, "html.parser")
    lists = soup.select(with_selector)

    if lists is None or len(lists) == 0:
        raise ParsingError(
            f"Failed to find any element with selector {with_selector}",
            context={"url": url, "selector": with_selector},
        )

    items = lists[0].find_all("a")
    if not items or len(items) == 0:
        raise ParsingError(
            f"Failed to find any 'a' element with selector {with_selector}",
            context={"url": url, "selector": with_selector},
        )

    pattern = re.compile(with_pattern)

    for item in items:
        href = item.get("href")
        text = item.text.strip()
        slug = href.split("/")[with_position]
        match = pattern.search(text)
        path_dicts[f"{path}/{slug}"] = match.group(1) if match.groups() else text

    return path_dicts


class CalendariosIdealScraper:
    _instance = None

    BASE_URL = "https://calendarios.ideal.es"
    CCAA_LIST_SELECTOR = "body > div.v-w > div.v-c.v-n-mrg > div.v-c > div > div:nth-child(1) > div > div:nth-child(6) > div > ul"
    PROVINCIAS_LIST_SELECTOR = "body > div.v-w > div.v-c.v-n-mrg > div.v-c > div > div:nth-child(1) > div > div:nth-child(15) > div > ul"
    MUNICIPIOS_LIST_SELECTOR = "body > div.v-w > div.v-c.v-n-mrg > div.v-c > div > div:nth-child(1) > div > div:nth-child(6) > div > ul"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, sitemap_filename: str = "sitemap.json"):
        if not hasattr(self, "initialized"):
            self.__sitemap_filename_path = DATA_DIR / sitemap_filename
            self.__sitemap = {}
            self.__load_or_build_sitemap()
            self.initialized = True

    def __load_or_build_sitemap(self):
        sitemap_nested_dict = None
        try:
            sitemap_nested_dict = import_from_json(self.__sitemap_filename_path)
        except FileNotFoundError:
            sitemap_nested_dict = self.__class__.get_nested_sitemap_dict()
            if sitemap_nested_dict:
                export_to_json(
                    sitemap_nested_dict, self.__sitemap_filename_path, overwrite=True
                )
        if sitemap_nested_dict is None:
            raise FileNotFoundError(
                f"Failed to load or build sitemap from {self.__sitemap_filename_path}"
            )
        self.__sitemap = get_property_values_from_leaves(
            sitemap_nested_dict, "children", "path"
        )

    @property
    def sitemap(self) -> dict[str, str]:
        return self.__sitemap

    @classmethod
    def get_nested_sitemap_dict(cls) -> dict[str, Any]:
        sitemap_dict = {}
        ccaa_dict = get_subpaths_dict_from(
            base_url=cls.BASE_URL,
            path="laboral",
            with_selector=cls.CCAA_LIST_SELECTOR,
            with_position=2,
            with_pattern=r"de\s+(.+?)\s+\d{4}$",
        )
        for ccaa_path, ccaa_name in ccaa_dict.items():
            provincia_dict = get_subpaths_dict_from(
                base_url=cls.BASE_URL,
                path=ccaa_path,
                with_selector=cls.PROVINCIAS_LIST_SELECTOR,
                with_position=3,
                with_pattern=r"provincia\s+de\s+(.+?)\s+\d{4}$",
            )
            sitemap_dict[ccaa_name] = {
                "path": ccaa_path,
                "has_calendar": True,
                "children": {},
            }
            for provincia_path, provincia_name in provincia_dict.items():
                municipio_dict = get_subpaths_dict_from(
                    base_url=cls.BASE_URL,
                    path=provincia_path,
                    with_selector=cls.MUNICIPIOS_LIST_SELECTOR,
                    with_position=4,
                    with_pattern=r"de\s+(.+?)$",
                )
                sitemap_dict[ccaa_name]["children"][provincia_name] = {
                    "path": provincia_path,
                    "has_calendar": False,
                    "children": {},
                }
                for municipio_path, municipio_name in municipio_dict.items():
                    sitemap_dict[ccaa_name]["children"][provincia_name]["children"][
                        municipio_name
                    ] = {"path": municipio_path, "has_calendar": True, "children": {}}
        return sitemap_dict

    def scrape_holidays(self, path: str, year: int) -> ScrapedHolidaysDetail:
        url = f"{self.__class__.BASE_URL}/{path}/{year}"

        response = try_get(url)
        if response is None:
            raise ScrapingError("Error fetching data from external source", url=url)
        if response.status_code == 404:
            raise ScrapingError(
                f"Data not found for path {path} and year {year}",
                category="not_found",
                url=url,
                context={"path": path, "year": year},
                safe_message="The requested data was not found.",
            )
        if response.status_code != 200:
            raise ScrapingError(
                f"Unexpected status code {response.status_code} when fetching data from external source",
                url=url,
                context={"received_status_code": response.status_code},
                safe_message="An unexpected error occurred while fetching data.",
            )
        soup = BeautifulSoup(response.text, "html.parser")

        months = soup.find_all("table", class_="bm-calendar")
        holidays = []
        for month in months:
            month_name = month.find(class_="bm-calendar-month-title").text.strip()
            month_id = CAPITALIZED_MONTHS.get(month_name)
            if month_id is None:
                raise ParsingError(
                    f"Unexpected month name: {month_name}",
                    context={"month_name": month_name, "path": path, "year": year},
                )

            holidays_nacional = month.find_all(
                "td", class_="bm-calendar-state-nacional"
            )
            holidays_autonomico = month.find_all(
                "td", class_="bm-calendar-state-autonomico"
            )
            holidays_local = month.find_all("td", class_="bm-calendar-state-local")

            holidays.extend(
                [
                    Holiday(
                        date=date(year, int(month_id), int(h.text.strip())),
                        name=h.get("title", ""),
                        type=HolidayType.nacional,
                    )
                    for h in holidays_nacional
                ]
                + [
                    Holiday(
                        date=date(year, int(month_id), int(h.text.strip())),
                        name=h.get("title", ""),
                        type=HolidayType.autonomico,
                    )
                    for h in holidays_autonomico
                ]
                + [
                    Holiday(
                        date=date(year, int(month_id), int(h.text.strip())),
                        name=h.get("title", ""),
                        type=HolidayType.local,
                    )
                    for h in holidays_local
                ]
            )
        logger.debug(
            "Scraped holidays data fields",
            extra={"event_name": "scraping.data_scraped", "path": path, "year": year, "data_length": len(holidays)},
        )
        return ScrapedHolidaysDetail(
            year=year,
            source=url,
            data=sorted(holidays, key=lambda holiday: holiday.date) if holidays else []
        )
