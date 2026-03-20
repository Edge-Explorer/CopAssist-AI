from fastapi import APIRouter
from src.api.v1.endpoints import alerts_router, telemetry_router

api_router = APIRouter()

# Register sub-routers for different modules
api_router.include_router(alerts_router, prefix="/v1/alerts", tags=["Alerts"])
api_router.include_router(telemetry_router, prefix="/v1/telemetry", tags=["Telemetry"])
