from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.v1 import router
from app.core.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="API de Dias Laborables y Festivos en España",
    description="Servicio para consultar días laborables según municipio y año, con soporte para diferentes formatos de mes.",
    version="1.0.0"
)

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

@app.get("/ping", description="Endpoint para verificar la disponibilidad del servicio", tags=["Health Check"])
async def ping():
    return {"message": "pong"}

app.include_router(router, prefix="/v1")


