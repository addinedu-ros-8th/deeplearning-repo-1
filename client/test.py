import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from socket_client import SocketClient
import mysql.connector
from PyQt5.QtNetwork import QTcpSocket


import os 
from config import SERVER_PORT, SERVER_IP

remote = mysql.connector.connect(
            host="addinedu.synology.me",
            user='faa',
            password='Addinedu1!@',
            database = 'faa'
        )
cur = remote.cursor()

from_class = uic.loadUiType("./test.ui")[0]

class MyWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.socket = QTcpSocket()
        self.setupUi(self)

        self.stackedWidget.setCurrentWidget(self.login_page)

        self.socket_client = SocketClient()
        self.socket_client.connect()

        self.server_ip = SERVER_IP
        self.server_port = SERVER_PORT

        self.socket_client.connect(SERVER_IP,SERVER_PORT)

        # self.socket_client.connected.connect(self.on_connected)
        # self.socket_client.disconnected.connect(self.on_disconnected)
        # self.socket_client.error.connect(self.on_error)
        # self.socket.readyRead.connect(self.readData)
        # self.socket.readyReceve.connect(self.receveData)


        
        #로그인 화면 버튼 이벤트
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.find_id_btn.clicked.connect(self.find_id)
        self.find_passwd_btn.clicked.connect(self.find_passwd)

        #회원가입 화면 버튼 이벤트
        self.register_complete_btn.clicked.connect(self.register_complete)

        #아이디 찾기 화면 버튼 이벤트
        self.find_id_result.clicked.connect(self.id_check)

        #비밀번호 찾기 화면 버튼 이벤트
        self.id_check_btn.clicked.connect(self.id_check)

        #비밀번호 재설정 화면 버튼 이벤트
        self.passwd_reset_btn.clicked.connect(self.passwd_reset)
    # def on_connected(self):

    def login(self):
        input_id = self.input_login_id.text()
        input_password = self.input_password.text()
        msg = f"LOGIN {input_id} {input_password}"
        self.socket_client.sendData(msg)
        cur.execute("SELECT login_id,password FROM user WHERE (login_id = %s, password = %s)",(input_id,input_password))
        result = cur.fetchone()[0]
        
        if result is not None :
            db_password = result[1]
            if input_password == db_password:
                QMessageBox.about(self, "로그인", "로그인 성공!")
                self.stackedWidget.setCurrentWidget(self.main_page)
            else:
                self.socket_client.sendData(msg)
                self.stackedWidget.setCurrentWidget(self.login_page)

    
    def register(self):
        self.stackedWidget.setCurrentWidget(self.register_page)
    
    def find_id(self):
        self.stackedWidget.setCurrentWidget(self.find_id_page)
    
    def find_passwd(self):
        self.stackedWidget.setCurrentWidget(self.id_check_page)
    
    def register_complete(self):
        name = self.input_name.text()
        login_id = self.input_id.text()
        password = self.input_password.text()
        email = self.input_email.text()
        height = self.input_height.text()
        weight = self.input_weight.text()
        
        if password != self.pw_check:
            QMessageBox.about(self, '비밀번호 오류','비밀번호를 확인하세요')
            return
        
        cur.execute("INSERT INTO user(name, login_id,password,email,height,weight) VALUE (%s,%s,%s,%s,%s,%s)",(name,login_id,password,email,height,weight))
        self.stackedWidget.setCurrentWidget(self.login_page)
    
    def id_check(self):
        current_widget = self.stackedWidget.currentWidget()
        widget_name = current_widget.objectName()
        #print(widget_name)
        if widget_name == "find_id_page":
            name = self.find_id_input_name.text()
            email = self.find_id_input_email.text()
            cur.execute("SELECT login_id FROM user where name = %s and email = %s",(name,email))
            rows = cur.fetchall()
            if len(rows) == 0:
                QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
            else:
                QMessageBox.about(self, "아이디 찾기", f"아이디는 {rows[0][0]}입니다.")
                name.clear()
                email.clear()  
                self.stackedWidget.setCurrentWidget(self.login_page)
                #확인 -> 리셋 

        else:
            name = self.id_check_input_name.text()
            id = self.id_check_input_id.text()
            email = self.id_check_input_email.text()
            cur.execute("SELECT login_id FROM user where name = %s and email = %s and login_id = %s",(name,email,id))
            rows = cur.fetchall()
            if len(rows) == 0:
                QMessageBox.about(self, "아이디 확인", "일치하는 아이디가 없습니다.")
            else:
                QMessageBox.about(self, "아이디 확인", f"아이디가 확인되었습니다.")
                
                self.stackedWidget.setCurrentWidget(self.passwd_reset_page)

    def passwd_reset(self):
        # name = self.id_check_input_name.text()
        # id = self.id_check_input_id.text()
        # email = self.id_check_input_email.text()
        # cur.execute("SELECT (name,login_id,email) FROM user WHERE name = %s and login_id = %s and email = %s",(name,id,email))
        self.passwd_reset_input_passwd.text()
        if passwd_reset_input_passwd != self.check_passwd_for_reset:
            QMessageBox.about(self, '재확인 오류','비밀번호 확인해주세요')
            return
        cur.execute("UPDATE user SET password=%s WHERE password")
        self.stackedWidget.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    myWindow.socket_client.connected("127.0.0.1",8888)
    sys.exit(app.exec_())
