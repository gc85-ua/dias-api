import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.v1 import router
from app.core.logging_config import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.exceptions import AppError, ScrapingError

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Dias Laborables y Festivos en España",
    description="Servicio para consultar días laborables según municipio y año, con soporte para diferentes formatos de mes.",
    version="1.0.0",
)

app.add_middleware(RequestIDMiddleware)


@app.exception_handler(ScrapingError)
async def scraping_error_handler(request: Request, exc: ScrapingError):
    logger.warning(
        "Scraping error",
        extra={"event_name": "scraping.error", "error_code": exc.code, "error_category": exc.category, "retryable": exc.retryable, **exc.context},
    )
    status = 404 if exc.category == "not_found" else 503
    return JSONResponse(status_code=status, content={"error_code": exc.code, "message": exc.safe_message})

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.warning(
        "Application error",
        extra={"event_name": "app.error", "error_code": exc.code, "error_category": exc.category, "retryable": exc.retryable, **exc.context},
    )
    status = 404 if exc.category == "not_found" else 500
    return JSONResponse(status_code=status, content=exc.to_dict())


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        extra={"event_name": "app.unhandled_error"},
    )
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
    )


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


@app.get("/ping", description="Endpoint para verificar la disponibilidad del servicio", tags=["Health Check"])
async def ping():
    return {"message": "pong"}


app.include_router(router, prefix="/v1")
