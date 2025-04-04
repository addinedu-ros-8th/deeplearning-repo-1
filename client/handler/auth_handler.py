# auth_handler.py
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QFileDialog
from network.packer import pack_data
from PyQt5.QtCore import QEventLoop
from PyQt5.QtGui import QPixmap


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

        # Check credentials locally first (optional)
        self.cur.execute("SELECT password FROM user WHERE name = %s and password = %s", (name, input_passwd))
        result = self.cur.fetchall()

        if not result:
            QMessageBox.warning(self.main_window, "계정 비밀번호", "비밀번호가 일치하지 않습니다.")
            return

        # TCP login request to server
        passwd = result[0][0]
        data = pack_data(command="LI", name=name, pw=passwd)
        self.tcp.sendData(data)

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)
        loop.exec_()

        if self.tcp.result == 0:
            print("로그인 성공")
            self.main_window.username = name
            self.main_window.set_user_name(name)
            self.main_window.set_profile_icon(name)
            # tier 가져오기 
            self.cur.execute("SELECT tier FROM user WHERE name = %s", (name,))
            tier_result = self.cur.fetchone()
            if tier_result: 
                self.main_window.tier = tier_result[0]
                self.main_window.set_user_tier(self.main_window.tier)
                print(f"user tier: {self.main_window.tier}")
            else: 
                print("user tier 없음")
  

            self.main_window.stackedWidget_big.setCurrentWidget(self.main_window.big_main_page)     # page 이동 
            # Routine 생성 요청 (서버가 routine 생성만)
            rr_data = pack_data(command="RR", name=name)
            self.tcp.sendData(rr_data)
        else:
            QMessageBox.warning(self.main_window, "로그인 실패", "로그인 정보가 틀렸습니다.")
