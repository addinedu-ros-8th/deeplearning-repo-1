# main_window.py
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from auth_window import AuthWindow
from server.database import FAAdb
from network.udp_client import UdpClient
from network.socket_client import Client
from ui.ui_setup import UISetupHelper
from handler.auth_handler import AuthHandler
from handler.workout_handler import WorkoutHandler
from handler.record_handler import RecordHandler
import Controller.Detector as Detector
import Constants as cons 
main_class = uic.loadUiType("client/ui/main_page.ui")[0]
class MainWindow(QMainWindow, main_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.db = FAAdb()
        self.cur = self.db.conn.cursor()

        self.tcp = Client()
        self.udp = UdpClient()
        self.camera = None
        self.profile_cnt = 0
        self.is_lookup = False
        self.hand_detector = Detector.handDetector()
        self.modal_pause_view = None
        self.modal_exit_view = None
        self.video_thread = None
        self.current_gesture = None
        self.gesture_start_time = None
        self.selection_confirmed = False
        
        self.auth = AuthHandler(self)
        self.btn_profile1.clicked.connect(lambda: self.auth.login_user(self.label_profile1.text()))
        self.btn_profile2.clicked.connect(lambda: self.auth.login_user(self.label_profile2.text()))
        self.btn_profile3.clicked.connect(lambda: self.auth.login_user(self.label_profile3.text()))
        self.btn_profile4.clicked.connect(lambda: self.auth.login_user(self.label_profile4.text()))

        self.workout_handler = WorkoutHandler(self)
        self.btn_add_workout.clicked.connect(self.workout_handler.add_workout_to_table)
        self.btn_delete_workout.clicked.connect(self.workout_handler.delete_selected_workout)

        self.record_handler = RecordHandler(self)
        
        UISetupHelper.profiles(self)
        UISetupHelper.buttons(self)
        UISetupHelper.button_stylers(self)
        self.displayScore()
    # Login
    def plus_profile(self):
        self.second=AuthWindow()
        self.second.show()
        self.second.stackedWidget.setCurrentWidget(self.second.add_profile_page)
    def add_profile(self, profile_cnt):
        self.db.conn.reconnect(attempts=3, delay=2) #db 새로고침
        print(profile_cnt)
        self.cur.execute("SELECT user_icon, name FROM user WHERE name IS NOT NULL")
        profiles = self.cur.fetchall()
        
        profile_buttons = [
            (self.btn_profile1, self.label_profile1),
            (self.btn_profile2, self.label_profile2),
            (self.btn_profile3, self.label_profile3),
            (self.btn_profile4, self.label_profile4)
        ]
        icon_size = 200  # 버튼 크기 설정
        
        for i in range(min(profile_cnt, len(profiles))):
            user_icon, name = profiles[i]
            pixmap = QPixmap()
            pixmap.loadFromData(user_icon)  # 바이너리 데이터를 QPixmap으로 변환
            
            btn, label = profile_buttons[i]
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(icon_size, icon_size))
            label.setText(name)
            btn.setVisible(True)

        self.btn_plus_profile.setEnabled(profile_cnt < 4)

    # Main
    def set_user_name(self,name):
        self.lb_name.setText(name)
        self.lb_name_2.setText(name)        # account name 
    def back2login(self):
        self.stackedWidget_big.setCurrentWidget(self.profile_page)
    def go2account(self):
        self.stackedWidget_big.setCurrentWidget(self.account_page)
        
    def show_main(self):
        self.stackedWidget_small.setCurrentWidget(self.main_page)
    def show_record(self):
        self.stackedWidget_small.setCurrentWidget(self.record_page)
    def show_rank(self):
        self.stackedWidget_small.setCurrentWidget(self.rank_page)
    def displayScore(self):
        current_score = 4720
        max_score = 10000
        text = f"{current_score} / {max_score} (next tier)"
        self.lb_score.setText(text)
    def go2calendar(self):
        self.stackedWidget_big.setCurrentWidget(self.calendar_page)

    
    # Workout 
    def back2main(self):
        if self.camera is not None:
            self.camera.stop()
        self.stackedWidget_big.setCurrentWidget(self.big_main_page)
        self.showNormal()

    # Account 
    def show_modify(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_modify)
    def show_goal(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_goal)
    def show_todayrecord(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_record)
    def show_config(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_config)
    def set_user_tier(self,tier):
        tier_icon_path = cons.TIER_ICONS.get(tier)
        if tier_icon_path: 
            self.lb_tier.setPixmap(QPixmap(tier_icon_path))
            self.lb_tier.setScaledContents(True)
        else:
            print(f"[DEBUG] 티어 아이콘 경로가 잘못되었거나 존재하지 않음: {tier_icon_path}")

            
    # def on_item_click(self, item):
    #     # 클릭된 항목에 따라 재생할 비디오 경로 지정
    #     video_map = {
    #         "Front Lunge": "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
    #         "Side Lunge": "/home/sang/dev_ws/save_file/Asset/side-lunge.mp4",
    #         "Squat": "/home/sang/dev_ws/save_file/Asset/squat.mp4"
    #     }
        
    #     # 클릭된 항목의 텍스트를 가져와서 해당 비디오 경로로 비디오 재생
    #     video_path = video_map.get(item.text(), "")
    #     print(video_path)
    #     if video_path:
    #         self.play_workout_video(video_path)
    
    # def play_workout_video(self, video_path):
    #     # 비디오 재생 코드 (예시로 출력만 합니다)
    #     print(f"Playing workout video: {video_path}")

    def count(self):
        if self.tcp.result == 'up':
            self.count_up+=1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())