from fastapi import APIRouter, Query
from app.services.festivos_service import get_festivos as gf
from app.schemas.services import FestivosResponse
from datetime import date

endpoint = APIRouter()



@endpoint.get("/", 
              response_model=FestivosResponse, 
              summary="Obtener días festivos por mes según municipio", 
              description="Devuelve un objeto con los días festivos de cada mes detallando tipo, nombre y fecha de cada festivo.")
async def get_festivos(municipio: str, año: int | None = Query(default=date.today().year, description="Año para el cual se desean obtener los días festivos. Si no se proporciona, se utilizará el año actual.")):
    return gf(year=año, location=municipio)