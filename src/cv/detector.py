import cv2
import threading
import requests
import queue
import collections
import mediapipe as mp
from datetime import datetime

class CrowdDetector:
    """
    Intelligent CV Detector:
    1. HOG + Haar Cascade: Multi-mode counting.
    2. MediaPipe Pose: Behavioral Analysis (Arms raised = Threat detection).
    3. Moving Average: 10-frame smoothing for robust counts.
    """
    def __init__(self, sensor_id="CAM_HOG_01"):
        self.sensor_id = sensor_id
        
        # --- 1. Detectors Setup ---
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # --- 2. MediaPipe Pose (For aggressive behavior) ---
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        
        # --- 3. Communication & Buffering ---
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
        print(f"Starting Pro-Level Guard on {self.sensor_id}...")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break

            frame = cv2.resize(frame, (640, 480))
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # --- A. Count People ---
            bodies, _ = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(4, 4), scale=1.05)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            self.count_buffer.append(max(len(bodies), len(faces)))
            smoothed_count = int(round(sum(self.count_buffer) / len(self.count_buffer)))
            density = min(smoothed_count / 15.0, 1.0)

            # --- B. Analyze Pose (Behavior Detection) ---
            results = self.pose.process(rgb_frame)
            anomalies = []
            if results.pose_landmarks:
                # Detect if hands are raised high (Aggressive or Distress signal)
                # Landmark 15 = Left Wrist, 16 = Right Wrist, 11/12 = Shoulders
                l_wrist = results.pose_landmarks.landmark[15].y
                r_wrist = results.pose_landmarks.landmark[16].y
                shoulder_y = min(results.pose_landmarks.landmark[11].y, results.pose_landmarks.landmark[12].y)
                
                if l_wrist < (shoulder_y - 0.1) or r_wrist < (shoulder_y - 0.1):
                    anomalies.append("AGGRESSIVE_STANCE")
                    cv2.putText(frame, "🚨 ALERT: THREAT DETECTED!", (200, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                # Visual Landmarks
                self.mp_draw.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # --- C. Telemetry Reporting ---
            if not self.telemetry_queue.full() and datetime.now().second % 3 == 0:
                payload = {
                    "sensor_id": self.sensor_id,
                    "person_count": smoothed_count,
                    "crowd_density": round(density, 2),
                    "anomalies_detected": anomalies or (["CROWD_CONGESTION"] if density > 0.7 else []),
                    "timestamp": datetime.now().isoformat(),
                    # Simulated Location: Gateway of India, Mumbai - Neel
                    "latitude": 18.9220,
                    "longitude": 72.8347
                }
                self.telemetry_queue.put(payload)

            # --- D. Rendering ---
            for (x, y, w, h) in faces: cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"Officer Feed - Active People: {smoothed_count}", (10, 440), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("CopAssist AI - Behavioral Patrol", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = CrowdDetector()
    detector.detect_and_report(source=0)
