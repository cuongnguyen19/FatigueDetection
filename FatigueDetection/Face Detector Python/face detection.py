import cv2
import numpy as np
from urllib.request import urlopen
import dlib 
from math import hypot
import time

import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
font = cv2.FONT_HERSHEY_PLAIN

def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)

    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))
  
    hor_line = cv2.line(frame, left_point, right_point, (0,255,0), 3)
    ver_line = cv2.line(frame, center_top, center_bottom, (0,255,255), 3)

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
 
    return ratio

# change to your ESP32-CAM ip
url = "http://192.168.43.163:81/stream"
stream = urlopen(url)

bytes = bytes()
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1 and b>a:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        bf = np.frombuffer(jpg, dtype=np.uint8)
        img = cv2.imdecode(bf, cv2.IMREAD_COLOR)
        frame = cv2.resize(img, (1280, 960))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray) 

        for face in faces:
            landmarks = predictor(gray, face)
            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)

            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            end = time.time()

            if blinking_ratio > 4.5:
                cv2.putText(frame, "CLOSE", (75, 250), font, 7, (255, 0, 255), 3)  # 方法，作用：在图像上打印文字，设置字体，颜色，大小
            else:
                cv2.putText(frame, "OPEN", (75, 250), font, 7, (0, 255, 0), 3)
                start = time.time()
            print("闭眼时间:%.2f秒" % (end - start))

            if (end - start) > 2:
                cv2.putText(frame, "TIRED", (200, 325), font, 7, (0, 0, 255), 3)
                duration = 1000
                freq = 1000

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 27:
            exit(0)
    if b<a :
        bytes=bytes[a:]