
# 클라이언트 연결 수락 및 처리

import sys
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress

from client_handler import ClientHandler
from config import SERVER_PORT, SERVER_IP
from database import FAAdb

class FAAServer(QTCPServer):
    def __init__(self):
        super(FAAServer, self).__init__()

    # client 연결 기다리기 
    def server_listen(self):
        if self.listen(QHostAddress.Any, SERVER_PORT): print(f"Server listening on port {SERVER_PORT}")
        else: print(f"Failed to listen on port {SERVER_PORT}")
    
    # client 연결 되면 식별하기  (QTcpServer 객체가 client연결 수신시 자동 being called )
    def incomingConnection(self, socketDescrpiter):    
        client_socket = ClientHandler(socketDescrpiter)
        client_socket.start() # thread 시작 
    

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    
    conn = FAAdb()          # db연결  
    server = FAAServer()    
    server.server_listen()   



    app.exec_() 