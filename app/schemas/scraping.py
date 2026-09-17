from datetime import date
from enum import Enum

from pydantic import BaseModel, HttpUrl


class HolidayType(str,Enum):
    nacional = "nacional"
    autonomico = "autonomico"
    local = "local"

class Holiday(BaseModel):
    date: date
    name: str
    type: HolidayType

class Scraped(BaseModel):
    year: int
    source: HttpUrl | None = None

class ScrapedHolidaysDetail(Scraped):
    data: list[Holiday] = []
