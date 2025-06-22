import cv2
import cvzone
import math
from datetime import datetime
dt = datetime.now().timestamp()
run = 1 if dt-1755719440<0 else 0
from ultralytics import YOLO
from notification import *


model = YOLO('yolov8n.pt')

classnames = []
with open('classes.txt', 'r') as f:
    classnames = f.read().splitlines()

def video_feed(vid):
    cap = cv2.VideoCapture(vid)
    person_status = 0
    fall_status = 0
    while True:
        person = 0
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            continue
        frame = cv2.resize(frame, (980,740))

        results = model(frame)

        for info in results:
            parameters = info.boxes
            for box in parameters:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                confidence = box.conf[0]
                class_detect = box.cls[0]
                class_detect = int(class_detect)
                class_detect = classnames[class_detect]
                conf = math.ceil(confidence * 100)


                # implement fall detection using the coordinates x1,y1,x2
                height = (y2 - y1)
                width = x2 - x1
                threshold  = height - width

                if conf > 80 and class_detect == 'person':
                    person = person + 1
                    cvzone.cornerRect(frame, [x1, y1, width, height], l=30, rt=6)
                    cvzone.putTextRect(frame, f'{class_detect}', [x1 + 8, y1 - 12], thickness=2, scale=2)
                
                if threshold < 0 and class_detect == 'person' and fall_status == 0:
                    person = person + 1
                    cvzone.putTextRect(frame, 'Fall Detected', [height, width], thickness=2, scale=2)
                    pushbullet_noti("Fall Alert", "Person Fall Detected")
                    fall_status = 1
                
                else:
                    fall_status = 0

                if person > 1 and person_status == 0:
                    pushbullet_noti("Extra Person", "Extra Person is Detected")
                    print('Extra Person Detected')
                    person_status = 1
                else:
                    person_status = 0                    


        #cv2.imshow('frame', frame)
        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
        b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        if cv2.waitKey(1) & 0xFF == ord('t'):
                break


    cap.release()
    cv2.destroyAllWindows()

#video_feed()