from datetime import date

from pydantic import AliasChoices, BaseModel, HttpUrl, Field, ConfigDict
from typing import List
class Locations(BaseModel):
    locations: List[str]

class Laborables(BaseModel):
    enero: int = Field(..., validation_alias=AliasChoices("1","enero", "January"))
    febrero: int = Field(..., validation_alias=AliasChoices("2","febrero", "February"))
    marzo: int = Field(..., validation_alias=AliasChoices("3","marzo", "March"))
    abril: int = Field(..., validation_alias=AliasChoices("4","abril", "April"))
    mayo: int = Field(..., validation_alias=AliasChoices("5","mayo", "May"))
    junio: int = Field(..., validation_alias=AliasChoices("6","junio", "June"))
    julio: int = Field(..., validation_alias=AliasChoices("7","julio", "July"))
    agosto: int = Field(..., validation_alias=AliasChoices("8","agosto", "August"))
    septiembre: int = Field(..., validation_alias=AliasChoices("9","septiembre", "September"))
    octubre: int = Field(..., validation_alias=AliasChoices("10","octubre", "October"))
    noviembre: int = Field(..., validation_alias=AliasChoices("11","noviembre", "November"))
    diciembre: int = Field(..., validation_alias=AliasChoices("12","diciembre", "December"))
    total: int = Field(..., validation_alias=AliasChoices("total"))
    model_config = ConfigDict(extra="forbid", populate_by_name=True, serialize_by_alias=True)

class ServiceResponse(BaseModel):
    año: int
    municipio: str
    fuente: HttpUrl

class LaborablesResponse(ServiceResponse):
    laborables: Laborables

class Festivo(BaseModel):
    fecha: date = Field(..., validation_alias=AliasChoices("date", "fecha"))
    nombre: str = Field(..., validation_alias=AliasChoices("name", "nombre"))
    tipo: str = Field(..., validation_alias=AliasChoices("type", "tipo"))

class FestivosResponse(ServiceResponse):
    festivos: List[Festivo]