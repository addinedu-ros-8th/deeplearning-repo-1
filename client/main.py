import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtNetwork import QTcpSocket, QUdpSocket
from config import SERVER_PORT, SERVER_PORT
from socket_client import Client
from server.database import FAAdb
import json
import struct

main_class = uic.loadUiType("/home/sang/dev_ws/save_file/client/ui/auth.ui")[0]
second_class = uic.loadUiType("/home/sang/dev_ws/save_file/client/ui/main_page.ui")[0]

class MainWindow(QMainWindow, main_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("User")

        self.db = FAAdb()
        self.cur = self.db.conn.cursor()
        self.tcp = Client()
        
        self.stackedWidget.setCurrentWidget(self.login_page)
        self.profile_cnt = 0
        
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

        #프로필 설정 화면 버튼 이벤트
        self.btn_select_profile_img.clicked.connect(self.select_icon)
        self.btn_profile_save.clicked.connect(self.profile_save)

    def login(self):
        id = self.input_id.text()
        passwd = self.input_passwd.text()

        #data = {"command": 'LOGIN', "id":id,'passwd':passwd}
        data = self.pack_data(command="LI", id=id, pw=passwd)
        self.tcp.sendData(data)

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
        loop.exec_()

        if self.tcp.result == 0:
            client.close()
            self.client_main = secondWindow()
            self.client_main.show()
        else:
            QMessageBox.about(self, "로그인 실패", "로그인 정보가 틀렸습니다.")
    
    def register(self):
        self.stackedWidget.setCurrentWidget(self.register_page)
    
    def find_id(self):
        self.stackedWidget.setCurrentWidget(self.find_id_page)
    
    def find_passwd(self):
        self.stackedWidget.setCurrentWidget(self.id_check_page)
    
    def register_complete(self):
        id = self.register_input_id.text()
        passwd = self.register_input_passwd.text()
        passwd_compare = self.input_passwd_compare.text()
        email = self.register_input_email.text()
        
        if passwd == passwd_compare:
            data = self.pack_data(command="RS", id=id, pw=passwd, email=email)
            self.tcp.sendData(data)

            loop = QEventLoop()
            self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
            loop.exec_()  # 응답이 올 때까지 여기서 대기

            if self.tcp.result == 0:
                QMessageBox.about(self, "회원가입", "가입 성공")
                self.stackedWidget.setCurrentWidget(self.login_page)
            elif self.tcp.result == 1:
                QMessageBox.about(self, "회원가입", "아이디 중복")
            elif self.tcp.result == 2:
                QMessageBox.about(self, "회원가입", "이메일 중복")
        else:
            QMessageBox.warning(self, "회원가입", "비밀번호가 일치하지 않습니다.")

    
    def id_check(self):
        current_widget = self.stackedWidget.currentWidget()
        widget_name = current_widget.objectName()
        #print(widget_name)

        if widget_name == 'find_id_page':
            #name = self.find_id_input_name.text()
            email = self.find_id_input_email.text()
            data = self.pack_data(command="FI", email=email)
            self.tcp.sendData(data)  

            loop = QEventLoop()
            self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
            loop.exec_()  # 응답이 올 때까지 여기서 대기

            if self.tcp.result == 0:
                QMessageBox.about(self, "아이디 찾기", f"아이디는 {self.tcp.data['id']}입니다.")
                self.stackedWidget.setCurrentWidget(self.login_page)
            else:
                QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
        else:
            id = self.id_check_input_id.text()
            email = self.id_check_input_email.text()
            data = self.pack_data(command="FI", id=id, email=email)
            self.tcp.sendData(data)  

            loop = QEventLoop()
            self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
            loop.exec_()  # 응답이 올 때까지 여기서 대기

            if self.tcp.result == 0:
                self.stackedWidget.setCurrentWidget(self.passwd_reset_page)
            else:
                QMessageBox.about(self, "아이디 찾기", "일치하는 정보가 없습니다.")
    
    def passwd_reset(self):
        id = self.id_check_input_id.text()
        email = self.id_check_input_email.text()

        new_passwd = self.passwd_reset_input_passwd.text()
        new_passwd_compare = self.passwd_reset_input_passwd_compare.text()

        if new_passwd == new_passwd_compare:
            self.cur.execute("UPDATE user set password = %s where login_id = %s and email = %s",(new_passwd,id,email) )
            self.db.commit()
            QMessageBox.about(self, "비밀번호 재설정", "변경이 완료되었습니다.")
            self.stackedWidget.setCurrentWidget(self.login_page)
        else:
            QMessageBox.warning(self, "비밀번호 재설정", "비밀번호가 일치하지 않습니다.")
    
    def pack_data(self, command, id=None,pw=None,name=None,email=None,data=None,content=None):
        packed_data = b''
        
        # 명령어 패킹 (길이 + 데이터)
        packed_data += struct.pack('I', len(command)) + command.encode('utf-8')
        
        # ID 패킹 (길이 + 데이터)
        if id is not None:
            packed_data += struct.pack('I', len(id)) + id.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 비밀번호 패킹 (길이 + 데이터)
        if pw is not None:
            packed_data += struct.pack('I', len(pw)) + pw.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이름 패킹 (길이 + 데이터)
        if name is not None:
            packed_data += struct.pack('I', len(name.encode('utf-8'))) + name.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이메일 패킹 (길이 + 데이터)
        if email is not None:
            packed_data += struct.pack('I', len(email)) + email.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 데이터 패킹
        if data is not None:
            data_bytes = data.encode('utf-8')
            packed_data += struct.pack('I', len(data_bytes)) + data_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        # 콘텐트 패킹
        if content is not None:
            content_bytes = content.encode('utf-8')
            packed_data += struct.pack('I', len(content_bytes)) + content_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        
        return packed_data
    
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

    def profile_save(self):
        client.close()
        self.profile_cnt += 1
        self.client_main.add_profile(self.profile_cnt)


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

        self.btn_profile1.setVisible(False)
        self.btn_profile2.setVisible(False)
        self.btn_profile3.setVisible(False)
        self.btn_profile4.setVisible(False)
        
        # 계정 생성 버튼 이벤트 연결
        self.btn_plus_profile.clicked.connect(self.plus_profile)

        self.btn_profile1.clicked.connect(self.move_main_page)
        self.btn_profile2.clicked.connect(self.move_main_page)
        self.btn_profile3.clicked.connect(self.move_main_page)
        self.btn_profile4.clicked.connect(self.move_main_page)
        
        #버튼 아이콘 설정
        self.btn_plus_profile.setIcon(QIcon("/home/sang/dev_ws/save_file/image_folder/plus.png"))  # 아이콘 설정
        self.btn_plus_profile.setIconSize(self.btn_plus_profile.sizeHint())  # 아이콘 크기를 버튼 크기의 절반으로 설정
        self.btn_plus_profile.setStyleSheet("""
        QPushButton {
            border: 2px solid #ccc;
            background-color: white;
        }
        """)

    # main pages 
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
    
    # login page
    def plus_profile(self):
        client.show()
        client.stackedWidget.setCurrentWidget(client.add_profile_page)
    
    def add_profile(self, profile_cnt):
        if profile_cnt == 1:
            self.btn_profile1.setVisible(True)
        if profile_cnt == 2:
            self.btn_profile2.setVisible(True)
        if profile_cnt == 3:
            self.btn_profile3.setVisible(True)
        if profile_cnt == 4:
            self.btn_profile4.setVisible(True)
        if profile_cnt == 4:
            self.btn_plus_profile.setEnabled(False)
    
    def move_main_page(self):
        self.stackedWidget_2.setCurrentWidget(self.big_main_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())
