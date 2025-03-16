
# network in client sides 

import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SERVER_PORT, SERVER_IP

from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QObject, pyqtSignal 

class SocketClient(QObject) :
    # event를 받을 수 있는 signals 
    receive_data = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.socket = QTcpSocket()
        
        # connect socket - event 
        self.socket.readyRead.connect(self.readData)
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.errorOccurred.connect(self.on_error)

    def connect(self):
        self.socket.connectToHost(SERVER_IP, SERVER_PORT)
    def readData(self):
        data = self.socket.readAll().data().decode()
        self.receive_data.emit(data)
    def sendData(self, msg):
        if self.socket.state() == QTcpSocket.ConnectedState:
            self.socket.write(msg.encode())
            print(f"[Client] Sent: {msg}")
        
    # socket callbacks : gui에서 받을 수 있음 
    def on_connected(self):
        print("[Client] Connected to server")
        self.connected.emit()
    def on_disconnected(self):
        print("[Client] Disconnected from server")
        self.disconnected.emit()
    def on_error(self,err):
        print(f"[Client] Socket error: {err}")
        self.error.emit(str(err))

