import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import signal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from config import SERVER_PORT
from database import FAAdb

class FAAServer(QTcpServer):
    def __init__(self):
        super(FAAServer, self).__init__()
        self.client_list = []

    def start_server(self):
        if self.listen(QHostAddress.Any, SERVER_PORT): print(f"Server listening on port {SERVER_PORT}")
        else: print(f"Failed to listen on port {SERVER_PORT}")

    def incomingConnection(self, socketDescriptor):
        client_socket = QTcpSocket(self)
        client_socket.setSocketDescriptor(socketDescriptor)
        print(f"클라이언트 연결됨: {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")

        # 클라이언트 연결 및 데이터 수신, 종료 핸들러 등록
        client_socket.readyRead.connect(lambda: self.receive_data(client_socket))
        client_socket.disconnected.connect(lambda: self.disconnected(client_socket))

        self.client_list.append(client_socket)

    def receive_data(self, client_socket):
        while client_socket.bytesAvailable() > 0:
            data = client_socket.readAll().data()
            print(f"[Server] 클라이언트 메세지 : {data.decode('utf-8')}")
            response = b"Server Received Your Message"
            client_socket.write(response)
            client_socket.flush()

    def disconnected(self, client_socket):
        print(f"[Server] client disconnected : {client_socket.peerAddress().toString()}")
        self.client_list.remove(client_socket)
        client_socket.deleteLater()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러

    conn = FAAdb()
    server = FAAServer()
    server.start_server()

    app.exec_()
