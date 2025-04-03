# auth_window.py
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QEventLoop
from server.database import FAAdb
from network.socket_client import Client

from PyQt5 import uic

auth_class = uic.loadUiType("client/ui/auth.ui")[0]

class AuthWindow(QMainWindow, auth_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Authentication")

        self.db = FAAdb()
        self.cur = self.db.conn.cursor()

        self.tcp = Client()
        self.profile_cnt = 0
        self.stackedWidget.setCurrentWidget(self.add_profile_page)

        #프로필 설정 화면 버튼 이벤트
        self.btn_select_profile_img.clicked.connect(self.select_icon)
        self.btn_profile_save.clicked.connect(self.profile_save)

    def select_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "/home/sang/dev_ws/save_file/profile_icon", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_path:
            pixmap = QPixmap(file_path)
            self.label.setPixmap(pixmap.scaled(300, 300))  # 크기 조절
            self.btn_select_profile_img.setStyleSheet(f"""
                QPushButton {{
                    border-image: url({file_path});
                    min-width: 200px;
                    min-height: 200px;
                }}
            """)
        with open(file_path,"rb") as file:
            self.image_data = file.read()

    def profile_save(self):
        name = self.profile_input_name.text()
        height = self.profile_input_height.text()
        weight = self.profile_input_weight.text()
        passwd = self.profile_input_passwd.text()        
        data = self.main.pack_data(command="RG", name=name, pw=passwd, image_data=self.image_data, height=height, weight= weight)
        self.main.tcp.sendData(data)  

        loop = QEventLoop()
        self.main.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
        loop.exec_()  # 응답이 올 때까지 여기서 대기
        if self.tcp.result == 0:
            QMessageBox.about(self, "회원가입", "가입 성공")
            self.close()
        elif self.tcp.result == 1:
            QMessageBox.about(self, "회원가입", "이름 중복")
        
        # if self.main.tcp.result == 0:
        #     QMessageBox.about(self, "회원가입", "가입 성공")
        #     self.close()
        #     self.client_main = MainWindow()
        #     self.client_main.profile_cnt += 1
        #     self.client_main.add_profile(self.client_main.profile_cnt)

            #self.cur.execute("insert into user(name, height, weight, user_icon, password, tier) values(%s, %s, %s, %s, %s,0)",(name,weight,height,self.image_data, passwd))
        # elif self.main.tcp.result == 1:
        #     QMessageBox.about(self, "회원가입", "이름 중복")
       
        #self.cur.execute("insert into user(name, height, weight, user_icon, password) values(%s, %s, %s, %s, %s)",(name,weight,height,self.image_data, passwd))
        #self.db.commit()
        