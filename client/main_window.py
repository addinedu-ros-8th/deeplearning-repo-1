
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from server.database import FAAdb
from network.udp_client import UdpClient
from network.packer import pack_data
from camera import Camera
from Video import Video

import Controller.Hands as hands
import Controller.Detector as Detector
from View.ViewMain import ViewMain
from View.ViewModal import ViewModalPause, ViewModalExit
import Constants as cons
import time, cv2
from PyQt5 import uic
from network.socket_client import Client
from auth_window import AuthWindow

main_class = uic.loadUiType("client/ui/real_real_main_page.ui")[0]
class MainWindow(QMainWindow, main_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.db = FAAdb()
        self.cur = self.db.conn.cursor()

        self.tcp = Client()
        self.udp = UdpClient()

        self.profile_cnt = 0
        self.is_lookup = False
        self.hand_detector = Detector.handDetector()
        self.modal_pause_view = None
        self.modal_exit_view = None
        self.video_thread = None
        
        self.current_gesture = None
        self.gesture_start_time = None
        
        self.selection_confirmed = False
        self.setup_profiles()
        self.setup_buttons()
        
    def setup_profiles(self):   # DB에서 프로필 불러오고 버튼 셋업
        self.count_up = 0
        self.tier=0
        
        # 프로필 계정 유무확인후 버튼 활성화
        self.cur.execute("select count(name) from user")
        # cnt = self.cur.fetchone()[0]  # ← fetchone()으로 처리
        cnt = self.cur.fetchall()
        cnt = int(cnt[0][0])
        
        self.cur.execute("select name,user_icon from user where name is not null")
        name = self.cur.fetchall()

        name_list=[]
        icon_list=[]
        if len(name) != 0:
            for n in name:
                name_list.append(n[0])
                icon_list.append(n[1])

        buttons = [self.btn_profile1, self.btn_profile2, self.btn_profile3, self.btn_profile4]
        labels = [self.label_profile1, self.label_profile2, self.label_profile3, self.label_profile4]
        
        # 모든 버튼과 라벨 숨기기
        for btn, label in zip(buttons, labels):
            btn.setVisible(False)
            label.setText("")

        if cnt == 0: return  # 프로필이 없을 경우 종료

        icon_size = 200  # 아이콘 크기 설정
        for i in range(cnt):
            pixmap = QPixmap()
            pixmap.loadFromData(icon_list[i])  # 바이너리 데이터를 QPixmap으로 변환
            
            buttons[i].setIcon(QIcon(pixmap))
            buttons[i].setIconSize(QSize(icon_size, icon_size))
            labels[i].setText(name_list[i])
            buttons[i].setVisible(True)
        self.profile_cnt = cnt
        self.btn_plus_profile.setEnabled(cnt < 4)


        # 버튼 아이콘 설정
        self.btn_plus_profile.setIcon(QIcon("/save_file/image_folder/plus.png"))  # 아이콘 설정
        self.btn_plus_profile.setIconSize(self.btn_plus_profile.sizeHint())  # 아이콘 크기를 버튼 크기의 절반으로 설정
        self.btn_plus_profile.setStyleSheet("""
        QPushButton {
            border: 2px solid #ccc;
            background-color: white;
        }
        """)

        # 계정 버튼 아이콘 설정
        self.btn_profile.setIcon(QIcon("/save_file/image_folder/profil_icon.png"))  # 아이콘 설정
        self.btn_profile.setIconSize(self.btn_plus_profile.sizeHint()*1.5)
        self.btn_profile.setStyleSheet("""
        QPushButton {
            border: 2px solid #ccc;
            background-color: white;
        }
        """)

    def setup_buttons(self): # 탭 버튼 이벤트 연결 및 기본 화면 설정
        # 탭 버튼들을 Toggle 가능하게 만들기
        self.btn_workout.setCheckable(True)
        self.btn_record.setCheckable(True)
        self.btn_rank.setCheckable(True)
        
        self.tab_group = QButtonGroup()
        self.tab_group.addButton(self.btn_workout)
        self.tab_group.addButton(self.btn_record)
        self.tab_group.addButton(self.btn_rank)
        self.tab_group.setExclusive(True)
        # 탭 페이지 전환 연결  
        self.btn_workout.clicked.connect(self.show_main)
        self.btn_record.clicked.connect(self.show_record)
        self.btn_rank.clicked.connect(self.show_rank)
        # 메인 → 운동 페이지 이동 버튼
        self.btn_start.clicked.connect(self.go2workout)
        
        # 기본 화면 설정 
        self.btn_workout.setChecked(True)
        self.stackedWidget_big.setCurrentWidget(self.profile_page)
        self.stackedWidget_small.setCurrentWidget(self.main_page)
        
        # 프로필 추가 버튼 연결 
        self.btn_plus_profile.clicked.connect(self.plus_profile)
        
        # 프로필 선택 버튼 이벤트 연결
        self.btn_profile1.clicked.connect(self.clicked_profile_1)
        self.btn_profile2.clicked.connect(self.clicked_profile_2)
        self.btn_profile3.clicked.connect(self.clicked_profile_3)
        self.btn_profile4.clicked.connect(self.clicked_profile_4)
        
        # 운동 화면 → 메인 화면으로 돌아가기
        self.btn_work_to_main.clicked.connect(self.back_work_to_main)
        #영상 저장 명령버튼
        self.btn_save.clicked.connect(self.save_video)
    

    def go2workout(self):
        self.modal_exit_view = None
        self.modal_pause_view = None
        self.lb_cam.clear()
        QApplication.processEvents()

        # Page switch
        self.stackedWidget_big.setCurrentWidget(self.workout_page)
        self.showFullScreen()
        self.lookup_frame.hide()
        self.lb_cam = self.workout_page.findChild(QLabel, "lb_cam")
        self.lb_cam.setScaledContents(True)
        
        # Hide widget which contains workout list 
        #self.workout_list_widget.hide()
        # 2. Video widget 
        # self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # self.video_widget = QVideoWidget()
        # self.video_player.setVideoOutput(self.video_widget)
        
        #self.workout_list.layout().addWidget(self.video_widget)
        # self.video_widget.hide()

        # Camera 시작 
        self.camera = Camera()
        self.camera.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(30)
        
        # bttn View 구성 
        self.view = ViewMain()
        self.view.set_mode("main")
        self.view.set_button_action("start", self.handle_start)
        self.view.set_button_action("exit", self.handle_exit)
        self.view.set_button_action("lookup", self.handle_lookup)

    def update_gui(self):
        if self.camera.frame is not None:
            frame_copy = self.camera.frame.copy()
            # 1. Mediapipe로 손 키포인트 추출
            frame = self.hand_detector.findHands(self.camera.frame, draw=False)
            lmList = self.hand_detector.findPosition(frame, draw=False)
            Detector.analyze_user(frame)

            hands.set()
            # 👆 손가락 제스처로 운동 선택
            if self.is_lookup:
                number = self.hand_detector.count_fingers(lmList)
                cv2.putText(frame, f' {number}', (cons.window_width - 100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                if 1 <= number <= 5:
                    if self.current_gesture != number:
                        self.current_gesture = number
                        self.gesture_start_time = time.time()
                        self.selection_confirmed = False
                        print(f"⏳ 숫자 {number} 인식됨. 유지 중...")

                    elif not self.selection_confirmed and time.time() - self.gesture_start_time >= 5:
                        print(f"🎯 숫자 {number} 확정됨! 운동 시작.")
                        self.selection_confirmed = True
                        self.play_selected_workout(number, self.tier)

                else:
                    # 손가락이 0개이거나 범위 바깥이면 초기화
                    self.current_gesture = None
                    self.gesture_start_time = None
                    self.selection_confirmed = False

            # 2. 버튼 그리기
            if self.view:
                self.view.appear(frame)
            if self.modal_pause_view :
                self.modal_pause_view.appear(frame)
            if self.modal_exit_view is not None:
                self.modal_exit_view.appear(frame) 

            # 3. PyQt에 이미지 보여주기
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)

            self.lb_cam.setPixmap(QPixmap.fromImage(qt_img))
            if self.camera.is_active == True:
                self.udp.send_video(frame_copy)

    def show_main(self):
        self.stackedWidget_small.setCurrentWidget(self.main_page)

    def show_record(self):
        self.stackedWidget_small.setCurrentWidget(self.record_page)

        self.radio_day.setChecked(True)
        self.radio_day.toggled.connect(self.switch_graph)
        self.radio_week.toggled.connect(self.switch_graph)
        self.radio_month.toggled.connect(self.switch_graph)    
    def switch_graph(self):
        if self.radio_day.isChecked():
            self.stackedGraphs.setCurrentIndex(0)
        elif self.radio_week.isChecked():
            self.stackedGraphs.setCurrentIndex(1)
        elif self.radio_month.isChecked():
            self.stackedGraphs.setCurrentIndex(2)
    def show_rank(self):
        self.stackedWidget_small.setCurrentWidget(self.rank_page)

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
        
    def clicked_profile_1(self):
        self.move_main_page(self.label_profile1.text())
    def clicked_profile_2(self):
        self.move_main_page(self.label_profile2.text())
    def clicked_profile_3(self):
        self.move_main_page(self.label_profile3.text())
    def clicked_profile_4(self):
        self.move_main_page(self.label_profile4.text())
        
    def move_main_page(self,name):
        input_passwd, ok = QInputDialog.getText(self, '계정 비밀번호', '비밀번호를 입력하세요 :')
    
        if not ok or not input_passwd:
            QMessageBox.warning(self, "계정 비밀번호", "비밀번호를 입력해야 합니다.")
            return
        
        self.cur.execute("SELECT password FROM user WHERE name = %s and password = %s", (name, input_passwd))
        result = self.cur.fetchall()
        
        if not result:
            QMessageBox.warning(self, "계정 비밀번호", "비밀번호가 일치하지 않습니다.")
            return
        
        passwd = result[0][0]
        data = pack_data(command="LI", name=name, pw=passwd)
        self.tcp.sendData(data)

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
        loop.exec_()
    
        if self.tcp.result == 0:
            print("로그인 성공")
            self.stackedWidget_big.setCurrentWidget(self.big_main_page)
            self.set_user_name(name)
        else:
            QMessageBox.warning(self, "계정 비밀번호", "로그인 정보가 틀렸습니다.")
    
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
        self.camera.stop()
        self.stackedWidget_big.setCurrentWidget(self.big_main_page)
        self.showNormal()

    def play_selected_workout(self, index, tier):
        if tier == 0:
            videos = {
                1: "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
                2: "/home/sang/dev_ws/save_file/Asset/squat.mp4",
                3: "/home/sang/dev_ws/save_file/Asset/shoulder_press.mp4",
                4: "/home/sang/dev_ws/save_file/Asset/knee-up.mp4"
            }
        elif tier == 1:
            videos = {
                1: "/home/sang/dev_ws/save_file/Asset/push-up.mp4",
                2: "/home/sang/dev_ws/save_file/Asset/bridge.mp4",
                3: "/home/sang/dev_ws/save_file/Asset/standing-bicycle.mp4",
                4: "/home/sang/dev_ws/save_file/Asset/side-lunge.mp4"
            }
        elif tier == 2:
            videos = {
                1: "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
                2: "/home/sang/dev_ws/save_file/Asset/squat.mp4",
                3: "/home/sang/dev_ws/save_file/Asset/shoulder_press.mp4",
                4: "/home/sang/dev_ws/save_file/Asset/knee-up.mp4"
            }   
        if index in videos:
            self.play_workout_video(videos[index])
        else:
            print(f"❌ {index}번 운동은 정의되지 않았습니다.")

    def play_workout_video(self, video_path):
        # 이전 재생 중이면 중단
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()

        self.lb_cam.clear()
        self.timer.stop()

        self.video_thread = Video(video_path,self.lb_cam.size())
        self.video_thread.frame_ready.connect(self.display_video_frame)
        self.video_thread.finished.connect(self.resume_camera)
        self.video_thread.start()

    def handle_start(self):
        print("🟢 START button tapped!")
        self.view.set_mode("working")
        self.lookup_frame.hide()
        self.save_video()
        QApplication.processEvents()
        self.view.set_button_action("pause", self.handle_pause)
        self.view.set_button_action("next", self.handle_next)

    def handle_exit(self):
        print("EXIT button tapped!")

        self.modal_exit_view = ViewModalExit()
        self.modal_exit_view.bttn_yes.action = self.handle_close_button
        self.modal_exit_view.bttn_no.action = self.handle_back_to_main

    def handle_lookup(self):
        print(" Lookup button tapped!")
        # show workout list 
        self.total_work_list=[]
        bronze_work_list=['Front Lunge', 'Squat', 'Sholder-press', 'Knee-up']
        silver_work_list=['Push-up', 'Bridge', 'Standing Bicycle', 'Side lunge']
        gold_work_list=['Sit-up', 'Side-plank', 'One-leg-knee-up', 'V-up']

        self.tier_list=['BRONZE', 'SILVER', 'GOLD']
        self.total_work_list.append(bronze_work_list)
        self.total_work_list.append(silver_work_list)
        self.total_work_list.append(gold_work_list)

        self.mode = "lookup"
        self.is_lookup = True
        self.view.set_mode("lookup")
        # lookup btns
        self.lookup_frame.show()
        self.workout_list.clear()
        self.label_tier.setText(self.tier_list[self.tier])
        
        for i in self.total_work_list[self.tier]:
            self.workout_list.addItem(i)
        self.workout_list.itemClicked.connect(self.on_item_click)

        self.view.set_button_action("next", self.handle_next)
        self.view.set_button_action("back", self.handle_back_to_main)

    def handle_pause(self):
        print("⏸️ PAUSE button tapped!")

        self.modal_pause_view = ViewModalPause()
        self.modal_pause_view.bttn_back.action = self.handle_back_to_main
        self.modal_pause_view.bttn_continue.action = self.handle_continue_button

    def handle_next(self):
        print("Next button tapped!")
        self.workout_list.clear()
        self.tier += 1
        if self.tier == 3:
            self.tier = 0
        self.view.tier = self.tier
        self.label_tier.setText(self.tier_list[self.tier])
        self.view.set_mode("lookup")
        for i in self.total_work_list[self.tier]:
            self.workout_list.addItem(i)
        self.workout_list.itemClicked.connect(self.on_item_click)

        self.view.set_button_action("next", self.handle_next)
        self.view.set_button_action("back", self.handle_back_to_main)

    def handle_back_to_main(self):
        print("🔙 BACK button tapped!")
        # hide workout list 
        #self.workout_list_widget.hide()
        self.is_paused = False
        self.is_lookup = False
        self.modal_pause_view = None
        self.modal_exit_view = None
        
        self.view.set_mode("main")
        self.lookup_frame.hide()
        self.view.set_button_action("start",  self.handle_start)
        self.view.set_button_action("exit",   self.handle_exit)
        self.view.set_button_action("lookup", self.handle_lookup)


    def handle_continue_button(self):
        print("▶️ CONTINUE button tapped!")
        self.modal_pause_view = None

        self.view.set_mode("working")
        self.lookup_frame.hide()
        self.view.set_button_action("pause", self.handle_pause)
        self.view.set_button_action("next", self.handle_next)

    def handle_close_button(self):
        print("🔴 Close!")
        self.camera.stop()
        self.stackedWidget_big.setCurrentWidget(self.big_main_page)
        self.showNormal()

        # self.close()

    def handle_show(self):
        print("show button tapped! ")
        """
        Need to implement 
        """
    def display_video_frame(self, img):
        if isinstance(img, QImage):  # img가 QImage인 경우
            pixmap = QPixmap.fromImage(img)
        elif isinstance(img, QPixmap):  # img가 이미 QPixmap이면 변환 필요 없음
            pixmap = img
        else:
            print("❌ Error: img 타입이 QImage나 QPixmap이 아닙니다.")
            return

        self.lb_cam.setPixmap(pixmap)

    def resume_camera(self):
        print("🎬 Video done. Switching back to camera.")
        self.lb_cam.clear()
        self.lb_cam.setPixmap(QPixmap())
        self.lb_cam.show()
        self.timer.start(30)

    def count(self):
        if client.tcp.result == 'up':
            #print(self.tcp.result)
            self.count_up+=1
    def save_video(self):
        self.udp.video_writer=True
        data=self.pack_data("RC",data='True')
        self.tcp.sendData(data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())