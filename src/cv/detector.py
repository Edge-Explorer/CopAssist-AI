import cv2
import threading
import requests
import queue
import collections
import numpy as np
from datetime import datetime

class CrowdDetector:
    """
    Intelligent CV Detector (Robust Version):
    1. Count: Hybrid HOG + Haar Cascades.
    2. Behavior: Motion Analytics (Detects "Running" or "Sudden Movement").
    3. GPS: Integrated Location Intelligence for CopMap.
    """
    def __init__(self, sensor_id="CAM_HOG_01"):
        self.sensor_id = sensor_id
        
        # Detectors
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Motion History for "Behavioral Analysis" - Neel
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
        self.prev_gray = None
        
        self.api_url = "http://localhost:8000/api/v1/telemetry/"
        self.telemetry_queue = queue.Queue(maxsize=10)
        self.telemetry_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.telemetry_thread.start()
        
        self.count_buffer = collections.deque(maxlen=10)

    def _sender_loop(self):
        while True:
            try:
                payload = self.telemetry_queue.get()
                requests.post(self.api_url, json=payload, timeout=8)
                self.telemetry_queue.task_done()
            except Exception: pass

    def detect_and_report(self, source=0):
        cap = cv2.VideoCapture(source)
        print(f"Starting Intelligent Patrol on {self.sensor_id}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # --- 1. Aggressive Movement Detection (Behavior) ---
            motion_mask = self.fgbg.apply(frame)
            motion_pixels = cv2.countNonZero(motion_mask)
            
            anomalies = []
            # High Motion = "Running" or "Chaos" - Neel
            if motion_pixels > 80000: # Threshold for high activity
                anomalies.append("SUSPICIOUS_MOTION")
                cv2.putText(frame, "🚨 ALERT: HIGH-SPEED MOTION!", (150, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # --- 2. Crowd Counting ---
            bodies, _ = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(8, 8), scale=1.05)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            raw_count = max(len(bodies), len(faces))
            self.count_buffer.append(raw_count)
            smoothed_count = int(round(sum(self.count_buffer) / len(self.count_buffer)))
            density = min(smoothed_count / 15.0, 1.0)

            # --- 3. Telemetry ---
            if not self.telemetry_queue.full() and datetime.now().second % 3 == 0:
                payload = {
                    "sensor_id": self.sensor_id,
                    "person_count": smoothed_count,
                    "crowd_density": round(density, 2),
                    "anomalies_detected": anomalies or (["CROWD_CONGESTION"] if density > 0.7 else []),
                    "timestamp": datetime.now().isoformat(),
                    "latitude": 18.9220, "longitude": 72.8347
                }
                self.telemetry_queue.put(payload)

            # --- 4. Render ---
            for (x, y, w, h) in faces: cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"Officer Feed - Active People: {smoothed_count}", (10, 440), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("CopAssist AI - Tactical Patrol", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = CrowdDetector()
    detector.detect_and_report(source=0)
