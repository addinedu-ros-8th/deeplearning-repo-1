import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtNetwork import QTcpSocket
from config import SERVER_HOST, SERVER_PORT

from_class = uic.loadUiType("./client.ui")[0]

class MainWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("User")
        
        self.stackedWidget.setCurrentWidget(self.login_page)

        # init socket 
        
        # 로그인 화면 버튼 이벤트
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

    def login(self):
        self.stackedWidget.setCurrentWidget(self.login_page)
    
    def register(self):
        self.stackedWidget.setCurrentWidget(self.register_page)
    
    def find_id(self):
        self.stackedWidget.setCurrentWidget(self.find_id_page)
    
    def find_passwd(self):
        self.stackedWidget.setCurrentWidget(self.id_check_page)
    
    def register_complete(self):
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
                self.stackedWidget.setCurrentWidget(self.login_page)
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
        self.passwd_reset_input_passwd.text()
        self.stackedWidget.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())
