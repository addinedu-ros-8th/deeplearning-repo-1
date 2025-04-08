from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import time
from PyQt5.QtGui import QImage, QPixmap

class Video(QThread):
    frame_ready = pyqtSignal(QImage)  # QPixmap으로 변경
    finished = pyqtSignal()

    def __init__(self, video_path, label_size):
        super().__init__()
        self.video_path = video_path
        self._is_stopped = False
        self.label_size = label_size  # QLabel 크기 저장

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Failed to open video: {self.video_path}")
            self.finished.emit()
            return

        while cap.isOpened():
            if self._is_stopped: 
                break
            ret, frame = cap.read()
            if not ret: 
                break
            
            # QLabel 크기에 맞게 리사이징
            frame_resized = cv2.resize(frame, (self.label_size.width(), self.label_size.height()))

            # OpenCV BGR -> PyQt RGB 변환
            rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.frame_ready.emit(qt_img)
            time.sleep(1 / 30)

        cap.release()
        self.finished.emit()

    def stop(self):
        self._is_stopped = True
