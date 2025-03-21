import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import signal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from config import SERVER_PORT
from database import FAAdb
import json

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
            data = data.decode('utf-8')
            self.data = json.loads(data)
            print(f"[Server] 클라이언트 메세지 : {data}")
            # response = b"Server Received Your Message"
            # client_socket.write(response)
            # client_socket.flush()
            print(self.data['command'])
            if self.data['command'] == "FIND_ID":
                print("아이디찾기")
                self.find_id()
            elif self.data['command'] == "LOGIN":
                print("로그인")
                self.login()  
    
    def send_data(self,client_socket, response_data):
        if client_socket.state() == QTcpSocket.ConnectedState:
            json_data = json.dumps(response_data, default=str)
            client_socket.write(json_data.encode('utf-8'))
            client_socket.flush()
            print(f"[Server] 클라이언트로 응답 전송: {json_data}")
        else:
            print("[Server] 클라이언트와의 연결이 끊어져 응답을 전송할 수 없습니다.")

    def disconnected(self, client_socket):
        print(f"[Server] client disconnected : {client_socket.peerAddress().toString()}")
        self.client_list.remove(client_socket)
        client_socket.deleteLater()
    
    def find_id(self):
        self.cur.execute("SELECT login_id FROM user where name = %s and email = %s",(self.data['name'],self.data['email']))
        rows = self.cur.fetchall()
        if len(rows) == 0:
            print('없어용')
            data = {"command":"FIND_ID_RESULT","status":1,}
            #QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
        else:
            #QMessageBox.about(self, "아이디 찾기", f"아이디는 {rows[0][0]}입니다.")
            #self.stackedWidget.setCurrentWidget(self.login_page)
            print(rows[0][0])
            data = {"command":"FIND_ID_RESULT","status":0,'id':rows[0][0]}
        
        self.send_data(self.client_socket,data)
    
    def login(self):
        self.cur.execute("SELECT name FROM user where login_id = %s and password = %s",(self.data['id'],self.data['passwd']))
        rows = self.cur.fetchall()
        if len(rows) == 0:
            print('로그인정보가 틀렸습니다.')
            data = {"command":"LOGIN_RESULT","status":1,"err":"Invalid credentials"}
            #QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
        else:
            #QMessageBox.about(self, "아이디 찾기", f"아이디는 {rows[0][0]}입니다.")
            #self.stackedWidget.setCurrentWidget(self.login_page)
            print(rows[0][0])
            data = {"command":"LOGIN_RESULT","status":0,'name':rows[0][0]}
        self.send_data(self.client_socket,data)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러

    conn = FAAdb()
    server = FAAServer()
    server.start_server()

    app.exec_()
