from PyQt5.QtNetwork import QTcpSocket, QHostAddress
from PyQt5.QtCore import QCoreApplication
import sys
import signal
import struct
import os

class FileClient:
    def __init__(self, server_ip="127.0.0.1", server_port=8888, file_path=None):
        self.socket = QTcpSocket()
        self.server_ip = QHostAddress(server_ip)
        self.server_port = server_port
        self.file_path = file_path

        print(f"[FileClient] Connecting to server {server_ip}:{server_port}...")
        self.socket.connectToHost(self.server_ip, self.server_port)

        if not self.socket.waitForConnected(5000):  # 서버 연결 대기 (최대 5초)
            print(f"[FileClient] Error: Unable to connect to server ({self.socket.errorString()})")
            return

        self.send_video()

    def send_video(self):
        """파일 크기를 먼저 보내고, 그 후 파일을 전송"""
        if not self.file_path or not os.path.exists(self.file_path):
            print("[FileClient] File not found.")
            return

        file_size = os.path.getsize(self.file_path)

        try:
            with open(self.file_path, "rb") as f:
                print(f"[FileClient] Sending file: {self.file_path} ({file_size} bytes)")

                # 1. 파일 크기 먼저 전송 (8바이트)
                self.socket.write(struct.pack("!Q", file_size))

                # 2. 파일 데이터 전송
                while chunk := f.read(4096):
                    self.socket.write(chunk)

                self.socket.flush()

                # 3. 모든 데이터가 송신될 때까지 대기
                if not self.socket.waitForBytesWritten(5000):
                    print("[FileClient] Warning: Timeout waiting for bytes to be written.")

                print("[FileClient] File sent successfully!")

        except Exception as e:
            print(f"[FileClient] Error sending file: {e}")

        # 4. 서버가 수신을 완료할 때까지 연결 유지
        self.socket.waitForDisconnected(5000)
        self.socket.disconnectFromHost()

    def on_disconnected(self):
        print("[FileClient] Disconnected from server.")

    def on_error(self, error):
        print(f"[FileClient] Error: {error}")

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    file_path = "/home/sang/dev_ws/save_file/recorded_20250402_121312.mp4"  # 전송할 파일 경로
    client = FileClient(file_path=file_path)

    sys.exit(app.exec_())