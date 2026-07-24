from enum import Enum

from pydantic import BaseModel, HttpUrl
from datetime import date
from typing import List, Optional

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
    source: Optional[HttpUrl] = None

class ScrapedHolidaysDetail(Scraped):
    data: Optional[List[Holiday]] = None
