### Project Application Guidance

- Open a Wifi
- Config and run `LED_Webserver&face_recognition_combined` project
  -  Modify the `ssid` and `password` to your Wifi name and password in `LED_Webserver&face_recognition_combined/src/CameraWebServer_example.cpp`
  -  Build, upload and monitor series output, and copy the IP address
  -  Open the IP address in the browser, open stream to see the video stream
- Config and run `Face Detector Python` project
  - Config a Python OpenCV environment
  - Modify the `url` to `"http://your ip address:81/stream"` in `Face Detector Python/LED_request&face_recognition.py`
  - run this project
