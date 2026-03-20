import cv2
import threading
import requests
import queue
import os
from datetime import datetime

class CrowdDetector:
    """
    Real-time Detection using BOTH HOG (Person) and Haar Cascades (Face).
    This ensures it identifies you instantly via webcam even while sitting.
    """
    def __init__(self, sensor_id="CAM_HOG_01"):
        self.sensor_id = sensor_id
        
        # 1. HOG Person Detector (Good for full body/patrolling)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # 2. Haar Cascade Face Detector (Best for webcam/sitting officers)
        # Using the standard XML file built into OpenCV
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.api_url = "http://localhost:8000/api/v1/telemetry/"
        self.telemetry_queue = queue.Queue(maxsize=10)
        self.telemetry_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.telemetry_thread.start()

    def _sender_loop(self):
        while True:
            try:
                payload = self.telemetry_queue.get()
                requests.post(self.api_url, json=payload, timeout=2)
                self.telemetry_queue.task_done()
            except Exception: pass

    def detect_and_report(self, source=0):
        cap = cv2.VideoCapture(source)
        print(f"Starting Multi-Mode Detector on {self.sensor_id}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # --- Detection Logic ---
            # A. Full Body (HOG)
            people_boxes, _ = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(8, 8), scale=1.05)
            
            # B. Face (Haar) - Fast and accurate for sitting
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            # We combine the counts (using max to avoid double counting same person)
            person_count = max(len(people_boxes), len(faces))
            density = min(person_count / 15.0, 1.0) 

            # --- Telemetry ---
            if not self.telemetry_queue.full():
                payload = {
                    "sensor_id": self.sensor_id,
                    "person_count": person_count,
                    "crowd_density": round(density, 2),
                    "anomalies_detected": ["CROWD_CONGESTION"] if density > 0.7 else [],
                    "timestamp": datetime.now().isoformat()
                }
                self.telemetry_queue.put(payload)

            # --- Visual Feedback ---
            # Draw Face boxes (Blue)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Draw Body boxes (Green)
            for (x, y, w, h) in people_boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(frame, f"Detected: {person_count}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("CopAssist AI - Real CV Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = CrowdDetector()
    detector.detect_and_report(source=0)
