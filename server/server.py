import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import signal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from config import SERVER_PORT
from database import FAAdb
import json
import struct

class FAAServer(QTcpServer):
    def __init__(self):
        super(FAAServer, self).__init__()
        self.client_list = []
        self.db = FAAdb()
        self.cur = self.db.conn.cursor()

    def start_server(self):
        if self.listen(QHostAddress.Any, SERVER_PORT): print(f"Server listening on port {SERVER_PORT}")
        else: print(f"Failed to listen on port {SERVER_PORT}")

    def incomingConnection(self, socketDescriptor):
        self.client_socket = QTcpSocket(self)
        self.client_socket.setSocketDescriptor(socketDescriptor)
        print(f"클라이언트 연결됨: {self.client_socket.peerAddress().toString()}:{self.client_socket.peerPort()}")

        # 클라이언트 연결 및 데이터 수신, 종료 핸들러 등록
        self.client_socket.readyRead.connect(lambda: self.receive_data(self.client_socket))
        self.client_socket.disconnected.connect(lambda: self.disconnected(self.client_socket))

        self.client_list.append(self.client_socket)

    def receive_data(self, client_socket):
        while client_socket.bytesAvailable() > 0:
            data = client_socket.readAll().data()
            self.data = self.unpack_data(data)
            print(f"[Server] 클라이언트 메세지 : {self.data}")
            # response = b"Server Received Your Message"
            # client_socket.write(response)
            # client_socket.flush()
            # print(self.data['command'])
            if self.data['command'] == "FI":
                 print("아이디찾기")
                 self.find_id()
            elif self.data['command'] == "LI":
                 print("로그인")
                 self.login()  
            elif self.data['command'] == "RS":
                 print("회원가입")
                 self.register() 
    
    def unpack_data(self, binary_data):
        offset = 0
        
        # 명령어 언패킹
        command_len = struct.unpack_from('I', binary_data, offset)[0]
        offset += 4
        command = binary_data[offset:offset + command_len].decode('utf-8')
        offset += command_len
        
        def unpack_string():
            nonlocal offset
            length = struct.unpack_from('I', binary_data, offset)[0]
            offset += 4
            if length > 0:
                value = binary_data[offset:offset + length].decode('utf-8')
                offset += length
                return value
            return None
        
        # 각 필드 언패킹
        id = unpack_string()
        pw = unpack_string()
        name = unpack_string()
        email = unpack_string()
        data = unpack_string()
        content = unpack_string()
        
        return {
            'command': command,
            'id': id,
            'pw': pw,
            'name': name,
            'email': email,
            'data': data,
            'content': content
        }

    def pack_data(self, command, status=None, name=None, err=None, id=None, list_data=None, routine_number=None, total_day=None, total_time=None,email=None):
        packed_data = b''
        
        # 명령어 패킹 (길이 + 데이터)
        packed_data += struct.pack('I', len(command)) + command.encode('utf-8')
        
        # ID 패킹 (길이 + 데이터)
        if id is not None:
            packed_data += struct.pack('I', len(id)) + id.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 상태 패킹 (길이 + 데이터)
        if status is not None:
            packed_data += struct.pack('I', len(status)) + status.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이름 패킹 (길이 + 데이터)
        if name is not None:
            packed_data += struct.pack('I', len(name.encode('utf-8'))) + name.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 에러 메시지 패킹 (길이 + 데이터)
        if err is not None:
            packed_data += struct.pack('I', len(err)) + err.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 리스트 데이터 패킹
        if list_data is not None:
            list_bytes = list_data.encode('utf-8')
            packed_data += struct.pack('I', len(list_bytes)) + list_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        # 루틴 번호 패킹
        if routine_number is not None:
            packed_data += struct.pack('I', len(routine_number)) + routine_number.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 총 일수 패킹
        if total_day is not None:
            packed_data += struct.pack('I', len(total_day)) + total_day.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 총 시간 패킹
        if total_time is not None:
            packed_data += struct.pack('I', len(total_time)) + total_time.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        if email is not None:
            packed_data += struct.pack('I', len(email)) + email.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        return packed_data
    
    def send_data(self,client_socket, response_data):
        if client_socket.state() == QTcpSocket.ConnectedState:
            client_socket.write(response_data)
            client_socket.flush()
            print(f"[Server] 클라이언트로 응답 전송: {response_data}")
        else:
            print("[Server] 클라이언트와의 연결이 끊어져 응답을 전송할 수 없습니다.")

    def disconnected(self, client_socket):
        print(f"[Server] client disconnected : {client_socket.peerAddress().toString()}")
        self.client_list.remove(client_socket)
        client_socket.deleteLater()
    
    def find_id(self):
        if self.data['id'] == None:
            self.cur.execute("SELECT login_id FROM user where email = %s",(self.data['email'],))
            rows = self.cur.fetchall()
            if len(rows) == 0:
                print('없어용')
                #data = {"command":"FIND_ID_RESULT","status":1,}
                data = self.pack_data("FR",status='1')
                #QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
            else:
                #QMessageBox.about(self, "아이디 찾기", f"아이디는 {rows[0][0]}입니다.")
                #self.stackedWidget.setCurrentWidget(self.login_page)
                print(rows[0][0])
                #data = {"command":"FIND_ID_RESULT","status":0,'id':rows[0][0]}
                data = self.pack_data("FR",status='0',id=rows[0][0])
        else:
            self.cur.execute("SELECT login_id FROM user where login_id = %s and email = %s",(self.data['id'],self.data['email'],))
            rows = self.cur.fetchall()
            if len(rows) == 0:
                print('없어용')
                #data = {"command":"FIND_ID_RESULT","status":1,}
                data = self.pack_data("FR",status='1')
                #QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
            else:
                #QMessageBox.about(self, "아이디 찾기", f"아이디는 {rows[0][0]}입니다.")
                #self.stackedWidget.setCurrentWidget(self.login_page)
                print(rows[0][0])
                #data = {"command":"FIND_ID_RESULT","status":0,'id':rows[0][0]}
                data = self.pack_data("FR",status='0',id=rows[0][0])
        
        self.send_data(self.client_socket,data)
    
    def login(self):
        self.cur.execute("SELECT login_id FROM user where login_id = %s and password = %s",(self.data['id'],self.data['pw']))
        rows = self.cur.fetchall()
        print(rows[0][0])
        if len(rows) == 0:
            print('로그인정보가 틀렸습니다.')
            #data = {"command":"LOGIN_RESULT","status":1,"err":"Invalid credentials"}
            data = self.pack_data("LR",status='1',err="Invalid credentials")


            #QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
        else:
            #QMessageBox.about(self, "아이디 찾기", f"아이디는 {rows[0][0]}입니다.")
            #self.stackedWidget.setCurrentWidget(self.login_page)
            print(rows[0][0])
            #data = {"command":"LOGIN_RESULT","status":0,'login_id':rows[0][0]}
            data = self.pack_data("LR",status='0',id=rows[0][0])
        self.send_data(self.client_socket,data)
    
    def register(self):
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM user WHERE login_id = %s)",(self.data['id'],))
        duplication_id= int(self.cur.fetchall()[0][0])

        self.cur.execute("SELECT EXISTS(SELECT 1 FROM user WHERE email = %s)",(self.data['email'],))
        duplication_email= int(self.cur.fetchall()[0][0])
        print(duplication_id)
        print(duplication_email)
        if duplication_id == 1:
            data = self.pack_data("RR",status='1')
        
        if duplication_email == 1:
            data = self.pack_data("RR",status='2')
        
        if duplication_id == 0 and duplication_email == 0:
            self.cur.execute("insert into user(login_id, password, email) values(%s, %s, %s)",(self.data['id'],self.data['pw'],self.data['email']))
            self.db.commit()
            data = self.pack_data("RR",status='0')
               
        self.send_data(self.client_socket,data)
    

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러

    conn = FAAdb()
    server = FAAServer()
    server.start_server()

    app.exec_()
