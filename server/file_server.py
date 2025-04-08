from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import QFile, QIODevice, QTimer, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
import sys
import signal
import struct
import socket
import cv2
from datetime import datetime
import os

class VideoPlayerWindow(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Latest Video (PyQt)")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(video_path)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(30)  # 약 30 FPS

        self.show()

    def display_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.cap.release()
            self.close()
            return

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(q_image))


class FileServer:
    def __init__(self, port=8888):
        self.server = QTcpServer()
        self.server.listen(QHostAddress.Any, port)
        self.server.newConnection.connect(self.on_new_connection)
        print(f"[FileServer] Listening on port {port}...")
        self.name = None
        self.video_window = None

    def on_new_connection(self):
        """클라이언트가 연결되면 실행"""
        self.client_socket = self.server.nextPendingConnection()
        self.client_socket.readyRead.connect(self.receive_command)
        self.client_socket.disconnected.connect(self.on_disconnected)

        print("[FileServer] Client connected.")

        self.buffer = b''
        self.command = None
        self.name = None
        self.file = None
        self.file_size = None
        self.received_size = 0

    def receive_command(self):
        if self.client_socket.bytesAvailable() < 12:  # 최소 3개 문자열 길이값(4x3=12) 필요
            return

        # 먼저 전체 바이너리 데이터 다 읽기
        self.buffer += self.client_socket.readAll().data()

        try:
            # 데이터 언팩
            unpacked = self.unpack_data(self.buffer)

            self.command = unpacked.get("command")
            self.name = unpacked.get("name")
            self.data = unpacked.get("data")

            print(f"[FileServer] Received command: {self.command}")
            print(f"[FileServer] Received name: {self.name}")
            print(f"[FileServer] Received data: {self.data}")

            if self.command == "upload":
                self.client_socket.readyRead.disconnect()
                self.client_socket.readyRead.connect(self.receive_video)
            elif self.command == "br":
                print('[FileServer] Received br request.')
                self.process_latest_video_request()
                self.client_socket.disconnectFromHost()

            # 언팩 끝났으면 buffer 초기화
            self.buffer = b''

        except Exception as e:
            print(f"[FileServer] Error unpacking data: {e}")

    def process_latest_video_request(self):
        """사용자 이름 폴더에서 최신 mp4 파일을 찾아 클라이언트로 전송하고 서버에서 재생"""
        if not self.name:
            print("[FileServer] No user name received.")
            return

        folder_path = os.path.join(".", self.name)
        if not os.path.exists(folder_path):
            print(f"[FileServer] Folder '{self.name}' does not exist.")
            return

        # 폴더 내 mp4 파일 목록 가져오기
        mp4_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]
        if not mp4_files:
            print(f"[FileServer] No mp4 files found in '{self.name}' folder.")
            return

        # 최신 파일 선택 (파일명 기반 정렬)
        mp4_files.sort(reverse=True)
        latest_file = mp4_files[0]
        full_path = os.path.join(folder_path, latest_file)
        file_size = os.path.getsize(full_path)

        print(f"[FileServer] Sending latest file: {latest_file} ({file_size} bytes)")

        # PyQt로 영상 재생
        print("[FileServer] Playing video in PyQt window...")
        self.video_window = VideoPlayerWindow(full_path)

    def on_disconnected(self):
        """클라이언트가 연결을 끊으면 파일을 저장하고 종료"""
        if self.file and self.file.isOpen():
            self.file.close()
        self.client_socket.deleteLater()
        print("[FileServer] Client disconnected.")

    def unpack_data(self, binary_data):
        offset = 0

        def unpack_string():
            nonlocal offset
            length = struct.unpack_from('I', binary_data, offset)[0]
            offset += 4
            if length > 0:
                value = binary_data[offset:offset + length].decode('utf-8')
                offset += length
                return value
            return None

        command = unpack_string()
        name = unpack_string()
        data = unpack_string()

        return {
            "command": command,
            "name": name,
            "data": data
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)  # 꼭 QApplication 사용
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러
    server = FileServer(port=8888)
    sys.exit(app.exec_())
