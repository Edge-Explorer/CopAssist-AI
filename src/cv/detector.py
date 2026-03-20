import cv2
import threading
import requests
import queue
from datetime import datetime

class CrowdDetector:
    """
    Real-time Person Detection using OpenCV's HOG + SVM.
    Optimized to be non-blocking using a dedicated telemetry thread.
    """
    def __init__(self, sensor_id="CAM_HOG_01"):
        self.sensor_id = sensor_id
        # Initialize the HOG person detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.api_url = "http://localhost:8000/api/v1/telemetry/"
        
        # Telemetry queue for async reporting (prevents UI lag) - Neel
        self.telemetry_queue = queue.Queue(maxsize=10)
        self.telemetry_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.telemetry_thread.start()

    def _sender_loop(self):
        """ Runs in the background and sends data to the API. """
        while True:
            try:
                payload = self.telemetry_queue.get()
                requests.post(self.api_url, json=payload, timeout=2)
                self.telemetry_queue.task_done()
            except Exception:
                # Silently drop failed telemetry to keep the system running
                pass

    def detect_and_report(self, source=0):
        cap = cv2.VideoCapture(source)
        print(f"Starting Optimized CV Detector on {self.sensor_id}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            # 1. Image Pre-processing for speed
            # Resizing makes HOG much faster on standard laptops!
            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 2. Run Detection (HOG is CPU intensive)
            boxes, _ = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(8, 8), scale=1.05)

            person_count = len(boxes)
            density = min(person_count / 15.0, 1.0) 

            # 3. Queue Telemetry (Non-blocking)
            if not self.telemetry_queue.full():
                payload = {
                    "sensor_id": self.sensor_id,
                    "person_count": person_count,
                    "crowd_density": round(density, 2),
                    "anomalies_detected": ["CROWD_CONGESTION"] if density > 0.7 else [],
                    "timestamp": datetime.now().isoformat()
                }
                self.telemetry_queue.put(payload)

            # 4. Draw UI
            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(frame, f"People: {person_count}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("CopAssist AI - Real CV Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = CrowdDetector()
    detector.detect_and_report(source=0)
