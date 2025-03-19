from PyQt5.QtCore import QThread
from PyQt5.QtNetwork import QTcpSocket
class ClientHandler(QThread):
    def __init__(self, socketDescriptor):
        super().__init__()
        self.socketDescriptor = socketDescriptor
        self.client_socket = None
    def run(self):
        """
        QThread가 start()될 때 실제로 동작하는 메인 함수.
        여기서 소켓을 생성하고, 이벤트(readyRead 등)를 연결한 뒤
        self.exec_()로 이벤트 루프를 돌려주어야 신호 처리가 정상적으로 이루어짐짐
        """
        self.client_socket = QTcpSocket()
        # 소켓 디스크립터를 현재 쓰레드의 소켓에 세팅
        self.client_socket.setSocketDescriptor(self.socketDescriptor)
        # 클라이언트로부터 데이터가 도착했을 때
        self.client_socket.readyRead.connect(self.receive_data)
        # 클라이언트가 연결을 끊었을 때
        self.client_socket.disconnected.connect(self.disconnected)
        # 쓰레드 내 이벤트 루프 시작
        self.exec_()
    def receive_data(self):
        while self.client_socket.bytesAvailable() > 0:
            data = self.client_socket.readAll().data()
            print("[Server] 클라이언트 메세지 : ", data.decode("utf-8"))
            response = b"Server Received Your Message"
            self.client_socket.write(response)
            self.client_socket.flush()
    def disconnected(self):
        print(f"[Server] client disconnected : {self.client_socket.peerAddress().toString()}")
        self.client_socket.close()
        self.quit()  # 스레드 이벤트 루프 종료