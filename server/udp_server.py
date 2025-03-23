import sys
import numpy as np
import cv2
from PyQt5.QtNetwork import QUdpSocket, QHostAddress
from PyQt5.QtCore import QByteArray
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap

class UdpVideoServer(QWidget):
    def __init__(self, port=12345):
        super().__init__()
        self.udp_socket = QUdpSocket()
        self.udp_socket.bind(QHostAddress.Any, port)
        self.udp_socket.readyRead.connect(self.receive_data)

        print(f"[UDP Server] Listening for video on port {port}...")

        # UI 설정
        self.setWindowTitle("UDP Video Server")
        self.setGeometry(200, 200, 640, 480)
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def receive_data(self):
        while self.udp_socket.hasPendingDatagrams():
            data, sender, sender_port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())

            # 받은 데이터를 프레임으로 변환
            self.process_video_frame(data)

    def process_video_frame(self, frame_bytes):
        """ 수신한 비디오 프레임을 디코딩 후 화면에 표시 """
        try:
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

            if frame is not None:
                self.display_frame(frame)
            else:
                print("[UDP Server] Failed to decode frame")

        except Exception as e:
            print(f"[UDP Server] Error processing frame: {e}")

    def display_frame(self, frame):
        """ OpenCV 프레임을 QLabel에 표시 """
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(q_img))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = UdpVideoServer(port=12345)
    server.show()
    sys.exit(app.exec_())
