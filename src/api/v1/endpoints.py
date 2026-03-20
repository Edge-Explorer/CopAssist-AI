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
    """
    Submits telemetry from a CV sensor and triggers the Multi-Agent Brain.
    """
    from src.agents.vision_agent import vision_agent
    from src.agents.analysis_agent import analysis_agent
    from src.agents.llm_agent import llm_agent
    
    mock_telemetry.append(data)
    
    # Trigger Multi-Agent Flow
    # 1. Vision Agent: Summarize raw telemetry
    vision_summary = await vision_agent.process_telemetry(data)
    
    # 2. Analysis Agent: Add context (time, patterns)
    analysis_report = await analysis_agent.analyze(vision_summary)
    
    # 3. LLM Agent: RAG + Decision making
    decision = await llm_agent.generate_alert(analysis_report)
    
    # Store alert if severity is WARNING or CRITICAL (mock-up threshold)
    if any(keyword in decision["decision"].upper() for keyword in ["CRITICAL", "WARNING"]):
        alert = Alert(
            id=f"ALT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            severity="CRITICAL" if "CRITICAL" in decision["decision"].upper() else "WARNING",
            location=f"Sensor_{data.sensor_id}",
            timestamp=datetime.now(),
            description=decision["decision"],
            recommended_action="Dispatch Patrol / Notify Dispatch" 
        )
        mock_alerts.append(alert)
        return {"status": "success", "alert_generated": True, "alert_id": alert.id, "reasoning": decision["analysis"]}

    return {"status": "success", "alert_generated": False, "reasoning": decision["analysis"]}

@telemetry_router.get("/")
async def get_latest_telemetry():
    return mock_telemetry[-10:] if mock_telemetry else []
