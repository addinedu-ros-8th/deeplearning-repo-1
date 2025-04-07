# auth_handler.py
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog
from network.packer import pack_data
from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QPixmap
import time


class AuthHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tcp = self.main_window.tcp
        self.cur = self.main_window.cur

    def login_user(self, name):
        input_passwd, ok = QInputDialog.getText(self.main_window, '계정 비밀번호', '비밀번호를 입력하세요:')

        if not ok or not input_passwd:
            QMessageBox.warning(self.main_window, "계정 비밀번호", "비밀번호를 입력해야 합니다.")
            return

        # TCP login request to server
        data = pack_data(command="LI", status='0', name=name, pw=input_passwd)
        self.tcp.sendData(data)

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)
        loop.exec_()
        self.tcp.responseReceived.disconnect(loop.quit)

        if self.tcp.result == 0:
            data = self.tcp.data

            user_id = data['id']
            tmp = data['list_data'].split(",")
            height = int(tmp[0])
            weight = int(tmp[1])
            tier = int(tmp[2])
            score = int(tmp[3])
            

            self.main_window.set_user_name(name, user_id, height, weight, tier, score)
            self.main_window.set_profile_icon(name)
            self.main_window.stackedWidget_big.setCurrentWidget(self.main_window.big_main_page)     # page 이동 

            # Routine 생성 요청 (서버가 routine 생성만)
            rr_data = pack_data(command="RR", name=name)
            self.tcp.sendData(rr_data)

            loop2 = QEventLoop()
            self.tcp.responseReceived.connect(loop2.quit)
            loop2.exec_()
            self.tcp.responseReceived.disconnect(loop2.quit)

            if self.tcp.result == 0:
                # self.routine_list = []  # 초기화
                routine_str = self.tcp.data['list_data']
                items = routine_str.split(',')
                for item in items:
                    try:
                        id, name, sets, reps = item.strip().split('|')
                        self.main_window.routine.append({
                            'id': id,
                            'name': name,
                            'sets': int(sets),
                            'reps': int(reps)
                        })
                    except ValueError:
                        print("⚠️ 잘못된 루틴 항목 포맷:", item)
                print(" 루틴 리스트:", self.main_window.routine)
        else:
            QMessageBox.warning(self.main_window, "로그인 실패", "로그인 정보가 틀렸습니다.")
