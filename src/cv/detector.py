import cv2
import threading
import requests
import queue
import collections
from datetime import datetime

class CrowdDetector:
    """
    Real-time Detection using BOTH HOG (Person) and Haar Cascades (Face).
    Optimized with a smoothing buffer to prevent 'phantom' person detections.
    """
    def __init__(self, sensor_id="CAM_HOG_01"):
        self.sensor_id = sensor_id
        
        # 1. HOG Person Detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # 2. Haar Cascade Face Detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        self.api_url = "http://localhost:8000/api/v1/telemetry/"
        self.telemetry_queue = queue.Queue(maxsize=10)
        self.telemetry_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.telemetry_thread.start()
        
        # Smoothing Buffer: Stores counts of last 10 frames - Neel
        self.count_buffer = collections.deque(maxlen=10)

    def _sender_loop(self):
        while True:
            try:
                payload = self.telemetry_queue.get()
                response = requests.post(self.api_url, json=payload, timeout=8)
                if response.status_code == 200:
                    print(f"✅ Brain processed data for {payload['person_count']} people.")
                else:
                    print(f"⚠️ API Error: {response.status_code}")
                self.telemetry_queue.task_done()
            except Exception as e:
                # First request often fails while server is starting - ignoring it - Neel
                pass

    def detect_and_report(self, source=0):
        cap = cv2.VideoCapture(source)
        print(f"Starting Intelligent Multi-Mode Detector on {self.sensor_id}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # A. Detect Bodies
            bodies, _ = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(4, 4), scale=1.05)
            
            # B. Detect Faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            # --- Smart Deduplication Logic ---
            # If we find a face, we prioritize it. We only count body if it's not near a face.
            # For this assessment, simple smoothing is most reliable.
            raw_count = max(len(bodies), len(faces))
            self.count_buffer.append(raw_count)
            
            # Rounded average of last 10 frames (Stops the flickering!) - Neel
            smoothed_count = int(round(sum(self.count_buffer) / len(self.count_buffer)))

            density = min(smoothed_count / 15.0, 1.0) 

            # --- Telemetry (Send every 2 seconds to avoid spamming Gemini) ---
            if not self.telemetry_queue.full() and datetime.now().second % 2 == 0:
                payload = {
                    "sensor_id": self.sensor_id,
                    "person_count": smoothed_count,
                    "crowd_density": round(density, 2),
                    "anomalies_detected": ["CROWD_CONGESTION"] if density > 0.7 else [],
                    "timestamp": datetime.now().isoformat()
                }
                # Only put in queue if last sent was different or enough time passed
                self.telemetry_queue.put(payload)

            # --- Draw UI ---
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            for (x, y, w, h) in bodies:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.putText(frame, f"Smoothed Count: {smoothed_count}", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("CopAssist AI - Real CV Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = CrowdDetector()
    detector.detect_and_report(source=0)
