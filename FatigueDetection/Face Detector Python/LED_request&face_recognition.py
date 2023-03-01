import cv2
import numpy as np
from urllib.request import urlopen
import dlib 
from math import hypot
import time
import requests

import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())

detector = dlib.get_frontal_face_detector()   # get face detector
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")   # get face detector and extract the feature points
font = cv2.FONT_HERSHEY_PLAIN#set font style

# get the mid point between the upper and lower eyelid
def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

#  get the blinking ratio
def get_blinking_ratio(eye_points, facial_landmarks):
    #Use the points on the facial feature map to obtain the coordinates on both sides of the eyes on the face
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)

    # Use the points on the facial feature map to obtain the coordinates of the upper and lower eyelids of the human face, and calculate the coordinates of the middle point at the same time
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))
    
    # Connect the eyes left and right and up and down into a line for easy observation
    hor_line = cv2.line(frame, left_point, right_point, (0,255,0), 3)
    ver_line = cv2.line(frame, center_top, center_bottom, (0,255,255), 3)

    # Calculate the length of the line segment using the hypot function
    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    # get the ratio
    ratio = hor_line_lenght / ver_line_lenght
    return ratio

# change to your ESP32-CAM ip
url = "http://192.168.168.159:81/stream"
stream = urlopen(url)

bytes = bytes()
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')   # start
    b = bytes.find(b'\xff\xd9')   # end
    if a != -1 and b != -1 and b>a:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        bf = np.frombuffer(jpg, dtype=np.uint8)
        img = cv2.imdecode(bf, cv2.IMREAD_COLOR)
        frame = cv2.resize(img, (1280, 960))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # convert the video to gray and save it for easy judgment of facial feature points
        faces = detector(gray)   # use the dlib library to process the acquired face images

        # loop each frame
        for face in faces:
            landmarks = predictor(gray, face)
            # get left eye and right ratio
            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)

            # get mean ratio
            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            end = time.time()   # timing, judging the end time

            # Detect eye conditions
            if blinking_ratio > 4.5:
                cv2.putText(frame, "CLOSE", (75, 250), font, 7, (255, 0, 255), 3)   # put text on screen
            else:
                cv2.putText(frame, "OPEN", (75, 250), font, 7, (0, 255, 0), 3)
                start = time.time()   # timing 
            print("Close eyes time:%.2fsecond" % (end - start))   # get eye opening and closing time difference

            # determine if people is tired
            if (end - start) > 2:
                cv2.putText(frame, "TIRED", (200, 325), font, 7, (0, 0, 255), 3)
                duration = 1000
                freq = 1000
                x = requests.get('http://192.168.168.159:8001/25/on')
            else:
                x = requests.get('http://192.168.168.159:8001/25/off')

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 27:
            exit(0)
    if b<a :
        bytes=bytes[a:]
