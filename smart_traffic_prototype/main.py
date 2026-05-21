import cv2
import time
import os
import csv
from detector import TrafficDetector
from notifier import Notifier

VIDEO_SOURCE = "traffic_video.mp4"
LOG_CSV = "logs/events.csv"
ALERT_COOLDOWN = 20  # seconds — no repeated alert within this time

# Create required folders
os.makedirs("logs", exist_ok=True)

# Create CSV log file if not present
if not os.path.exists(LOG_CSV):
    with open(LOG_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "event", "vehicle_count", "details", "snapshot"])

# Initialize notifier & detector
notifier = Notifier()
detector = TrafficDetector(VIDEO_SOURCE, notifier, ALERT_COOLDOWN)

# Run detection
detector.run_detection()

print("Program finished.")



# import cv2, time, os, csv
# from detector import TrafficDetector
# from notifier import Notifier

# VIDEO_SOURCE = "traffic_video.mp4"
# LOG_CSV = "logs/events.csv"
# ALERT_COOLDOWN = 20   # seconds — no duplicate alert within this time

# os.makedirs("logs", exist_ok=True)

# if not os.path.exists(LOG_CSV):
#     with open(LOG_CSV, "w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["timestamp", "event", "vehicle_count", "details", "snapshot"])

# notifier = Notifier()

# # ✅ Create detector instance
# detector = TrafficDetector(VIDEO_SOURCE, notifier)

# # ✅ Run detection
# detector.run_detection()



# import cv2, time, os, csv
# from detector import detect
# from notifier import Notifier
# from imutils import resize

# VIDEO_SOURCE = "traffic_video.mp4"
# TRAFFIC_THRESHOLD = 20
# FRAME_SKIP = 2
# ACCIDENT_HEURISTIC = True
# LOG_CSV = "logs/events.csv"
# ALERT_COOLDOWN = 20   # seconds — no duplicate alert within this time

# os.makedirs("logs", exist_ok=True)

# if not os.path.exists(LOG_CSV):
#     with open(LOG_CSV, "w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["timestamp", "event", "vehicle_count", "details", "snapshot"])

# notifier = Notifier()
# cap = cv2.VideoCapture(VIDEO_SOURCE)
# frame_no = 0

# # ✅ Track last alert time
# last_alert_time = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame_no += 1
#     if FRAME_SKIP > 1 and frame_no % FRAME_SKIP != 0:
#         continue

#     frame = resize(frame, width=960)
#     detections, vehicle_count, any_person = detect(frame, conf=0.35)

#     for label, conf, (x1, y1, x2, y2) in detections:
#         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 6),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#     status = "Free Flow" if vehicle_count <= TRAFFIC_THRESHOLD else "Congested"
#     cv2.putText(frame, f"Traffic: {vehicle_count} ({status})", (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

#     # ✅ Accident detection with cooldown
#     current_time = time.time()
#     if ACCIDENT_HEURISTIC and any_person and vehicle_count > 3:
#         if current_time - last_alert_time >= ALERT_COOLDOWN:  # wait 20 sec before next alert
#             last_alert_time = current_time  # update last alert time

#             ts = int(current_time)
#             snapshot = f"logs/incident_{ts}.jpg"
#             cv2.imwrite(snapshot, frame)

#             event = {
#                 "type": "Accident Suspected",
#                 "location": "Traffic Camera 1",
#                 "time": time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "vehicle_count": vehicle_count,
#                 "snapshot": snapshot
#             }

#             notifier.send_alert(event)

#             with open(LOG_CSV, "a", newline="") as f:
#                 writer = csv.writer(f)
#                 writer.writerow([event["time"], event["type"],
#                                  vehicle_count, "person+vehicles", snapshot])

#             cv2.putText(frame, "⚠ Accident/Abnormal Detected", (10, 70),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
#         else:
#             # Optional: show cooldown message on screen
#             cv2.putText(frame, "Alert sent recently — waiting...", (10, 70),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

