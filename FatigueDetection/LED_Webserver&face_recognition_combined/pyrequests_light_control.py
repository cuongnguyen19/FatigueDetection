import cv2
import numpy as np
from urllib.request import urlopen
import dlib #调用识别检测库
from math import hypot
import time
import requests

import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())

detector = dlib.get_frontal_face_detector()#获取人脸分类器
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")#获取人脸检测器，提取特征点数
font = cv2.FONT_HERSHEY_PLAIN#设置写入文字的字体（在屏幕上的字体）

#用于求上眼皮与下眼皮的重点
def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

#用于计算眼睛长宽比，获取比值
def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    #利用脸谱特征图上的点，获得人脸上眼睛两边的坐标

    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))
    #利用脸谱特征图上的点，获得人脸上眼睛上下眼皮的坐标，同时计算中间点的坐标

    hor_line = cv2.line(frame, left_point, right_point, (0,255,0), 3)
    ver_line = cv2.line(frame, center_top, center_bottom, (0,255,255), 3)
    #将眼睛左右与上下连成线，方便观测

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
    #利用hypot函数计算得出线段的长度

    ratio = hor_line_lenght / ver_line_lenght
    #得到长宽比
    return ratio

# change to your ESP32-CAM ip
url = "http://192.168.31.194:81/stream"
stream = urlopen(url)

bytes = bytes()
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')#起始标志
    b = bytes.find(b'\xff\xd9')#结束标志
    if a != -1 and b != -1 and b>a:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        bf = np.frombuffer(jpg, dtype=np.uint8)
        img = cv2.imdecode(bf, cv2.IMREAD_COLOR)#这个i就可以拿去识别了
        frame = cv2.resize(img, (1280, 960))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 方法，作用：将摄像头捕获的视频转换为灰色并且保存，这样方便判断面部特征点
        faces = detector(gray)  # 利用dlib库，处理获取的人脸画面

        # 循环每一个画面
        for face in faces:
            landmarks = predictor(gray, face)
            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
            # 利用函数获得左右眼的比值

            blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2
            # 取平均数

            end = time.time()  # 记时，判断闭眼时间

            # 检测眼睛状况
            if blinking_ratio > 4.5:
                cv2.putText(frame, "CLOSE", (75, 250), font, 7, (255, 0, 255), 3)  # 方法，作用：在图像上打印文字，设置字体，颜色，大小
            else:
                cv2.putText(frame, "OPEN", (75, 250), font, 7, (0, 255, 0), 3)
                start = time.time()  # 记时
            print("闭眼时间:%.2f秒" % (end - start))  # 获取睁闭眼时间差

            # 判断是否疲劳
            if (end - start) > 2:
                cv2.putText(frame, "TIRED", (200, 325), font, 7, (0, 0, 255), 3)
                duration = 1000
                freq = 1000
                x = requests.get('http://192.168.31.194:8001/25/on')
                x = requests.get('http://192.168.89.198:8001/26/on')

            else:
                x = requests.get('http://192.168.31.194:8001/25/off')
                x = requests.get('http://192.168.89.198:8001/26/on')

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 27:
            exit(0)
    if b<a :
        bytes=bytes[a:]