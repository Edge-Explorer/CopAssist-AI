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
    # New GPS fields for CopMap integration - Neel
    latitude: Optional[float] = 19.0760 # Default Mumbai coordinates
    longitude: Optional[float] = 72.8777

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
    Also saves to PostgreSQL for our persistent logs!
    """
    print(f"📡 Telemetry received from {data.sensor_id} - People: {data.person_count}")
    from src.agents.vision_agent import vision_agent
    from src.agents.analysis_agent import analysis_agent
    from src.agents.llm_agent import llm_agent
    from src.db.models import SessionLocal, DBTelemetry, DBAlert
    
    # 1. Trigger Multi-Agent Flow FIRST to get the analysis!
    vision_summary = await vision_agent.process_telemetry(data)
    analysis_report = await analysis_agent.analyze(vision_summary)
    decision = await llm_agent.generate_alert(analysis_report)
    
    # 2. Save Telemetry + Analysis + Location!
    db = SessionLocal()
    try:
        new_telemetry = DBTelemetry(
            sensor_id=data.sensor_id,
            person_count=data.person_count,
            crowd_density=data.crowd_density,
            timestamp=data.timestamp,
            analysis_summary=analysis_report,
            latitude=data.latitude,
            longitude=data.longitude
        )
        db.add(new_telemetry)
        db.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        db.close()
    
    # 3. Store alert if severity is WARNING or CRITICAL
    if any(keyword in str(decision["decision"]).upper() for keyword in ["CRITICAL", "WARNING"]):
        alert_id = f"ALT_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save Alert to PostgreSQL
        db = SessionLocal()
        try:
            new_alert = DBAlert(
                id=alert_id,
                severity="CRITICAL" if "CRITICAL" in decision["decision"].upper() else "WARNING",
                location=f"Sensor_{data.sensor_id}",
                timestamp=datetime.now(),
                description=decision["decision"],
                recommended_action="Dispatching Patrol - SOP Followed",
                latitude=data.latitude,
                longitude=data.longitude
            )
            db.add(new_alert)
            db.commit()
        except Exception as e:
            print(f"Alert DB Error: {e}")
        finally:
            db.close()
            
        return {"status": "success", "alert_generated": True, "alert_id": alert_id, "reasoning": decision["analysis"]}

    return {"status": "success", "alert_generated": False, "reasoning": decision["analysis"]}

@telemetry_router.get("/")
async def get_latest_telemetry():
    return mock_telemetry[-10:] if mock_telemetry else []
