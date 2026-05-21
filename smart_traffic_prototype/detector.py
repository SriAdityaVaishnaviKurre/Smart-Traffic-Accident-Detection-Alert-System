# # detector.py
# import cv2
# import time
# from ultralytics import YOLO
# import numpy as np
# # import osq

# class TrafficDetector:
#     def __init__(self, video_path, notifier=None):
#         self.video_path = video_path
#         self.notifier = notifier

#         print("🚦 Loading YOLO models...")
#         self.vehicle_model = YOLO("yolov8n.pt")  # general detection
#         self.smoke_model = YOLO("smoke.pt") if os.path.exists("smoke.pt") else None
#         self.violence_model = YOLO("violence.pt") if os.path.exists("violence.pt") else None

#         self.last_alert_time = 0
#         self.alert_cooldown = 20  # seconds
#         print("✅ Models loaded successfully.")

#     def run_detection(self):
#         cap = cv2.VideoCapture(self.video_path)
#         if not cap.isOpened():
#             print("❌ Error: Could not open video source.")
#             return

#         print("🎥 Starting detection...")
#         frame_no = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             frame_no += 1
#             frame = cv2.resize(frame, (960, 540))

#             # ===== YOLO detections =====
#             results = self.vehicle_model(frame, stream=True)
#             detected_labels = []
#             person_count = 0
#             vehicle_count = 0

#             for r in results:
#                 for box in r.boxes:
#                     cls = int(box.cls[0])
#                     label = self.vehicle_model.names[cls]
#                     conf = float(box.conf[0])
#                     (x1, y1, x2, y2) = map(int, box.xyxy[0])

#                     if label in ["car", "truck", "bus", "motorbike"]:
#                         vehicle_count += 1
#                     elif label == "person":
#                         person_count += 1

#                     detected_labels.append(label)
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                     cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 6),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#             # ===== Smoke Detection =====
#             smoke_detected = False
#             if self.smoke_model:
#                 smoke_results = self.smoke_model(frame, stream=True)
#                 for r in smoke_results:
#                     for box in r.boxes:
#                         smoke_detected = True
#                         (x1, y1, x2, y2) = map(int, box.xyxy[0])
#                         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
#                         cv2.putText(frame, "Smoke/Fire", (x1, y1 - 6),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#             # ===== Violence / Crowd Detection =====
#             crowd_detected = False
#             violence_detected = False
#             if self.violence_model:
#                 v_results = self.violence_model(frame, stream=True)
#                 for r in v_results:
#                     for box in r.boxes:
#                         violence_detected = True
#                         (x1, y1, x2, y2) = map(int, box.xyxy[0])
#                         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
#                         cv2.putText(frame, "Fighting Detected", (x1, y1 - 6),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#             if person_count > 10:
#                 crowd_detected = True
#                 cv2.putText(frame, "⚠ Crowd Gathering", (10, 100),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

#             # ===== Show Traffic Info =====
#             status = "Free Flow" if vehicle_count < 10 else "Congested"
#             cv2.putText(frame, f"Traffic: {vehicle_count} ({status})", (10, 40),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

#             # ===== Alert Logic =====
#             current_time = time.time()
#             if (smoke_detected or violence_detected or crowd_detected or vehicle_count > 5) and \
#                 (current_time - self.last_alert_time >= self.alert_cooldown):

#                 self.last_alert_time = current_time
#                 ts = int(current_time)
#                 snapshot = f"logs/alert_{ts}.jpg"
#                 cv2.imwrite(snapshot, frame)

#                 event = {
#                     "time": time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "location": "Traffic Camera 1",
#                     "vehicle_count": vehicle_count,
#                     "snapshot": snapshot,
#                 }

#                 if smoke_detected:
#                     event["type"] = "Smoke/Fire Detected"
#                 elif violence_detected:
#                     event["type"] = "Violence/Fight Detected"
#                 elif crowd_detected:
#                     event["type"] = "Crowd Gathering Detected"
#                 else:
#                     event["type"] = "Possible Accident"

#                 print(f"🚨 Sending alert: {event['type']}")
#                 if self.notifier:
#                     self.notifier.send_alert(event)

#             cv2.imshow("Smart Traffic Monitoring", frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()


from ultralytics import YOLO
import cv2, time
import numpy as np
import os

