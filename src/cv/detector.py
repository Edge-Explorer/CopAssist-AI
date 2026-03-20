import cv2
import time
import requests
from datetime import datetime

class CrowdDetector:
    """
    Real-time Person Detection using OpenCV's HOG + SVM.
    This provides 'Real CV' telemetry for the CopAssist brain.
    """
    def __init__(self, sensor_id="CAM_HOG_01"):
        self.sensor_id = sensor_id
        # Initialize the HOG descriptor/person detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.api_url = "http://localhost:8000/api/v1/telemetry/"

    def detect_and_report(self, source=0):
        """
        source: 0 for webcam, or path to a video file.
        """
        cap = cv2.VideoCapture(source)
        print(f"Starting CV Detector on {self.sensor_id}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize for faster processing (Student-level optimization!)
            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect people
            boxes, weights = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(8, 8), scale=1.05)

            person_count = len(boxes)
            density = min(person_count / 20.0, 1.0) # Assume 20 people is max density for this view

            # Draw boxes on frame for the visual demo
            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(frame, f"People: {person_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("CopAssist AI - Real CV Feed", frame)

            # Send telemetry to our FastAPI backend
            try:
                payload = {
                    "sensor_id": self.sensor_id,
                    "person_count": person_count,
                    "crowd_density": round(density, 2),
                    "anomalies_detected": ["CROWD_CONGESTION"] if density > 0.7 else [],
                    "timestamp": datetime.now().isoformat()
                }
                requests.post(self.api_url, json=payload, timeout=1)
            except Exception:
                # Silently fail if API isn't up, so the CV feed doesn't lag
                pass

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = CrowdDetector()
    # Note: Using 0 for webcam. If you have a video file, put the path here!
    detector.detect_and_report(source=0)
