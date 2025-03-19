
# network in client sides 

import sys
import os 
import signal 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SERVER_PORT, SERVER_IP

from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QObject, pyqtSignal,QCoreApplication

class Client(QObject) :    
    def __init__(self):
        super().__init__()
        self.socket = QTcpSocket()                              # 1. create socket 
        self.socket.connectToHost(SERVER_IP, SERVER_PORT)       # 2. connect to server 
        self.socket.connected.connect(self.on_connected)        # 3. send data 
        self.socket.readyRead.connect(self.readData)            # 4. read data 
        
    def on_connected(self):
        print("[Client] Connected to server")
        self.send_data()
    
    def send_data(self):
        if self.socket.state() == QTcpSocket.ConnectedState:  # :흰색_확인_표시: 연결 상태 확인
            message = b"hi,server"
            self.socket.write(message)
            self.socket.flush()

    def readData(self):
        if self.socket.bytesAvailable()>0:
            response = self.socket.readAll().data()
            print("서버 응답 : ",response.decode("utf-8"))
            # self.receive_data.emit(data)

    def sendData(self, msg):
        if self.socket.state() == QTcpSocket.ConnectedState:
            message = b"hi,server"
            self.socket.write(message)
            print("서버로 메세지 전송 : ", message.decode("utf-8"))

    def on_disconnected(self):
        print("[Client] Disconnected from server")
        self.disconnected.emit()
    def on_error(self,err):
        print(f"[Client] Socket error: {err}")
        self.error.emit(str(err))

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)    # Ctrl+C 시그널 등록
    client = Client() 
    sys.exit(app.exec_())