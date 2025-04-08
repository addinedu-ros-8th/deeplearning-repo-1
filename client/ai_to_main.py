
# ai_to_main 

import sys
import os 
import signal 
import json 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SERVER_PORT, SERVER_IP

from PyQt5.QtNetwork import QTcpSocket, QUdpSocket
from PyQt5.QtCore import QObject, pyqtSignal,QCoreApplication
import struct


class AitoMain(QObject) :    
    responseReceived = pyqtSignal()
    routineIndexUpdated = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.socket = QTcpSocket()                              # 1. create socket 
        self.socket.connectToHost(SERVER_IP, SERVER_PORT)       # 2. connect to server 
        self.socket.connected.connect(self.on_connected)        # 3. send data 
        self.socket.readyRead.connect(self.readData)            # 4. read data 

        self.udp_socket = QUdpSocket()
        self.result = None
        self.name=None
        
    def on_connected(self):
        print("[Client] Connected to server")
        self.socket.write(b'AI_HELLO')
        self.socket.flush()

    def readData(self):
        if self.socket.bytesAvailable() > 0:
            data = self.socket.readAll().data()

            # JSON이면 무시
            if data.startswith(b'{'):
                print("[AitoMain] JSON 메시지 수신됨 (AI 서버에서 처리할 예정)")
                return

            # ✅ 그 외는 바이너리로 해석
            try:
                self.data = self.unpack_data(data)
                print("서버 응답 : ", self.data)

                if self.data['command'] == 'FR':
                    self.result = int(self.data['status'])
                    self.responseReceived.emit()
                elif self.data['command'] == 'LR':
                    self.result = int(self.data['status'])
                    self.responseReceived.emit()
                elif self.data['command'] == 'RR':
                    self.result = int(self.data['status'])
                    self.responseReceived.emit()
                elif self.data['command'] == 'RC':
                    self.result = self.data['status']
                    self.name=self.data['name']

                self.responseReceived.emit()

            except Exception as e:
                print("[AitoMain] 바이너리 패킷 파싱 실패:", e)

    
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
            # 전송 완료 대기

    def on_disconnected(self):
        print("[Client] Disconnected from server")
        self.disconnected.emit()
    def on_error(self,err):
        print(f"[Client] Socket error: {err}")
        self.error.emit(str(err))

    def pack_data(self, command, status=None, pw=None, name=None, height=None, weight=None, data=None, content=None, image_data=None, joint=None, angle=None):
        packed_data = b''

        def pack_string(value):
            if value is not None:
                encoded = value.encode('utf-8')
                return struct.pack('I', len(encoded)) + encoded
            return struct.pack('I', 0)

        # 언팩 순서에 맞춰서 패킹
        packed_data += pack_string(command)
        packed_data += pack_string(status)
        packed_data += pack_string(pw)
        packed_data += pack_string(name)
        packed_data += pack_string(str(height) if height is not None else None)
        packed_data += pack_string(str(weight) if weight is not None else None)
        packed_data += pack_string(data)
        packed_data += pack_string(content)

        # 이미지 데이터 패킹
        if image_data is not None:
            packed_data += struct.pack('I', len(image_data)) + image_data
        else:
            packed_data += struct.pack('I', 0)

        # joint 리스트 패킹
        if joint is not None:
            packed_data += struct.pack('I', len(joint))
            for j in joint:
                packed_data += struct.pack('I', j)
        else:
            packed_data += struct.pack('I', 0)

        # angle 패킹 (람다 함수는 문자열로 변환)
        if angle is not None:
            if callable(angle):
                angle_str = f"lambda idx: {angle(0)}"
            else:
                angle_str = str(angle)
            packed_data += pack_string(angle_str)
        else:
            packed_data += struct.pack('I', 0)

        return packed_data

    
if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)    # Ctrl+C 시그널 등록
    client = AitoMain() 
    sys.exit(app.exec_())