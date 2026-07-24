from fastapi import APIRouter, Query
from app.services.laborables_service import get_laborables as gl
from app.schemas.services import LaborablesResponse
from datetime import date

endpoint = APIRouter()



@endpoint.get("/", 
              response_model=LaborablesResponse, 
              summary="Obtener días laborables por mes según municipio", 
              description="Devuelve un objeto con los días laborables de cada mes y el total de días laborables en el año.")
async def get_laborables(municipio: str, año: int | None = Query(default=date.today().year, description="Año para el cual se desean obtener los días laborables. Si no se proporciona, se utilizará el año actual.")):
    return gl(year=año, location=municipio)