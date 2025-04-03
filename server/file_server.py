from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import QCoreApplication, QFile, QIODevice
import sys
import signal
import struct

class FileServer:
    def __init__(self, port=8888):
        self.server = QTcpServer()
        self.server.listen(QHostAddress.Any, port)
        self.server.newConnection.connect(self.on_new_connection)
        print(f"[FileServer] Listening on port {port}...")

    def on_new_connection(self):
        """클라이언트가 연결되면 실행"""
        self.client_socket = self.server.nextPendingConnection()
        self.client_socket.readyRead.connect(self.receive_video)
        self.client_socket.disconnected.connect(self.on_disconnected)

        print("[FileServer] Client connected.")

        self.file = None
        self.file_size = None
        self.received_size = 0

    def receive_video(self):
        """파일 크기를 먼저 받고, 이후 데이터만 저장"""
        if self.file_size is None:
            if self.client_socket.bytesAvailable() < 8:
                return  # 파일 크기를 읽을 수 있을 때까지 기다림
            
            self.file_size = struct.unpack("!Q", self.client_socket.read(8))[0]  # 8바이트 파일 크기 읽기
            print(f"[FileServer] Expected file size: {self.file_size} bytes")

            # 파일 저장 준비
            self.file = QFile("received_video.mp4")
            if not self.file.open(QIODevice.WriteOnly):
                print("[FileServer] Failed to open file for writing.")
                return

        while self.client_socket.bytesAvailable() > 0:
            data = self.client_socket.read(self.client_socket.bytesAvailable())
            self.file.write(data)
            self.received_size += len(data)
            print(f"[FileServer] Receiving video data... {self.received_size}/{self.file_size} bytes")

        # 파일을 다 받았으면 닫기
        if self.received_size >= self.file_size:
            print("[FileServer] File received successfully.")
            self.file.close()
            self.client_socket.disconnectFromHost()

    def on_disconnected(self):
        """클라이언트가 연결을 끊으면 파일을 저장하고 종료"""
        if self.file and self.file.isOpen():
            self.file.close()
        self.client_socket.deleteLater()
        print("[FileServer] Client disconnected.")

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러
    server = FileServer(port=8888)
    sys.exit(app.exec_())
