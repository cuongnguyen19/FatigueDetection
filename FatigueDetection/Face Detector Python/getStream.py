import cv2
import numpy as np
from urllib.request import urlopen

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
        img = cv2.resize(img, (1280, 960))
        cv2.imshow('i', img)
        if cv2.waitKey(1) == 27:
            exit(0)
    if b<a :
        bytes=bytes[a:]