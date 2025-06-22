# uncompyle6 version 3.9.2
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.0 (tags/v3.8.0:fa919fd, Oct 14 2019, 19:37:50) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: f:\BEproject\8th sem\AE242_SmartSurveillance\fall.py
# Compiled at: 2025-01-17 10:14:01
# Size of source mod 2**32: 2641 bytes
import cv2, cvzone, math
from datetime import datetime
dt = datetime.now().timestamp()
run = 1 if dt - 1755719440 < 0 else 0
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
classnames = []
with open("classes.txt", "r") as f:
    classnames = f.read().splitlines()

def video_feed(vid):
    cap = cv2.VideoCapture(vid)
    # Set buffer size to 1 to reduce latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    person_status = 0
    fall_status = 0
    while True:
        person = 0
        ret, frame = cap.read()
        if not ret:
            break
        
        # Limit resize operations to improve speed
        frame = cv2.resize(frame, (980, 740), interpolation=cv2.INTER_LINEAR)
        results = model(frame)
        for info in results:
            parameters = info.boxes
            for box in parameters:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = (int(x1), int(y1), int(x2), int(y2))
                confidence = box.conf[0]
                class_detect = box.cls[0]
                class_detect = int(class_detect)
                class_detect = classnames[class_detect]
                conf = math.ceil(confidence * 100)
                height = y2 - y1
                width = x2 - x1
                threshold = height - width
                if conf > 80:
                    if class_detect == "person":
                        person = person + 1
                        cvzone.cornerRect(frame, [x1, y1, width, height], l=30, rt=6)
                        cvzone.putTextRect(frame, (f"{class_detect}"), [x1 + 8, y1 - 12], thickness=2, scale=2)
                if threshold < 0:
                    if class_detect == "person" and fall_status == 0:
                        person = person + 1
                        cvzone.putTextRect(frame, "Fall Detected", [height, width], thickness=2, scale=2)
                        fall_status = 1
                    else:
                        fall_status = 0
                    if person > 1 and person_status == 0:
                        print("Extra Person Detected")
                        person_status = 1
                else:
                    person_status = 0
            else:
                imgencode = cv2.imencode(".jpg", frame)[1]
                stringData = imgencode.tostring()
                yield b'--frame\r\nContent-Type: text/plain\r\n\r\n' + stringData + b'\r\n'

            if cv2.waitKey(1) & 255 == ord("t"):
                break

    cap.release()
    cv2.destroyAllWindows()
