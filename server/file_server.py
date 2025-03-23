from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt5.QtCore import QCoreApplication, QFile, QIODevice
import sys

class FileServer:
    def __init__(self, port=12346):
        self.server = QTcpServer()
        self.server.listen(QHostAddress.Any, port)
        self.server.newConnection.connect(self.on_new_connection)
        print(f"[FileServer] Listening on port {port}...")

    def on_new_connection(self):
        """클라이언트가 연결되면 실행"""
        self.client_socket = self.server.nextPendingConnection()
        self.client_socket.readyRead.connect(self.receive_file)
        self.client_socket.disconnected.connect(self.on_disconnected)

        print("[FileServer] Client connected.")

        # 파일 저장 준비
        self.file = QFile("received_file.MOV")
        if not self.file.open(QIODevice.WriteOnly):
            print("[FileServer] Failed to open file for writing.")
            return

    def receive_file(self):
        """클라이언트에서 데이터를 받아 파일에 저장"""
        if not self.file.isOpen():
            print("[FileServer] File is not open.")
            return
        
        data = self.client_socket.readAll()
        self.file.write(data)
        print(f"[FileServer] Receiving file data... {len(data)} bytes received.")

    def on_disconnected(self):
        """클라이언트가 연결을 끊으면 파일을 닫음"""
        if self.file.isOpen():
            self.file.close()
            print("[FileServer] File saved successfully.")
        self.client_socket.deleteLater()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    server = FileServer()
    sys.exit(app.exec_())
