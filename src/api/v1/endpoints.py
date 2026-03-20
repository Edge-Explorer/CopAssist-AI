from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

alerts_router = APIRouter()
telemetry_router = APIRouter()

# Schema for Alerts
class Alert(BaseModel):
    id: str
    severity: str # "CRITICAL", "WARNING", "INFO"
    location: str
    timestamp: datetime
    description: str
    recommended_action: str

# Schema for Telemetry
class TelemetryData(BaseModel):
    sensor_id: str
    person_count: int
    crowd_density: float # 0.0 to 1.0
    anomalies_detected: List[str]
    timestamp: datetime

# In-memory mock storage for initial development
mock_alerts = []
mock_telemetry = []

@alerts_router.get("/", response_model=List[Alert])
async def get_alerts(severity: Optional[str] = None):
    if severity:
        return [alert for alert in mock_alerts if alert.severity == severity]
    return mock_alerts

@alerts_router.get("/summary")
async def get_alert_summary():
    return {
        "total_alerts": len(mock_alerts),
        "critical": len([a for a in mock_alerts if a.severity == "CRITICAL"]),
        "latest_update": datetime.now()
    }

@telemetry_router.post("/")
async def submit_telemetry(data: TelemetryData):
    mock_telemetry.append(data)
    # This would normally trigger the Analysis Agent
    return {"status": "success", "processed": True}

@telemetry_router.get("/")
async def get_latest_telemetry():
    return mock_telemetry[-10:] if mock_telemetry else []
