# workout_handler.py

import time, cv2
from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMessageBox, QTableWidgetItem
import Controller.Hands as hands
import Controller.Detector as Detector
from View.ViewMain import ViewMain
from View.ViewModal import ViewModalPause, ViewModalExit
from Video import Video
from network.packer import pack_data
from camera import Camera
import Constants as cons

class WorkoutHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.cur = self.main_window.cur
        self.db = self.main_window.db
        
    def add_workout_to_table(self):
        workout = self.main_window.workout_text.text().strip()
        tier = self.main_window.combo_tier.currentText()

        if not workout:
            QMessageBox.warning(self.main_window, "입력오류", "운동 이름을 입력해주세요.")
            return 

        try: 
            self.cur.execute(
                "INSERT INTO workout (workout_name, tier, reps) VALUES (%s, %s, %s)",
                (workout, tier, 20)
            )
            self.db.commit()
        except Exception as e:
            QMessageBox.critical(self.main_window, "DB 오류", f"운동 추가 중 오류 발생: {e}")
            return

        row_position = self.main_window.tableWidget.rowCount()
        self.main_window.tableWidget.insertRow(row_position)
        self.main_window.tableWidget.setItem(row_position, 0, QTableWidgetItem(workout))
        self.main_window.tableWidget.setItem(row_position, 1, QTableWidgetItem(tier))

        self.main_window.workout_text.clear()
        self.main_window.combo_tier.setCurrentIndex(0)

    def delete_selected_workout(self):
        row = self.main_window.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(self.main_window, "선택 오류", "삭제할 운동을 선택해주세요.")
            return

        workout_item = self.main_window.tableWidget.item(row, 0)
        if workout_item is None:
            QMessageBox.warning(self.main_window, "삭제 오류", "유효한 운동이 아닙니다.")
            return

        workout = workout_item.text()

        try:
            self.cur.execute("DELETE FROM workout WHERE workout_name = %s", (workout,))
            self.db.commit()
        except Exception as e:
            QMessageBox.critical(self.main_window, "DB 오류", f"운동 삭제 중 오류 발생: {e}")
            return

        self.main_window.tableWidget.removeRow(row)
        
    def load_user_routine(self):
        self.cur.execute("SELECT workout_name FROM routine WHERE username = %s ORDER BY idx ASC", (self.main_window.username,))
        rows = self.cur.fetchall()
        self.routine = [row[0] for row in rows]
        self.current_index = 0

    @staticmethod
    def go2workout(main_window):
        main_window.modal_exit_view = None
        main_window.modal_pause_view = None
        main_window.lb_cam.clear()
        QApplication.processEvents()

        main_window.stackedWidget_big.setCurrentWidget(main_window.workout_page)
        main_window.showFullScreen()
        main_window.routine_frame.hide()
        main_window.lookup_frame.hide()
        main_window.routine_frame.hide()
        main_window.lb_cam = main_window.workout_page.findChild(QLabel, "lb_cam")
        main_window.lb_cam.setScaledContents(True)

        main_window.camera = Camera()
        main_window.camera.start()

        main_window.timer = QTimer()
        main_window.timer.timeout.connect(lambda: WorkoutHandler.update_gui(main_window))
        main_window.timer.start(30)
        # call routine 
        data = pack_data(command="GR", name=main_window.username)
        main_window.tcp.sendData(data)
        main_window.tcp.responseReceived.connect(lambda: WorkoutHandler.on_routine_ready(main_window))

        
        main_window.view = ViewMain()
        main_window.view.set_mode("main")
        main_window.view.set_button_action("start", lambda: WorkoutHandler.handle_start(main_window))
        main_window.view.set_button_action("exit", lambda: WorkoutHandler.handle_exit(main_window))
        main_window.view.set_button_action("lookup", lambda: WorkoutHandler.handle_lookup(main_window))

    @staticmethod
    def update_gui(main_window):
        if main_window.camera.frame is not None:
            frame_copy = main_window.camera.frame.copy()
            frame = main_window.hand_detector.findHands(main_window.camera.frame, draw=False)
            lmList = main_window.hand_detector.findPosition(frame, draw=False)
            Detector.analyze_user(frame)
            hands.set()
            if main_window.is_workout:
                print(main_window.tcp.landmark)
                if isinstance(main_window.tcp.landmark, dict) and main_window.tcp.landmark.get("command") == "PI":
                    pi_data = main_window.tcp.landmark

                    # origin
                    ox, oy = pi_data['origin']['x'], pi_data['origin']['y']
                    cv2.circle(frame, (ox, oy), 10, (0, 255, 255), -1)  # 노란 원

                    # vector
                    vx, vy = pi_data['vector']['x'], pi_data['vector']['y']
                    cv2.arrowedLine(frame, (ox, oy), (vx, vy), (255, 0, 255), 3)  # 보라색 벡터 선

                    # landmarks
                    for pt in pi_data['landmarks']:
                        lx, ly = pt['x'], pt['y']
                        cv2.circle(frame, (lx, ly), 6, (0, 100, 255), -1)  # 주황색 점
                # 시간 갱신 
                    cv2.putText(frame, f"Count: {pi_data['count']}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                
                if main_window.remaining_time > 0:
                    current_time = time.time()
                    elapsed = current_time - main_window.last_tick_time

                    if elapsed >= 1 :
                        main_window.remaining_time -= 1
                        main_window.last_tick_time = current_time
                cv2.putText(frame, f"{main_window.remaining_time}", (cons.window_width - 250, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                if main_window.remaining_time <= 0:
                    main_window.is_workout = False
                    """
                        다음 운동 
                    """
                    # cv2.putText(frame, "✔ 운동 완료!", (cons.window_width - 100, 50),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 0), 3)

            elif main_window.is_lookup:
                number = main_window.hand_detector.count_fingers(lmList)
                cv2.putText(frame, f' {number}', (cons.window_width - 100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                if 1 <= number <= 5:
                    if main_window.current_gesture != number:
                        main_window.current_gesture = number
                        main_window.gesture_start_time = time.time()
                        main_window.selection_confirmed = False
                        print(f"⏳ 숫자 {number} 인식됨. 유지 중...")
                    elif not main_window.selection_confirmed and time.time() - main_window.gesture_start_time >= 3:
                        print(f"🎯 숫자 {number} 확정됨! 운동 시작.")
                        main_window.selection_confirmed = True
                        WorkoutHandler.play_selected_workout(main_window, number, main_window.tier)
                else:
                    main_window.current_gesture = None
                    main_window.gesture_start_time = None
                    main_window.selection_confirmed = False

            

            if main_window.view:
                main_window.view.appear(frame)
            if main_window.modal_pause_view:
                main_window.modal_pause_view.appear(frame)
            if main_window.modal_exit_view:
                main_window.modal_exit_view.appear(frame)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            main_window.lb_cam.setPixmap(QPixmap.fromImage(qt_img))
            if main_window.camera.is_active:
                main_window.udp.send_video(frame_copy)

    @staticmethod
    def play_selected_workout(main_window, index, tier):
        if index in cons.videos[tier]:
            WorkoutHandler.play_workout_video(main_window, cons.videos[tier][index])

    @staticmethod
    def play_workout_video(main_window, video_path):
        if main_window.video_thread and main_window.video_thread.isRunning():
            main_window.video_thread.stop()
            main_window.video_thread.wait()

        main_window.lb_cam.clear()
        main_window.timer.stop()

        main_window.video_thread = Video(video_path, main_window.lb_cam.size())
        main_window.video_thread.frame_ready.connect(lambda img: WorkoutHandler.display_video_frame(main_window, img))
        main_window.video_thread.finished.connect(lambda: WorkoutHandler.resume_camera(main_window))
        main_window.video_thread.start()

    @staticmethod
    def display_video_frame(main_window, img):
        if isinstance(img, QImage):
            pixmap = QPixmap.fromImage(img)
        elif isinstance(img, QPixmap):
            pixmap = img
        else:
            print("Error: img 타입이 QImage나 QPixmap이 아닙니다.")
            return
        main_window.lb_cam.setPixmap(pixmap)

    @staticmethod
    def resume_camera(main_window):
        print("Video done. Switching back to camera.")
        main_window.lb_cam.clear()
        main_window.lb_cam.setPixmap(QPixmap())
        main_window.lb_cam.show()
        main_window.timer.start(30)

    @staticmethod
    def save_video(main_window):
        main_window.udp.video_writer = True
        data = pack_data("RC", data='True')
        main_window.tcp.sendData(data)
    @staticmethod
    def handle_start(main_window):
        print("START button tapped!")
        main_window.view.set_mode("working")
        main_window.lookup_frame.hide()
        main_window.routine_frame.show()
        print(main_window.lb_cam.size())
        WorkoutHandler.save_video(main_window)
        QApplication.processEvents()
        """
            routine 부르기
        """


        main_window.remaining_time = cons.TIER_TIMES.get(main_window.tier, 80)
        main_window.last_tick_time = time.time()
        main_window.is_workout = True


        main_window.view.set_button_action("pause", lambda: WorkoutHandler.handle_pause(main_window))
        main_window.view.set_button_action("next", lambda: WorkoutHandler.handle_next(main_window))
    @staticmethod
    def on_routine_ready(main_window):
        # GR에 대한 응답인지 확인
        if main_window.tcp.data["command"] != "GR":
            return
        
        print("✅ 루틴 수신 완료, workout 시작 준비")
        main_window.routine_queue = main_window.tcp.routine_list.copy()
        main_window.current_index = 0
        main_window.set_current_workout()
        main_window.display_routine_list()
        # 이 연결은 한 번만 실행되도록 제거해주면 좋음
        try:
            main_window.tcp.responseReceived.disconnect()
        except Exception as e:
            print("disconnect 실패:", e)

    @staticmethod
    def handle_exit(main_window):
        print("EXIT button tapped!")
        main_window.modal_exit_view = ViewModalExit()
        main_window.modal_exit_view.bttn_yes.action = lambda: WorkoutHandler.handle_close_button(main_window)
        main_window.modal_exit_view.bttn_no.action = lambda: WorkoutHandler.handle_back_to_main(main_window)

    @staticmethod
    def handle_lookup(main_window):
        print("Lookup button tapped!")
        main_window.total_work_list = [
            ['Front Lunge', 'Squat', 'Sholder-press', 'Knee-up'],
            ['Push-up', 'Bridge', 'Standing Bicycle', 'Side lunge'],
            ['Sit-up', 'Side-plank', 'One-leg-knee-up', 'V-up']
        ]
        main_window.tier_list = ['BRONZE', 'SILVER', 'GOLD']

        main_window.is_lookup = True
        main_window.view.set_mode("lookup")
        main_window.routine_frame.hide()
        main_window.lookup_frame.show()
        main_window.workout_list.clear()
        main_window.label_tier.setText(main_window.tier_list[main_window.tier])

        for i in main_window.total_work_list[main_window.tier]:
            main_window.workout_list.addItem(i)
        # main_window.workout_list.itemClicked.connect(main_window.on_item_click)

        main_window.view.set_button_action("next", lambda: WorkoutHandler.handle_next(main_window))
        main_window.view.set_button_action("back", lambda: WorkoutHandler.handle_back_to_main(main_window))

    @staticmethod
    def handle_pause(main_window):
        print("⏸️ PAUSE button tapped!")
        data=pack_data("RC",data='False')
        main_window.tcp.sendData(data)
        main_window.modal_pause_view = ViewModalPause()
        main_window.modal_pause_view.bttn_back.action = lambda: WorkoutHandler.handle_back_to_main(main_window)
        main_window.modal_pause_view.bttn_continue.action = lambda: WorkoutHandler.handle_continue_button(main_window)

    @staticmethod
    def handle_next(main_window):
        print("Next button tapped!")
        main_window.is_ready = True 
        # main_window.workout_list.clear()
        # main_window.tier = (main_window.tier + 1) % 3
        # main_window.view.tier = main_window.tier
        # main_window.label_tier.setText(main_window.tier_list[main_window.tier])

        # main_window.view.set_mode("lookup")
        # for i in main_window.total_work_list[main_window.tier]:
        #     main_window.workout_list.addItem(i)
        # main_window.workout_list.itemClicked.connect(main_window.on_item_click)

        main_window.view.set_button_action("ready", lambda: WorkoutHandler.handle_next(main_window))
        main_window.view.set_button_action("back", lambda: WorkoutHandler.handle_back_to_main(main_window))

    @staticmethod
    def handle_back_to_main(main_window):
        print("🔙 BACK button tapped!")
        main_window.is_paused = False
        main_window.is_lookup = False
        main_window.modal_pause_view = None
        main_window.modal_exit_view = None
        main_window.is_workout = False

        main_window.view.set_mode("main")
        main_window.lookup_frame.hide()
        main_window.routine_frame.hide()
        main_window.view.set_button_action("start", lambda: WorkoutHandler.handle_start(main_window))
        main_window.view.set_button_action("exit", lambda: WorkoutHandler.handle_exit(main_window))
        main_window.view.set_button_action("lookup", lambda: WorkoutHandler.handle_lookup(main_window))

    @staticmethod
    def handle_continue_button(main_window):
        print("▶️ CONTINUE button tapped!")
        main_window.modal_pause_view = None
        main_window.view.set_mode("working")
        main_window.lookup_frame.hide()
        main_window.routine_frame.show()
        data=pack_data("RC",data='True')
        main_window.tcp.sendData(data)
        main_window.view.set_button_action("pause", lambda: WorkoutHandler.handle_pause(main_window))
        main_window.view.set_button_action("next", lambda: WorkoutHandler.handle_next(main_window))

    @staticmethod
    def handle_close_button(main_window):
        print("🔴 Close!")
        main_window.camera.stop()
        main_window.stackedWidget_big.setCurrentWidget(main_window.big_main_page)
        main_window.showNormal()

