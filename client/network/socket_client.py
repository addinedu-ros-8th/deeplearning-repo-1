
# network in client sides 

import sys
import os 
import signal 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SERVER_PORT, SERVER_IP

from PyQt5.QtNetwork import QTcpSocket, QUdpSocket
from PyQt5.QtCore import QObject, pyqtSignal,QCoreApplication
from ai_to_main import AitoMain
import json
import struct

class Client(QObject) :    
    responseReceived = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.AiSocket = AitoMain()
        self.socket = QTcpSocket()                              # 1. create socket 
        self.socket.connectToHost(SERVER_IP, SERVER_PORT)       # 2. connect to server 
        self.socket.connected.connect(self.on_connected)        # 3. send data 
        self.socket.readyRead.connect(self.readData)            # 4. read data 

        self.udp_socket = QUdpSocket()
        

        self.result = None
        
    def on_connected(self):
        print("[Client] Connected to server")

    def readData(self):
        if self.socket.bytesAvailable()>0:
            data = self.socket.readAll().data()
            self.data = self.unpack_data(data)
            print("서버 응답 : ",self.data)
            #print(type(response))
            #print(self.response['status'])
            
            if self.data['command'] == 'LI':
                self.result = int(self.data['status'])
                self.responseReceived.emit()
            elif self.data['command'] == 'RG':
                self.result = int(self.data['status'])
                self.responseReceived.emit()
            elif self.data['command'] == 'CT':
                print(self.data['status'])
                self.result = int(self.data['status'])
                self.responseReceived.emit()
            # self.receive_data.emit(data)
    
    def unpack_data(self, binary_data):
        offset = 0
        
        def unpack_string():
            nonlocal offset
            length = struct.unpack_from('I', binary_data, offset)[0]
            offset += 4
            if length > 0:
                value = binary_data[offset:offset+length].decode('utf-8')
                offset += length
                return value
            return None
        
        command = unpack_string()
        id = unpack_string()
        status = unpack_string()
        name = unpack_string()
        err = unpack_string()
        list_data = unpack_string()
        routine_number = unpack_string()
        total_day = unpack_string()
        total_time = unpack_string()
        email = unpack_string()
        
        return {
            "command": command,
            "id": id,
            "status": status,
            "name": name,
            "err": err,
            "list_data": list_data,
            "routine_number": routine_number,
            "total_day": total_day,
            "total_time": total_time,
            "email":email
        }
            
    def sendData(self, data):
        if self.socket.state() == QTcpSocket.ConnectedState:
            self.socket.write(data)
            self.socket.flush()
            print("서버로 메세지 전송 : ", data)

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