#     cv2.imshow("Smart Traffic Management", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()







# # main.py
# import cv2, time, os, csv
# from detector import detect
# from notifier import Notifier   # ✅ use the Notifier class
# from imutils import resize

# VIDEO_SOURCE = "traffic_video.mp4"  # or 0 for webcam
# TRAFFIC_THRESHOLD = 20
# FRAME_SKIP = 2
# ACCIDENT_HEURISTIC = True
# LOG_CSV = "logs/events.csv"

# os.makedirs("logs", exist_ok=True)

# # create csv if missing
# if not os.path.exists(LOG_CSV):
#     with open(LOG_CSV, "w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["timestamp", "event", "vehicle_count", "details", "snapshot"])

# # ✅ create notifier instance
# notifier = Notifier()

# cap = cv2.VideoCapture(VIDEO_SOURCE)
# frame_no = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame_no += 1
#     if FRAME_SKIP > 1 and frame_no % FRAME_SKIP != 0:
#         continue

#     frame = resize(frame, width=960)
#     detections, vehicle_count, any_person = detect(frame, conf=0.35)

#     # draw boxes
#     for label, conf, (x1, y1, x2, y2) in detections:
#         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 6),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#     status = "Free Flow" if vehicle_count <= TRAFFIC_THRESHOLD else "Congested"
#     cv2.putText(frame, f"Traffic: {vehicle_count} ({status})", (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

#     # ✅ Accident detection logic
#     if ACCIDENT_HEURISTIC and any_person and vehicle_count > 3:
#         ts = int(time.time())
#         snapshot = f"logs/incident_{ts}.jpg"
#         cv2.imwrite(snapshot, frame)

#         event = {
#             "type": "Accident Suspected",
#             "location": "Traffic Camera 1",
#             "time": time.strftime("%Y-%m-%d %H:%M:%S"),
#             "vehicle_count": vehicle_count,
#             "snapshot": snapshot
#         }

#         # ✅ Send SMS + Email
#         notifier.send_alert(event)

#         # ✅ Log into CSV
#         with open(LOG_CSV, "a", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow([event["time"], event["type"],
#                              vehicle_count, "person+vehicles", snapshot])

#         cv2.putText(frame, "⚠ Accident/Abnormal Detected", (10, 70),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)

#     cv2.imshow("Smart Traffic Management", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()









# # # main.py
# # import cv2, time, os, csv
# # # from detector import detect
# # # from notifier import Notifier   # ✅ use the Notifier class
# # from imutils import resize
# # # main.py
# # from detector import TrafficDetector
# # from notifier import Notifier

# # # Initialize notifier
# # notifier = Notifier()

# # # Initialize detector with video and notifier
# # detector = TrafficDetector(video_path="traffic_video.mp4", notifier=notifier)

# # # Run detection (this opens a window and shows alerts)
# # detector.run_detection()


# # VIDEO_SOURCE = "traffic_video.mp4"  # or 0 for webcam
# # TRAFFIC_THRESHOLD = 10
# # FRAME_SKIP = 2
# # ACCIDENT_HEURISTIC = True
# # LOG_CSV = "logs/events.csv"

# # os.makedirs("logs", exist_ok=True)

# # # create csv if missing
# # if not os.path.exists(LOG_CSV):
# #     with open(LOG_CSV, "w", newline="") as f:
# #         writer = csv.writer(f)
# #         writer.writerow(["timestamp", "event", "vehicle_count", "details", "snapshot"])

# # # ✅ create notifier instance
# # notifier = Notifier()

# # cap = cv2.VideoCapture(VIDEO_SOURCE)
# # frame_no = 0

# # while cap.isOpened():
# #     ret, frame = cap.read()
# #     if not ret:
# #         break
# #     frame_no += 1
# #     if FRAME_SKIP > 1 and frame_no % FRAME_SKIP != 0:
# #         continue

# #     frame = resize(frame, width=960)
# #     detections, vehicle_count, any_person = detect(frame, conf=0.35)

