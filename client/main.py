import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtNetwork import QTcpSocket
from config import SERVER_PORT, SERVER_PORT
from socket_client import Client
from server.database import FAAdb
import json

main_class = uic.loadUiType("./ui/auth.ui")[0]
second_class = uic.loadUiType("./ui/main_page.ui")[0]

class MainWindow(QMainWindow, main_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("User")

        db = FAAdb()
        self.cur = db.conn.cursor()
        self.tcp = Client()
        
        self.stackedWidget.setCurrentWidget(self.login_page)
        
        # 로그인 화면 버튼 이벤트
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.find_id_btn.clicked.connect(self.find_id)
        self.find_passwd_btn.clicked.connect(self.find_passwd)

        #회원가입 화면 버튼 이벤트
        self.register_complete_btn.clicked.connect(self.register_complete)

        #아이디 찾기 화면 버튼 이벤트
        self.find_id_result.clicked.connect(self.id_check)


    def login(self):
        id = self.input_id.text()
        passwd = self.input_passwd.text()

        data = {"command": 'LOGIN', "id":id,'passwd':passwd}
        self.tcp.sendData(data)

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
        loop.exec_()

        if self.tcp.result == 0:
            #QMessageBox.about(self, "로그인 성공", f"{self.tcp.response['name']} 님 안녕하세요.")
            client.close()
            self.client_main = secondWindow()
            self.client_main.show()
            #self.stackedWidget.setCurrentWidget(self.login_page)
        else:
            QMessageBox.about(self, "로그인 실패", "로그인 정보가 틀렸습니다.")
        #self.stackedWidget.setCurrentWidget(self.login_page)
    
    def register(self):
        self.stackedWidget.setCurrentWidget(self.register_page)
    def back2login (self):
        self.stackedWidget.setCurrentWidget(self.login_page)
    def find_id(self):
        self.stackedWidget.setCurrentWidget(self.find_id_page)
    
    def find_passwd(self):
        self.stackedWidget.setCurrentWidget(self.id_check_page)
    
    def register_complete(self):
        self.stackedWidget.setCurrentWidget(self.login_page)
    
    def id_check(self):
        current_widget = self.stackedWidget.currentWidget()
        widget_name = current_widget.objectName()

        name = self.find_id_input_name.text()
        email = self.find_id_input_email.text()
        #self.tcp.sendData("FIND_ID")
        data = {"command": 'FIND_ID', "name":name,'email':email}  # JSON 데이터 생성
        self.tcp.sendData(data)  # JSON 문자열을 바이트로 변환하여 전송

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
        loop.exec_()  # 응답이 올 때까지 여기서 대기

        if self.tcp.result == 0:
            QMessageBox.about(self, "아이디 찾기", f"아이디는 {self.tcp.response['id']}입니다.")
            self.stackedWidget.setCurrentWidget(self.login_page)
        else:
            QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
    
    def passwd_reset(self):
        self.passwd_reset_input_passwd.text()
        self.stackedWidget.setCurrentWidget(self.login_page)
    
    def receiveData(self, data):
        command = data["command"]
    

class secondWindow(QMainWindow, second_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("main_page")

        # 버튼을 toggle 가능하게 변경
        self.btn_workout.setCheckable(True)
        self.btn_record.setCheckable(True)
        self.btn_rank.setCheckable(True)
        self.btn_challenge.setCheckable(True)

        # 버튼 그룹으로 묶어서 exclusive 설정
        self.tab_group = QButtonGroup()
        self.tab_group.addButton(self.btn_workout)
        self.tab_group.addButton(self.btn_record)
        self.tab_group.addButton(self.btn_rank)
        self.tab_group.addButton(self.btn_challenge)
        self.tab_group.setExclusive(True)

        # 페이지 전환 이벤트 연결 
        self.btn_workout.clicked.connect(self.show_main)
        self.btn_record.clicked.connect(self.show_record)
        self.btn_rank.clicked.connect(self.show_rank)
        self.btn_challenge.clicked.connect(self.show_challenge)
        # 첫 화면 기본 설정 
        self.btn_workout.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.main_page)

    # pages 
    def show_main(self):
        self.stackedWidget.setCurrentWidget(self.main_page)

    def show_record(self):
        self.stackedWidget.setCurrentWidget(self.record_page)

        self.radio_day.setChecked(True)
        self.radio_day.toggled.connect(self.switch_graph)
        self.radio_week.toggled.connect(self.switch_graph)
        self.radio_month.toggled.connect(self.switch_graph)
    
    def show_rank(self):
        self.stackedWidget.setCurrentWidget(self.rank_page)


    def show_challenge(self):
        self.stackedWidget.setCurrentWidget(self.challenge_page)

    def switch_graph(self):
        if self.radio_day.isChecked():
            self.stackedGraphs.setCurrentIndex(0)
        elif self.radio_week.isChecked():
            self.stackedGraphs.setCurrentIndex(1)
        elif self.radio_month.isChecked():
            self.stackedGraphs.setCurrentIndex(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())
