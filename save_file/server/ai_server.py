import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
import numpy as np
import cv2
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QTcpSocket
from PyQt5.QtCore import QByteArray
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
import struct
import threading
import time
from file_client import FileClient
from ai_to_main import AitoMain
from exercise_model import ExerciseClassifier
from counting import ExerciseCounter

class AiServer(QWidget):
    def __init__(self, port=12345, record_duration=5):
        super().__init__()
        self.udp_socket = QUdpSocket()
        self.udp_socket.bind(QHostAddress.Any, port)
        self.udp_socket.readyRead.connect(self.receive_data)

        self.tcp = AitoMain()
        self.model = ExerciseClassifier()
        #self.file_server = FileClient()
        self.recording = False
        self.video_writer = None
        self.record_duration = record_duration  # 녹화 간격 (초)
        self.start_time = None
        self.video_filename = None

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
        """ 수신한 비디오 프레임을 디코딩 후 화면에 표시 및 녹화 """
        try:
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

            if frame is None:
                print("[UDP Server] Failed to decode frame")
                return
            # if self.start == True:
            frame = self.model.process_frame(frame)
            self.display_frame(frame)
            self.record_video(frame)

        except Exception as e:
            print(f"[UDP Server] Error processing frame: {e}")

    def record_video(self, frame):
        """ 프레임을 저장하여 녹화 파일 생성 """
        if not self.recording:
            self.start_new_recording(frame)

        self.video_writer.write(frame)

        if time.time() - self.start_time >= self.record_duration:
            self.stop_and_send_recording()

    def start_new_recording(self, frame):
        """ 새로운 비디오 파일 생성하여 녹화 시작 """
        self.recording = True
        self.start_time = time.time()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.video_filename = f"recorded_{timestamp}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        height, width, _ = frame.shape
        self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (width, height))

        print(f"[UDP Server] Started new recording: {self.video_filename}")

    def stop_and_send_recording(self):
        """ 녹화 종료 후 서버로 전송 """
        if self.recording:
            self.recording = False
            self.video_writer.release()
            self.video_writer = None

            print(f"[UDP Server] Stopped recording. Sending {self.video_filename} to server...")

            # 녹화된 파일을 서버로 전송
            self.send_video_to_server(self.video_filename)

    def send_video_to_server(self, video_path):
        """ 녹화된 비디오 파일을 서버로 전송 후 삭제 """
        try:
            if not os.path.exists(video_path):
                print(f"[UDP Server] Error: File {video_path} not found.")
                return

            print(f"[UDP Server] Initializing FileClient to send {video_path}...")

            # 파일 전송을 별도 스레드에서 실행하여 비동기 처리
            threading.Thread(target=self._send_video, args=(video_path,)).start()

        except Exception as e:
            print(f"[UDP Server] Error sending video to server: {e}")

    def _send_video(self, video_path):
        """파일 전송 실행 및 삭제"""
        try:
            file_client = FileClient(file_path=video_path)
            file_client.send_video()

            print(f"[UDP Server] Successfully sent {video_path} to server.")
            os.remove(video_path)  # 전송 완료 후 파일 삭제

        except Exception as e:
            print(f"[UDP Server] Error during file transmission: {e}")

    def display_frame(self, frame):
        """ OpenCV 프레임을 QLabel에 표시 """
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        q_img = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(q_img))
        self.label.repaint()  # 화면 갱신

if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = AiServer(port=12345)
    server.show()
    sys.exit(app.exec_())
