import sys
import os
import cv2
import time 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from Camera import Camera
from Video import Video
import Controller.Hands as hands
import Controller.Detector as Detector


from View.ViewModal import ViewModalPause,ViewModalExit
from View.ViewMain import ViewMain
import Constants as cons

from_class = uic.loadUiType("./Ui/main_page.ui")[0]

class MainWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Fitness AI App")
        
        self.is_lookup = False
        self.hand_detector = Detector.handDetector()
        self.modal_pause_view = None
        self.modal_exit_view = None
        self.video_thread = None
        
        self.current_gesture = None
        self.gesture_start_time = None
        self.selection_confirmed = False
        
        self.tiers = cons.TIERS  # ["Bronze", "Silver", "Gold"]
        self.tier_names = list(self.tiers.keys())
        self.current_tier_index = 0

        self.workout_buttons = [
            self.btn_workout_1,
            self.btn_workout_2,
            self.btn_workout_3,
            self.btn_workout_4,
        ] 
    
        # Gui btn
        self.btn_workout.setCheckable(True)
        self.btn_record.setCheckable(True)
        self.btn_rank.setCheckable(True)

        self.tab_group = QButtonGroup()
        self.tab_group.addButton(self.btn_workout)
        self.tab_group.addButton(self.btn_record)
        self.tab_group.addButton(self.btn_rank)
        self.tab_group.setExclusive(True)

        self.btn_workout.clicked.connect(self.page_main)
        self.btn_record.clicked.connect(self.page_record)
        self.btn_rank.clicked.connect(self.page_rank)
        self.btn_start.clicked.connect(self.go2workout)

        self.btn_workout.setChecked(True)
        self.stackedWidget_small.setCurrentWidget(self.main_page)
        
    def page_main(self):
        self.stackedWidget_small.setCurrentWidget(self.main_page)
    
    def page_record(self):
        self.stackedWidget_small.setCurrentWidget(self.record_page)
        self.radio_day.setChecked(True)
        self.radio_day.toggled.connect(self.switch_page)
        self.radio_week.toggled.connect(self.switch_page)
        self.radio_month.toggled.connect(self.switch_page)

    def page_rank(self):
        self.stackedWidget_small.setCurrentWidget(self.rank_page)

    def switch_page(self):
        if self.radio_day.isChecked():
            self.stackedGraphs.setCurrentIndex(0)
        elif self.radio_week.isChecked():
            self.stackedGraphs.setCurrentIndex(1)
        elif self.radio_month.isChecked():
            self.stackedGraphs.setCurrentIndex(2)

    def go2workout(self):
        self.modal_exit_view = None
        self.modal_pause_view = None
        self.lb_cam.clear()
        QApplication.processEvents()
        
        # 1. Page switch 
        self.stackedWidget_big.setCurrentWidget(self.page_workout)
        self.lb_cam = self.page_workout.findChild(QLabel, "lb_cam")
        self.lb_cam.setScaledContents(True)
        
        # Hide widget which contains workout list 
        self.workout_list_widget.hide()
        # 2. Video widget 
        self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.video_player.setVideoOutput(self.video_widget)
        
        self.workout_list.layout().addWidget(self.video_widget)
        self.video_widget.hide()
        # self.showMaximized()
        # self.lb_cam.setGeometry(0, 0, self.width(), self.height())

        # 3. Camera 시작 
        self.camera = Camera()
        self.camera.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(30)
        
        # 4. bttn View 구성 
        self.view = ViewMain()
        self.view.set_mode("main")
        self.view.set_button_action("start", self.handle_start)
        self.view.set_button_action("exit", self.handle_exit)
        self.view.set_button_action("lookup", self.handle_lookup)
        self.update_workout_buttons() # default = Bronze

        # lookup btns
        self.workout_group = QButtonGroup()
        self.workout_group.addButton(self.btn_workout_1)
        self.workout_group.addButton(self.btn_workout_2)
        self.workout_group.addButton(self.btn_workout_3)
        self.workout_group.addButton(self.btn_workout_4)
        self.workout_group.setExclusive(True)

        # self.btn_workout_1.clicked.connect(lambda: self.play_workout_video("./Asset/front-lunge.mp4"))
        # self.btn_workout_2.clicked.connect(lambda: self.play_workout_video("./Asset/side-lunge.mp4"))
        # self.btn_workout_3.clicked.connect(lambda: self.play_workout_video("./Asset/squat.mp4"))
        # self.btn_workout_4.clicked.connect(lambda: self.play_workout_video("./Asset/squat.mp4"))

    # def play_selected_workout(self, index):
    #     videos = {
    #         1: "./Asset/front-lunge.mp4",
    #         2: "./Asset/side-lunge.mp4",
    #         3: "./Asset/squat.mp4"
    #     }
    #     if index in videos:
    #         self.play_workout_video(videos[index])
    #     else:
    #         print(f"❌ {index}번 운동은 정의되지 않았습니다.")

    def play_workout_video(self, video_path):
        # 이전 재생 중이면 중단
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()

        self.lb_cam.clear()
        self.lb_cam.hide()
        self.timer.stop()

        self.video_thread = Video(video_path)
        self.video_thread.frame_ready.connect(self.display_video_frame)
        self.video_thread.finished.connect(self.resume_camera)
        self.video_thread.start()

    def display_video_frame(self, img):
        self.lb_cam.setPixmap(QPixmap.fromImage(img))
        self.lb_cam.show()

    def resume_camera(self):
        print("🎬 Video done. Switching back to camera.")
        self.lb_cam.clear()
        self.lb_cam.setPixmap(QPixmap())
        self.lb_cam.show()
        self.timer.start(30)

    def update_gui(self):
        if self.camera.frame is not None:
            frame = self.camera.frame.copy()
            # 1. Mediapipe로 손 키포인트 추출
            frame = self.hand_detector.findHands(frame, draw=False)
            lmList = self.hand_detector.findPosition(frame, draw=False)
            Detector.analyze_user(frame)

            hands.set()
            # 👆 손가락 제스처로 운동 선택
            if self.is_lookup:
                number = self.hand_detector.count_fingers(lmList)
                cv2.putText(frame, f' {number}', (cons.window_width - 100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                if 1 <= number <= 4:
                    if self.current_gesture != number:
                        self.current_gesture = number
                        self.gesture_start_time = time.time()
                        self.selection_confirmed = False
                        print(f"⏳ 숫자 {number} 인식됨. 유지 중...")

                    elif not self.selection_confirmed and time.time() - self.gesture_start_time >= 5:
                        print(f"🎯 숫자 {number} 확정됨! 운동 시작.")
                        self.selection_confirmed = True
                        self.play_selected_workout(number)

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
    
    def update_workout_buttons(self):
        tier_name = self.tier_names[self.current_tier_index]
        print(f"🔄 현재 티어: {tier_name}")

        # 버튼 텍스트 변경
        if self.view and "next" in self.view.buttons:
            self.view.buttons["next"].label.text = self.tier_names[(self.current_tier_index + 1) % len(self.tier_names)].upper()

        workouts = self.tiers[tier_name]

        for i, btn in enumerate(self.workout_buttons, start=1):
            if i in workouts:
                btn.setText(workouts[i]["name"])
                # QApplication.processEvents()
                btn.repaint()
                try:
                    btn.clicked.disconnect()
                except TypeError:
                    pass

                # 핵심: i=i 로 캡처
                btn.clicked.connect(lambda _, i=i: self.play_workout_video(workouts[i]["video"]))

    def handle_start(self):
        print("🟢 START button tapped!")
        self.view.set_mode("working")
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
        self.workout_list_widget.show()

        self.mode = "lookup"
        self.is_lookup = True
        self.view.set_mode("lookup")

        self.view.set_button_action("back", self.handle_back_to_main)
        self.view.set_button_action("next", self.handle_next) 
        self.update_workout_buttons()
    def handle_pause(self):
        print("⏸️ PAUSE button tapped!")

        self.modal_pause_view = ViewModalPause()
        self.modal_pause_view.bttn_back.action = self.handle_back_to_main
        self.modal_pause_view.bttn_continue.action = self.handle_continue_button

    def handle_next(self):
        print("🔁 Next Tier")

        self.current_tier_index = (self.current_tier_index + 1) % len(self.tier_names)
        tier_name = self.tier_names[self.current_tier_index]

        if "next" in self.view.buttons:
            next_tier_name = self.tier_names[(self.current_tier_index + 1) % len(self.tier_names)]
            self.view.buttons["next"].label.text = next_tier_name.upper()

        self.update_workout_buttons()


    def handle_back_to_main(self):
        print("🔙 BACK button tapped!")
        # hide workout list 
        self.workout_list_widget.hide()
        self.is_paused = False
        self.is_lookup = False
        self.modal_pause_view = None
        self.modal_exit_view = None
        
        self.view.set_mode("main")
        self.view.set_button_action("start",  self.handle_start)
        self.view.set_button_action("exit",   self.handle_exit)
        self.view.set_button_action("lookup", self.handle_lookup)


    def handle_continue_button(self):
        print("▶️ CONTINUE button tapped!")
        self.modal_pause_view = None

        self.view.set_mode("working")
        self.view.set_button_action("pause", self.handle_pause)
        self.view.set_button_action("next", self.handle_next)

    def handle_close_button(self):
        print("🔴 Close!")
        self.camera.stop()
        self.stackedWidget_big.setCurrentWidget(self.page)
        # self.close()

    def handle_show(self):
        print("show button tapped! ")
        """
        Need to implement 
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())