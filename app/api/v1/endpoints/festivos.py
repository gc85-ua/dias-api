import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Query

from app.schemas.services import FestivosResponse
from app.services.festivos_service import get_festivos as gf

logger = logging.getLogger(__name__)

endpoint = APIRouter()


@endpoint.get("/", 
              response_model=FestivosResponse, 
              summary="Obtener días festivos por mes según municipio", 
              description="Devuelve un objeto con los días festivos de cada mes detallando tipo, nombre y fecha de cada festivo.")
async def get_festivos(municipio: str, año: int | None = Query(default=datetime.now(tz=UTC).year, description="Año para el cual se desean obtener los días festivos. Si no se proporciona, se utilizará el año actual.")):
    logger.info("Fetching festivos", extra={"event_name": "festivos.fetch", "municipio": municipio, "año": año})
    response = gf(year=año, location=municipio)
    logger.debug("Fetched festivos data", extra={"event_name": "festivos.fetched", "data_is_empty": len(response.festivos) == 0})
    return response
