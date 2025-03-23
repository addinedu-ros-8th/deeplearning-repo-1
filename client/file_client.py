from PyQt5.QtNetwork import QTcpSocket, QHostAddress
from PyQt5.QtCore import QCoreApplication, QFile, QIODevice
import sys

class FileClient:
    def __init__(self, server_ip="127.0.0.1", server_port=12346, file_path="sample.txt"):
        self.socket = QTcpSocket()
        self.socket.connected.connect(self.send_file)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.errorOccurred.connect(self.on_error)

        self.server_ip = QHostAddress(server_ip)
        self.server_port = server_port
        self.file_path = file_path

        print("[FileClient] Connecting to server...")
        self.socket.connectToHost(self.server_ip, self.server_port)

    def send_file(self):
        """서버에 연결되면 파일 전송"""
        print("[FileClient] Connected to server, sending file...")

        file = QFile(self.file_path)
        if not file.open(QIODevice.ReadOnly):
            print("[FileClient] Failed to open file for reading.")
            return

        data = file.readAll()
        self.socket.write(data)
        self.socket.flush()
        file.close()

        print(f"[FileClient] Sent {len(data)} bytes.")
        self.socket.disconnectFromHost()  # 전송 후 연결 종료

    def on_disconnected(self):
        """파일 전송 후 연결이 끊어지면 종료"""
        print("[FileClient] Disconnected from server.")

    def on_error(self, error):
        print(f"[FileClient] Error: {error}")

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    client = FileClient(file_path="/home/sang/dev_ws/mediapipe/data/donguk.MOV")
    sys.exit(app.exec_())
