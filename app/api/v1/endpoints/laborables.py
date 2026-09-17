import logging
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query

from app.exceptions import ResourceNotFoundException
from app.schemas.services import LaborablesResponse
from app.services.laborables_service import get_laborables as gl

logger = logging.getLogger(__name__)

endpoint = APIRouter()



@endpoint.get("/", 
              response_model=LaborablesResponse, 
              summary="Obtener días laborables por mes según municipio", 
              description="Devuelve un objeto con los días laborables de cada mes y el total de días laborables en el año.")
async def get_laborables(municipio: str, año: int | None = Query(default=datetime.now(tz=UTC).year, description="Año para el cual se desean obtener los días laborables. Si no se proporciona, se utilizará el año actual.")):
    try:
        logger.info("Fetching laborables", extra={"municipio": municipio, "año": año})
        response: LaborablesResponse = gl(year=año, location=municipio)
        logger.debug("Fetched laborables data", extra={"data_is_empty": not response.laborables})
        return response
    except ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Resource not found")