import random
import time
from datetime import datetime
from src.api.v1.endpoints import TelemetryData, submit_telemetry

def simulate_crowd_telemetry(sensor_id: str = "CAM_001"):
    """
    Simulates real-time telemetry from a CV sensor.
    Normally this would be the output of a YOLO/OpenCV model.
    """
    while True:
        # Simulate varying crowd sizes and densities
        # During 'night hours', keep person count low but add rare anomalies
        current_hour = datetime.now().hour
        
        if 22 <= current_hour or current_hour <= 5: # Night (10 PM to 6 AM)
            person_count = random.randint(0, 5) if random.random() > 0.05 else random.randint(20, 100)
            density = 0.05 if person_count < 10 else 0.75
        else: # Day (6 AM to 10 PM)
            person_count = random.randint(5, 40)
            density = person_count / 100 # Rough linear mapping
            
        anomalies = []
        if person_count > 50 and (22 <= current_hour or current_hour <= 5):
            anomalies.append("UNAUTHORIZED_GATHERING")
            
        telemetry = TelemetryData(
            sensor_id=sensor_id,
            person_count=person_count,
            crowd_density=round(density, 2),
            anomalies_detected=anomalies,
            timestamp=datetime.now()
        )
        
        print(f"[{telemetry.timestamp}] Sensor {telemetry.sensor_id}: {telemetry.person_count} persons, {telemetry.crowd_density} density - {telemetry.anomalies_detected}")
        
        # In a real app, this would be a POST to the API or a direct message to the Vision Agent
        # For simulation, we just print it
        time.sleep(5)

if __name__ == "__main__":
    # In practice, this script would run in its own process or as a task in our FastAPI app
    print("Starting CCTV Telemetry Simulator...")
    simulate_crowd_telemetry()
