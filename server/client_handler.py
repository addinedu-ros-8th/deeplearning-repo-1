

# Server의 각 client와의 연결 관리 
# 소켓을 다루고 client로 부터 받은 데이터 처리하고 응답을 보내는 코드 

from PyQt5.QtCore import QThread
from PyQt5.QtNetwork import QTcpSocket

class ClientHandler(QThread):
    def __init__(self, socketDescriptor):
        self.client_socket = QTcpSocket()
        self.client_socket.setSocketDescriptor(socketDescriptor)

    def start(self):
        # 클라이언트로부터 데이터가 도착했을 때
        self.client_socket.readyRead.connect(self.receive_data)
        # 클라이언트가 연결을 끊었을 때
        self.client_socket.disconnected.connect(self.disconnected)
        self.client_socket.errorOccurred.connect(lambda err: self.socketError(self.client_socket, err))

    def socketError(self, client_socket, err):
        if client_socket.state() == QTcpSocket.UnconnectedState: self.clientDisconnected(client_socket)

    def receive_data(self):
        data = self.client_socket.readAll().data()
        if data:
            print("Data received from client.") 
            self.send_response("Data received successfully")

    def disconnected(self):
        # 클라이언트가 연결을 끊었을 때 처리 
        print(f"client disconnected : {self.client_socket}")
        self.client_socket.deleteLater()
        self.quit()  # 스레드 종료

    def send_response(self, message):
        # 클라이언트에 응답 보내기
        self.client_socket.write(message.encode())
        print("Response sent to client.")