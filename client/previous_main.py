# main_window.py
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from server.database import FAAdb
from network.udp_client import UdpClient
from network.packer import pack_data

import Controller.Hands as hands
import Controller.Detector as Detector
from View.ViewMain import ViewMain
from View.ViewModal import ViewModalPause, ViewModalExit

from PyQt5 import uic
from network.socket_client import Client
from auth_window import AuthWindow
from Record import RecordGraph
from ui.ui_setup import UISetupHelper
from handler.auth_handler import AuthHandler
from handler.workout_handler import WorkoutHandler

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
        
        UISetupHelper.profiles(self)
        UISetupHelper.buttons(self)
        UISetupHelper.button_stylers(self)
        self.displayScore()

        self.auth = AuthHandler(self)
        self.btn_profile1.clicked.connect(lambda: self.auth.login_user(self.label_profile1.text()))
        self.btn_profile2.clicked.connect(lambda: self.auth.login_user(self.label_profile2.text()))
        self.btn_profile3.clicked.connect(lambda: self.auth.login_user(self.label_profile3.text()))
        self.btn_profile4.clicked.connect(lambda: self.auth.login_user(self.label_profile4.text()))

        self.workout_handler = WorkoutHandler(self)
        self.btn_add_workout.clicked.connect(self.workout_handler.add_workout_to_table)
        self.btn_delete_workout.clicked.connect(self.workout_handler.delete_selected_workout)

    def displayScore(self):
        current_score = 4720
        max_score = 10000
        text = f"{current_score} / {max_score} (next tier)"
        self.lb_score.setText(text)
    def back2main(self):
        self.stackedWidget_big.setCurrentWidget(self.big_main_page)
        self.showNormal()

    def back2login(self):
        self.stackedWidget_big.setCurrentWidget(self.profile_page)

    def go2account(self):
        self.stackedWidget_big.setCurrentWidget(self.account_page)
        self.btn_back2main_2.clicked.connect(self.back_work_to_main)
        

    def go2calendar(self):
        self.stackedWidget_big.setCurrentWidget(self.calendar_page)
        self.btn_back2main.clicked.connect(self.back_work_to_main)

    # def go2workout(self):
    #     self.btn_work_to_main.clicked.connect(self.back_work_to_main)   # 운동 화면 → 메인 화면으로 돌아가기
    #     self.btn_save.clicked.connect(self.save_video)                  # Video save 명령버튼
        
    #     self.modal_exit_view = None
    #     self.modal_pause_view = None
    #     self.lb_cam.clear()
    #     QApplication.processEvents()

    #     # Page switch
    #     self.stackedWidget_big.setCurrentWidget(self.workout_page)
    #     self.showFullScreen()
    #     self.lookup_frame.hide()
    #     self.routine_frame.hide()
    #     self.lb_cam = self.workout_page.findChild(QLabel, "lb_cam")
    #     self.lb_cam.setScaledContents(True)
    
    #     # Camera 시작 
    #     self.camera = Camera()
    #     self.camera.start()

    #     self.timer = QTimer()
    #     self.timer.timeout.connect(self.update_gui)
    #     self.timer.start(30)
        
    #     # bttn View 구성 
    #     self.view = ViewMain()
    #     self.view.set_mode("main")
    #     self.view.set_button_action("start", self.handle_start)
    #     self.view.set_button_action("exit", self.handle_exit)
    #     self.view.set_button_action("lookup", self.handle_lookup)

    # def update_gui(self):
    #     if self.camera.frame is not None:
    #         frame_copy = self.camera.frame.copy()
    #         # 1. Mediapipe로 손 키포인트 추출
    #         frame = self.hand_detector.findHands(self.camera.frame, draw=False)
    #         lmList = self.hand_detector.findPosition(frame, draw=False)
    #         Detector.analyze_user(frame)

    #         hands.set()
    #         # 👆 손가락 제스처로 운동 선택
    #         if self.is_lookup:
    #             number = self.hand_detector.count_fingers(lmList)
    #             cv2.putText(frame, f' {number}', (cons.window_width - 100, 50),
    #                         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    #             if 1 <= number <= 5:
    #                 if self.current_gesture != number:
    #                     self.current_gesture = number
    #                     self.gesture_start_time = time.time()
    #                     self.selection_confirmed = False
    #                     print(f"⏳ 숫자 {number} 인식됨. 유지 중...")

    #                 elif not self.selection_confirmed and time.time() - self.gesture_start_time >= 3:
    #                     print(f"🎯 숫자 {number} 확정됨! 운동 시작.")
    #                     self.selection_confirmed = True
    #                     self.play_selected_workout(number, self.tier)

    #             else:
    #                 # 손가락이 0개이거나 범위 바깥이면 초기화
    #                 self.current_gesture = None
    #                 self.gesture_start_time = None
    #                 self.selection_confirmed = False

    #         # 2. 버튼 그리기
    #         if self.view:
    #             self.view.appear(frame)
    #         if self.modal_pause_view :
    #             self.modal_pause_view.appear(frame)
    #         if self.modal_exit_view is not None:
    #             self.modal_exit_view.appear(frame) 

    #         # 3. PyQt에 이미지 보여주기
    #         img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)

    #         self.lb_cam.setPixmap(QPixmap.fromImage(qt_img))
    #         if self.camera.is_active == True:
    #             self.udp.send_video(frame_copy)
    # Main 
    
    def show_main(self):
        self.stackedWidget_small.setCurrentWidget(self.main_page)
    def show_record(self):
        self.stackedWidget_small.setCurrentWidget(self.record_page)

        self.radio_day.setChecked(True)
        self.radio_day.toggled.connect(self.switch_radio)
        self.radio_week.toggled.connect(self.switch_radio)
        self.radio_month.toggled.connect(self.switch_radio)
   
    def switch_graph(self, new_graph):
        self.graph_container_layout.removeWidget(self.current_graph)
        self.current_graph.setParent(None)
        self.graph_container_layout.addWidget(new_graph)
        self.current_graph = new_graph

    def switch_radio(self):
        if self.radio_day.isChecked():
            self.switch_graph(self.graph_day)
            self.graph_day.set_mode("day")
        elif self.radio_week.isChecked():
            self.switch_graph(self.graph_week)
            self.graph_week.set_mode("week")
        elif self.radio_month.isChecked():
            self.switch_graph(self.graph_month)
            self.graph_month.set_mode("month")
    def show_rank(self):
        self.stackedWidget_small.setCurrentWidget(self.rank_page)

    # Account 
    def show_modify(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_modify)
    def show_goal(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_goal)
    def show_todayrecord(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_record)
    def show_config(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_config)
        
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
          
    def set_user_name(self,name):
        self.lb_name.setText(name)
    
    def on_item_click(self, item):
        # 클릭된 항목에 따라 재생할 비디오 경로 지정
        video_map = {
            "Front Lunge": "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
            "Side Lunge": "/home/sang/dev_ws/save_file/Asset/side-lunge.mp4",
            "Squat": "/home/sang/dev_ws/save_file/Asset/squat.mp4"
        }
        
        # 클릭된 항목의 텍스트를 가져와서 해당 비디오 경로로 비디오 재생
        video_path = video_map.get(item.text(), "")
        print(video_path)
        if video_path:
            self.play_workout_video(video_path)
    
    def play_workout_video(self, video_path):
        # 비디오 재생 코드 (예시로 출력만 합니다)
        print(f"Playing workout video: {video_path}")

    def back_work_to_main(self):
        if self.camera is not None:
            self.camera.stop()
        self.stackedWidget_big.setCurrentWidget(self.big_main_page)
        self.showNormal()

    # def play_selected_workout(self, index, tier):
    #     if tier == 0:
    #         videos = {
    #             1: "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
    #             2: "/home/sang/dev_ws/save_file/Asset/squat.mp4",
    #             3: "/home/sang/dev_ws/save_file/Asset/shoulder_press.mp4",
    #             4: "/home/sang/dev_ws/save_file/Asset/knee-up.mp4"
    #         }
    #     elif tier == 1:
    #         videos = {
    #             1: "/home/sang/dev_ws/save_file/Asset/push-up.mp4",
    #             2: "/home/sang/dev_ws/save_file/Asset/bridge.mp4",
    #             3: "/home/sang/dev_ws/save_file/Asset/standing-bicycle.mp4",
    #             4: "/home/sang/dev_ws/save_file/Asset/side-lunge.mp4"
    #         }
    #     elif tier == 2:
    #         videos = {
    #             1: "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
    #             2: "/home/sang/dev_ws/save_file/Asset/squat.mp4",
    #             3: "/home/sang/dev_ws/save_file/Asset/shoulder_press.mp4",
    #             4: "/home/sang/dev_ws/save_file/Asset/knee-up.mp4"
    #         }   
    #     if index in videos:
    #         self.play_workout_video(videos[index])
    #     else:
    #         print(f"❌ {index}번 운동은 정의되지 않았습니다.")

    # def play_workout_video(self, video_path):
    #     # 이전 재생 중이면 중단
    #     if self.video_thread and self.video_thread.isRunning():
    #         self.video_thread.stop()
    #         self.video_thread.wait()
        
    #     self.lb_cam.clear()
    #     self.timer.stop()

    #     self.video_thread = Video(video_path,self.lb_cam.size())
    #     self.video_thread.frame_ready.connect(self.display_video_frame)
    #     self.video_thread.finished.connect(self.resume_camera)
    #     self.video_thread.start()

    # def handle_start(self):
    #     print("🟢 START button tapped!")
    #     self.view.set_mode("working")
    #     self.lookup_frame.hide()
    #     self.Routine_frame.show()
    #     self.save_video()
    #     QApplication.processEvents()

    #     # Routine 조회 
    #     data = pack_data(command="GR", name=self.username)
    #     self.tcp.sendData(data)

    #     self.view.set_button_action("pause", self.handle_pause)
    #     self.view.set_button_action("next", self.handle_next)


    # def handle_exit(self):
    #     print("EXIT button tapped!")

    #     self.modal_exit_view = ViewModalExit()
    #     self.modal_exit_view.bttn_yes.action = self.handle_close_button
    #     self.modal_exit_view.bttn_no.action = self.handle_back_to_main

    # def handle_lookup(self):
    #     print(" Lookup button tapped!")
    #     # show workout list 
    #     self.total_work_list=[]
    #     bronze_work_list=['Front Lunge', 'Squat', 'Sholder-press', 'Knee-up']
    #     silver_work_list=['Push-up', 'Bridge', 'Standing Bicycle', 'Side lunge']
    #     gold_work_list=['Sit-up', 'Side-plank', 'One-leg-knee-up', 'V-up']

    #     self.tier_list=['BRONZE', 'SILVER', 'GOLD']
    #     self.total_work_list.append(bronze_work_list)
    #     self.total_work_list.append(silver_work_list)
    #     self.total_work_list.append(gold_work_list)

    #     self.is_lookup = True
    #     self.view.set_mode("lookup")
    #     # lookup btns
    #     self.routine_frame.hide()
    #     self.lookup_frame.show()
    #     self.workout_list.clear()
    #     self.label_tier.setText(self.tier_list[self.tier])
        
    #     for i in self.total_work_list[self.tier]:
    #         self.workout_list.addItem(i)
    #     self.workout_list.itemClicked.connect(self.on_item_click)

    #     self.view.set_button_action("next", self.handle_next)
    #     self.view.set_button_action("back", self.handle_back_to_main)

    # def handle_pause(self):
    #     print("⏸️ PAUSE button tapped!")

    #     self.modal_pause_view = ViewModalPause()
    #     self.modal_pause_view.bttn_back.action = self.handle_back_to_main
    #     self.modal_pause_view.bttn_continue.action = self.handle_continue_button

    # def handle_next(self):
    #     print("Next button tapped!")
    #     self.workout_list.clear()
    #     self.tier += 1
    #     if self.tier == 3:
    #         self.tier = 0
    #     self.view.tier = self.tier
    #     self.label_tier.setText(self.tier_list[self.tier])
    #     self.view.set_mode("lookup")
    #     for i in self.total_work_list[self.tier]:
    #         self.workout_list.addItem(i)
    #     self.workout_list.itemClicked.connect(self.on_item_click)

    #     self.view.set_button_action("next", self.handle_next)
    #     self.view.set_button_action("back", self.handle_back_to_main)

    # def handle_back_to_main(self):
    #     print("🔙 BACK button tapped!")
    #     # hide workout list 
    #     self.is_paused = False
    #     self.is_lookup = False
    #     self.modal_pause_view = None
    #     self.modal_exit_view = None
        
    #     self.view.set_mode("main")
    #     self.lookup_frame.hide()
    #     self.routine_frame.show()
    #     self.view.set_button_action("start",  self.handle_start)
    #     self.view.set_button_action("exit",   self.handle_exit)
    #     self.view.set_button_action("lookup", self.handle_lookup)

    # def handle_continue_button(self):
    #     print("▶️ CONTINUE button tapped!")
    #     self.modal_pause_view = None

    #     self.view.set_mode("working")
    #     self.lookup_frame.hide()
    #     self.routine_frame.show()
    #     self.view.set_button_action("pause", self.handle_pause)
    #     self.view.set_button_action("next", self.handle_next)

    # def handle_close_button(self):
    #     print("🔴 Close!")
    #     self.camera.stop()
    #     self.stackedWidget_big.setCurrentWidget(self.big_main_page)
    #     self.showNormal()

    # def display_video_frame(self, img):
    #     if isinstance(img, QImage):  # img가 QImage인 경우
    #         pixmap = QPixmap.fromImage(img)
    #     elif isinstance(img, QPixmap):  # img가 이미 QPixmap이면 변환 필요 없음
    #         pixmap = img
    #     else:
    #         print("❌ Error: img 타입이 QImage나 QPixmap이 아닙니다.")
    #         return

    #     self.lb_cam.setPixmap(pixmap)

    # def resume_camera(self):
    #     print("🎬 Video done. Switching back to camera.")
    #     self.lb_cam.clear()
    #     self.lb_cam.setPixmap(QPixmap())
    #     self.lb_cam.show()
    #     self.timer.start(30)

    def count(self):
        if self.tcp.result == 'up':
            self.count_up+=1
    # def save_video(self):
    #     self.udp.video_writer=True
    #     data=pack_data("RC",data='True')
    #     self.tcp.sendData(data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())