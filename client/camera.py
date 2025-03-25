import cv2
import threading

class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.frame = None
        self.stopped = False
        self.thread = threading.Thread(target=self._update)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def _update(self):
        while not self.stopped:
            ret, frame = self.capture.read()
            if ret:
                self.frame = frame

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.capture.release()