# #     # draw boxes
# #     for label, conf, (x1, y1, x2, y2) in detections:
# #         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
# #         cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 6),
# #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

# #     status = "Free Flow" if vehicle_count <= TRAFFIC_THRESHOLD else "Congested"
# #     cv2.putText(frame, f"Traffic: {vehicle_count} ({status})", (10, 30),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

# #     # ✅ Accident detection logic
# #     if ACCIDENT_HEURISTIC and any_person and vehicle_count > 4:
# #         ts = int(time.time())
# #         snapshot = f"logs/incident_{ts}.jpg"
# #         cv2.imwrite(snapshot, frame)

# #         event = {
# #             "type": "Accident Suspected",
# #             "location": "Traffic Camera 1",
# #             "time": time.strftime("%Y-%m-%d %H:%M:%S"),
# #             "vehicle_count": vehicle_count,
# #             "snapshot": snapshot
# #         }

# #         # ✅ Send SMS + Email
# #         notifier.send_alert(event)

# #         # ✅ Log into CSV
# #         with open(LOG_CSV, "a", newline="") as f:
# #             writer = csv.writer(f)
# #             writer.writerow([event["time"], event["type"],
# #                              vehicle_count, "person+vehicles", snapshot])

# #         cv2.putText(frame, "⚠ Accident/Abnormal Detected", (10, 70),
# #                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)

# #     cv2.imshow("Smart Traffic Management", frame)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()

# # main.py
# import cv2, time, os, csv
# from detector import detect
# from notifier import send_sms
# from imutils import resize

# VIDEO_SOURCE = "traffic_video.mp4"  # or 0 for webcam
# TRAFFIC_THRESHOLD = 20
# FRAME_SKIP = 2
# ACCIDENT_HEURISTIC = True
# LOG_CSV = "logs/events.csv"
# os.makedirs("logs", exist_ok=True)

# # create csv if missing
# if not os.path.exists(LOG_CSV):
#     with open(LOG_CSV, "w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["timestamp","event","vehicle_count","details","snapshot"])

# cap = cv2.VideoCapture(VIDEO_SOURCE)
# frame_no = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     frame_no += 1
#     if FRAME_SKIP > 1 and frame_no % FRAME_SKIP != 0:
#         continue

#     frame = resize(frame, width=960)
#     detections, vehicle_count, any_person = detect(frame, conf=0.35)

#     # draw boxes
#     for label, conf, (x1,y1,x2,y2) in detections:
#         cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),2)
#         cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1-6),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 1)

#     status = "Free Flow" if vehicle_count <= TRAFFIC_THRESHOLD else "Congested"
#     cv2.putText(frame, f"Traffic: {vehicle_count} ({status})", (10,30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

#     if ACCIDENT_HEURISTIC and any_person and vehicle_count > 5:
#         ts = int(time.time())
#         snapshot = f"logs/incident_{ts}.jpg"
#         cv2.imwrite(snapshot, frame)
#         message = f"Emergency: possible accident detected. Vehicles: {vehicle_count}. Snapshot: {snapshot}"
#         send_sms(message)
#         with open(LOG_CSV, "a", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), "accident_suspected",
#                              vehicle_count, "person+vehicles", snapshot])
#         cv2.putText(frame, "⚠ Accident/Abnormal Detected", (10,70),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 3)

#     cv2.imshow("Smart Traffic Management", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
    

# # cap.release()
# # cv2.destroyAllWindows()

# # from detector import TrafficDetector
# # from notifier import Notifier

# # def main():
# #     print("🚦 Smart Traffic Prototype Started")

# #     # init detector
# #     detector = TrafficDetector(video_path="traffic_video.mp4")

# #     # init notifier
# #     notifier = Notifier()

# #     # run detection
# #     events = detector.run_detection()

# #     # if abnormal event detected, notify
# #     for event in events:
# #         notifier.send_alert(event)

# # if __name__ == "__main__":
# #     main()
