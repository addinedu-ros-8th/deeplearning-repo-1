import cv2
import threading

class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.frame = None
        self.stopped = False
        self.thread = threading.Thread(target=self._update)
        self.thread.daemon = True
        self.counter = 0 
        self.is_active = False

    def start(self):
        self.is_active = True  # 카메라 시작 시 활성화 상태로 설정
        self.thread.start()

    def _update(self):
        while not self.stopped:
            ret, frame = self.capture.read()
            if ret:
                #frame = cv2.flip(frame, 1)
                self.frame = frame

    def stop(self):
        self.is_active = False
        self.stopped = True
        self.thread.join()
        self.capture.release()