from fastapi import APIRouter

from app.api.v1.endpoints import festivos, laborables

router = APIRouter()
router.include_router(laborables.endpoint, tags=["laborables"], prefix="/laborables")
router.include_router(festivos.endpoint, tags=["festivos"], prefix="/festivos")
