import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Query

from app.schemas.services import LaborablesResponse
from app.services.laborables_service import get_laborables as gl

logger = logging.getLogger(__name__)

endpoint = APIRouter()


@endpoint.get("/", 
              response_model=LaborablesResponse, 
              summary="Obtener días laborables por mes según municipio y año", 
              description="Devuelve un objeto con los días laborables de cada mes y el total de días laborables en el año.")
async def get_laborables(municipio: str, año: int | None = Query(default=datetime.now(tz=UTC).year, description="Año para el cual se desean obtener los días laborables. Si no se proporciona, se utilizará el año actual.")):
    logger.info("Fetching laborables", extra={"event_name": "laborables.fetch", "municipio": municipio, "año": año})
    response: LaborablesResponse = gl(year=año, location=municipio)
    logger.debug("Fetched laborables data", extra={"event_name": "laborables.fetched", "data_is_empty": not response.laborables})
    return response