class TrafficDetector:
    
    def __init__(self, video_path=None, notifier=None, cooldown=20):
        self.video_path = video_path
        self.notifier = notifier
        self.cooldown = cooldown
        self.last_alert_time = 0     # ⬅ cooldown tracker
        

        # Load YOLO models
        self.vehicle_model = YOLO("yolov8n.pt")

        try:
            if os.path.exists("smoke.pt"):
                self.smoke_model = YOLO("smoke.pt")
                print("✅ Loaded smoke/fire model")
            else:
                self.smoke_model = None
                print("⚠ smoke.pt not found, skipping smoke detection")
        except:
            self.smoke_model = None

        # Classes
        self.person_class = 0
        self.vehicle_classes = [2, 3, 5, 7]  # car, bike, bus, truck

    # ------------------------------
    # VEHICLE + PERSON DETECTION
    # ------------------------------
    def detect_vehicles_and_persons(self, frame):
        results = self.vehicle_model(frame, stream=True)
        detections, persons, vehicles = [], [], []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls)
                conf = float(box.conf)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = r.names[cls]

                detections.append((label, conf, (x1, y1, x2, y2)))

                if cls == self.person_class:
                    persons.append((x1, y1, x2, y2))
                elif cls in self.vehicle_classes:
                    vehicles.append((x1, y1, x2, y2))

        return detections, persons, vehicles

    # ------------------------------
    # SMOKE DETECTION
    # ------------------------------
    def detect_smoke(self, frame):
        if not self.smoke_model:
            return []
        smoke_boxes = []
        results = self.smoke_model(frame, stream=True)
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                smoke_boxes.append((x1, y1, x2, y2))
        return smoke_boxes

    # ------------------------------
    # COLLISION CHECK (IOU)
    # ------------------------------
    def compute_iou(self, box1, box2):
        x1, y1, x2, y2 = box1
        xb1, yb1, xb2, yb2 = box2

        xi1, yi1 = max(x1, xb1), max(y1, yb1)
        xi2, yi2 = min(x2, xb2), min(y2, yb2)

        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        area1 = (x2 - x1) * (y2 - y1)
        area2 = (xb2 - xb1) * (yb2 - yb1)
        union = area1 + area2 - inter_area

        return inter_area / union if union > 0 else 0

    def check_collisions(self, vehicles):
        collision_flag = False
        for i in range(len(vehicles)):
            for j in range(i + 1, len(vehicles)):
                if self.compute_iou(vehicles[i], vehicles[j]) > 0.2:
                    collision_flag = True
        return collision_flag

    # ------------------------------
    # SAFE ALERT SYSTEM WITH COOLDOWN
    # ------------------------------
    def trigger_alert(self, message):
        current = time.time()
        if current - self.last_alert_time >= self.cooldown:  # ⬅ No repeat within 20 sec
            self.last_alert_time = current
            if self.notifier:
                self.notifier.notify(message)

    # ------------------------------
    # MAIN LOOP
    # ------------------------------
    def run_detection(self):
        cap = cv2.VideoCapture(self.video_path or 0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            detections, persons, vehicles = self.detect_vehicles_and_persons(frame)
            collision_detected = self.check_collisions(vehicles)
            smoke = self.detect_smoke(frame)

            # Draw boxes
            for label, conf, (x1, y1, x2, y2) in detections:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Collision alert
            if collision_detected:
                cv2.putText(frame, "⚠ COLLISION!", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                self.trigger_alert("Vehicle collision detected")

            # Smoke alert
            for (x1, y1, x2, y2) in smoke:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                self.trigger_alert("Smoke/Fire detected")

            # Show output
            cv2.imshow("Smart Traffic Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()





# from ultralytics import YOLO
# import cv2, time
# import numpy as np
# import os

# class TrafficDetector:
    
#     def __init__(self, video_path=None, notifier=None):
#         self.video_path = video_path
#         self.notifier = notifier

#         # ✅ Always available YOLOv8 vehicle/person model
#         self.vehicle_model = YOLO("yolov8n.pt")   # default lightweight model

#         # ✅ Optional model (skip if missing)
#         try:
#             if os.path.exists("smoke.pt"):
#                 self.smoke_model = YOLO("smoke.pt")
#                 print("✅ Loaded smoke/fire model")
#             else:
#                 self.smoke_model = None
#                 print("⚠ smoke.pt not found, skipping smoke detection")
#         except Exception as e:
#             self.smoke_model = None
#             print(f"⚠ Could not load smoke.pt: {e}")

#         # COCO class IDs
#         self.person_class = 0
#         self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

#         self.prev_vehicle_boxes = []

#     def detect_vehicles_and_persons(self, frame):
#         """Detect vehicles and persons in a frame"""
#         results = self.vehicle_model(frame, stream=True)
#         detections, persons, vehicles = [], [], []

#         for r in results:
#             for box in r.boxes:
#                 cls = int(box.cls)
#                 conf = float(box.conf)
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 label = r.names[cls]
#                 detections.append((label, conf, (x1, y1, x2, y2)))

#                 if cls == self.person_class:
#                     persons.append((x1, y1, x2, y2))
#                 elif cls in self.vehicle_classes:
#                     vehicles.append((x1, y1, x2, y2))

#         return detections, persons, vehicles

#     def detect_smoke(self, frame):
#         """Detect smoke/fire if smoke model exists"""
#         if not self.smoke_model:
#             return []
#         results = self.smoke_model(frame, stream=True)
#         smoke_boxes = []
#         for r in results:
#             for box in r.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 smoke_boxes.append((x1, y1, x2, y2))
#         return smoke_boxes

#     def check_collisions(self, vehicles):
#         """Naive vehicle collision detection (overlapping boxes)"""
#         collisions = []
#         for i, v1 in enumerate(vehicles):
#             for j, v2 in enumerate(vehicles):
#                 if i >= j:
#                     continue
#                 iou = self.compute_iou(v1, v2)
#                 if iou > 0.2:  # overlap threshold
#                     # collisions.append((v1, v2))
#                     continue
#         return collisions

#     @staticmethod
#     def compute_iou(box1, box2):
#         """Compute overlap (IoU) between two bounding boxes"""
#         x1, y1, x2, y2 = box1
#         x1b, y1b, x2b, y2b = box2

#         xi1, yi1 = max(x1, x1b), max(y1, y1b)
#         xi2, yi2 = min(x2, x2b), min(y2, y2b)
#         inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

#         box1_area = (x2 - x1) * (y2 - y1)
#         box2_area = (x2b - x1b) * (y2b - y1b)
#         union_area = box1_area + box2_area - inter_area

#         return inter_area / union_area if union_area > 0 else 0

#     def run_detection(self):
#         cap = cv2.VideoCapture(self.video_path or 0)
#         frame_no = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             frame_no += 1

#             detections, persons, vehicles = self.detect_vehicles_and_persons(frame)
#             collisions = self.check_collisions(vehicles)
#             smoke = self.detect_smoke(frame)

#             # Draw detections
#             for label, conf, (x1, y1, x2, y2) in detections:
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 5),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#             # Highlight collisions
#             for v1, v2 in collisions:
#                 cv2.rectangle(frame, (v1[0], v1[1]), (v1[2], v1[3]), (0, 0, 255), 2)
#                 cv2.rectangle(frame, (v2[0], v2[1]), (v2[2], v2[3]), (0, 0, 255), 2)
#                 cv2.putText(frame, "⚠ Vehicle Collision!", (10, 60),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
#                 if self.notifier:
#                     self.notifier.send_alert("Vehicle collision detected")

#             # Highlight smoke
#             for (x1, y1, x2, y2) in smoke:
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
#                 cv2.putText(frame, "🔥 Smoke/Fire", (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
#                 if self.notifier:
#                     self.notifier.send_alert("Smoke/Fire detected")

#             cv2.imshow("Smart Traffic Detection", frame)
#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()


# # detector.py
# import cv2
# from ultralytics import YOLO
# from imutils import resize
# import time
# import numpy as np

# class TrafficDetector:
#     def __init__(self, video_path=None, notifier=None):
#         self.video_path = video_path
#         self.notifier = notifier

#         # # YOLOv8 models
#         # self.vehicle_model = YOLO("yolov8n.pt")   # Detect vehicles & person
#         # self.smoke_model = YOLO("smoke.pt")        # Replace with smoke/fire YOLO model
#         # self.person_class = 0                       # COCO class for person
#         # self.vehicle_classes = [2, 3, 5, 7]        # car, motorcycle, bus, truck

#         # # For tracking collisions
#         # self.prev_vehicle_boxes = []

#     # IoU calculation for collision detection
#     @staticmethod
#     def iou(boxA, boxB):
#         xA = max(boxA[0], boxB[0])
#         yA = max(boxA[1], boxB[1])
#         xB = min(boxA[2], boxB[2])
#         yB = min(boxA[3], boxB[3])
#         interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
#         boxAArea = (boxA[2]-boxA[0]+1)*(boxA[3]-boxA[1]+1)
#         boxBArea = (boxB[2]-boxB[0]+1)*(boxB[3]-boxB[1]+1)
#         return interArea / float(boxAArea + boxBArea - interArea)

#     # Detect collisions between vehicles
#     def detect_collisions(self, boxes, iou_thresh=0.3):
#         collisions = []
#         for i, boxA in enumerate(boxes):
#             for j, boxB in enumerate(boxes):
#                 if i >= j: continue
#                 if self.iou(boxA, boxB) > iou_thresh:
#                     collisions.append((i, j))
#         return collisions

#     # Detect groups of people
#     @staticmethod
#     def detect_person_groups(person_boxes, distance_thresh=50):
#         groups = []
#         centroids = [(int((x1+x2)/2), int((y1+y2)/2)) for (x1,y1,x2,y2) in person_boxes]
#         for i, c1 in enumerate(centroids):
#             group = [i]
#             for j, c2 in enumerate(centroids):
#                 if i == j: continue
#                 dist = ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)**0.5
#                 if dist < distance_thresh:
#                     group.append(j)
#             if len(group) > 1:
#                 groups.append(group)
#         return groups

#     def run_detection(self):
#         cap = cv2.VideoCapture(self.video_path)
#         frame_no = 0

#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             frame_no += 1
#             frame = resize(frame, width=960)

#             # --- Vehicle & Person Detection ---
#             results = self.vehicle_model(frame, stream=True)
#             vehicle_boxes = []
#             person_boxes = []

#             for r in results:
#                 for box in r.boxes:
#                     cls_id = int(box.cls[0])
#                     conf = float(box.conf[0])
#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     label = r.names[cls_id]

#                     if cls_id == self.person_class:
#                         person_boxes.append((x1,y1,x2,y2))
#                         cv2.rectangle(frame, (x1,y1),(x2,y2),(255,0,0),2)
#                         cv2.putText(frame, f"{label} {conf:.2f}", (x1,y1-6),
#                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,255),1)
#                     elif cls_id in self.vehicle_classes:
#                         vehicle_boxes.append((x1,y1,x2,y2))
#                         cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),2)
#                         cv2.putText(frame, f"{label} {conf:.2f}", (x1,y1-6),
#                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)

#             # --- Collision Detection ---
#             collisions = self.detect_collisions(vehicle_boxes)
#             if collisions and self.notifier:
#                 event = {
#                     "type": "Vehicle Collision",
#                     "time": time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "details": collisions
#                 }
#                 self.notifier.send_alert(event)
#                 for i,j in collisions:
#                     cv2.putText(frame, "COLLISION!", (vehicle_boxes[i][0], vehicle_boxes[i][1]-20),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255),2)

#             # --- Smoke Detection ---
#             smoke_results = self.smoke_model(frame, stream=True)
#             smoke_detected = False
#             for r in smoke_results:
#                 for box in r.boxes:
#                     x1,y1,x2,y2 = map(int, box.xyxy[0])
#                     cv2.rectangle(frame, (x1,y1),(x2,y2),(0,0,255),2)
#                     cv2.putText(frame, "SMOKE", (x1,y1-6),
#                                 cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
#                     smoke_detected = True
#             if smoke_detected and self.notifier:
#                 event = {
#                     "type": "Smoke Detected",
#                     "time": time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "details": "Smoke detected in frame"
#                 }
#                 self.notifier.send_alert(event)

#             # --- Person Group Detection ---
#             groups = self.detect_person_groups(person_boxes)
#             if groups and self.notifier:
#                 event = {
#                     "type": "Person Group Detected",
#                     "time": time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "details": groups
#                 }
#                 self.notifier.send_alert(event)
#                 for group in groups:
#                     for idx in group:
#                         x1,y1,x2,y2 = person_boxes[idx]
#                         cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
#                         cv2.putText(frame,"GROUP",(x1,y1-6),
#                                     cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)

#             cv2.imshow("Smart Traffic Detector", frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()

# detector.py
# from ultralytics import YOLO

# # small model for CPU speed; change to yolov8s.pt or custom model for accuracy
# MODEL_NAME = "yolov8n.pt"
# model = YOLO(MODEL_NAME)

# VEHICLE_LABELS = {"car","truck","bus","motorbike","bicycle","motorcycle"}

# def detect(frame, conf=0.35):
#     """
#     Returns:
#       detections: list of (label, confidence, (x1,y1,x2,y2))
#       vehicle_count: int
#       any_person: bool
#     """
#     results = model(frame, conf=conf, verbose=False)
#     detections = []
#     vehicle_count = 0
#     any_person = False

#     for r in results:
#         for box in r.boxes:
#             cls_id = int(box.cls[0])
#             label = model.names[cls_id]
#             confv = float(box.conf[0])
#             xyxy = tuple(map(int, box.xyxy[0].tolist()))
#             detections.append((label, confv, xyxy))
#             if label in VEHICLE_LABELS:
#                 vehicle_count += 1
#             if label == "person":
#                 any_person = True

#     return detections, vehicle_count, any_person

# # # class TrafficDetector:
# # #     def __init__(self, video_path=None):
# # #         self.video_path = video_path

# # #     def run_detection(self):
# # #         # placeholder: later we add YOLO + OpenCV
# # #         print(f"Running detection on {self.video_path}...")
# # #         # simulate detection
# # #         events = [
# # #             {"type": "accident", "location": "Junction A", "time": "12:30 PM"}
# # #         ]
# # #         return events
