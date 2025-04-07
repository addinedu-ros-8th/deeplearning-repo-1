# workout_handler.py

import time, cv2
from PyQt5.QtCore import QTimer
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

        print("💡 현재 username:", main_window.username)

    def load_user_routine(self):
        self.cur.execute("SELECT workout_name FROM routine WHERE username = %s ORDER BY idx ASC", (self.main_window.username,))
        rows = self.cur.fetchall()
        self.routine = [row[0] for row in rows]
        self.current_index = 0
    
    # def update_break_gui(self):
    #     # break 상태일 경우 화면에 타이머 표시
    #     if hasattr(self, 'classifier') and self.classifier.break_active:
    #         remaining = int(30 - (time.time() - self.classifier.break_start_time))
    #         if remaining >= 0:
    #             cv2.putText(frame, f"Break Time: {remaining}s", (cons.window_width // 2 - 200, 80),
    #                         cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    #         if not self.classifier.check_break():
    #             print("[Main] break 종료됨")
    #             # break 종료 시 아무 것도 하지 않음 (exercise_model이 알아서 다음 세트 처리)
    #     return frame

    def next_set_or_workout(self):
        model = self.main_window.classifier
        current = model.get_current_exercise()

        if current is None:
            self.main_window.lb_what.setText("루틴 완료")
            return

        if model.reps_done < current['sets']:
            print(f"➡️ 다음 세트 시작: {model.reps_done + 1}/{current['sets']}")
        else:
            print(f"✅ 운동 완료: {current['name']}")
            model.reps_done = 0
            model.current_routine_idx += 1
            model.update_routine_index(model.current_routine_idx)

        if model.current_routine_idx < len(model.routine_list):
            self.main_window.remaining_time = 30
            self.main_window.last_tick_time = time.time()
            self.main_window.is_break = True
        else:
            print("🎉 루틴 전체 완료")
            self.main_window.lb_what.setText("모든 운동 완료!")


    @staticmethod
    def go2workout(main_window):
        main_window.modal_exit_view = None
        main_window.modal_pause_view = None
        main_window.lb_cam.clear()
        QApplication.processEvents()

        main_window.stackedWidget_big.setCurrentWidget(main_window.workout_page)
        main_window.showFullScreen()
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
        # data = pack_data(command="GR", name=main_window.username)
        # main_window.tcp.sendData(data)
        # main_window.tcp.responseReceived.connect(lambda: WorkoutHandler.on_routine_ready(main_window))

        WorkoutHandler.on_routine_ready(main_window)
        
        main_window.view = ViewMain()
        main_window.view.set_mode("main")
        main_window.view.set_button_action("start", lambda: WorkoutHandler.handle_start(main_window))
        main_window.view.set_button_action("exit", lambda: WorkoutHandler.handle_exit(main_window))
        main_window.view.set_button_action("lookup", lambda: WorkoutHandler.handle_lookup(main_window))
    
    @staticmethod
    def handle_break_time(main_window, frame):
        if not main_window.is_break: return
        if main_window.remaining_time > 0:
            now = time.time()
            if now - main_window.last_tick_time >= 1:
                main_window.remaining_time -= 1
                main_window.last_tick_time = now
        else:
            main_window.is_break = False
            main_window.workout_handler.next_set_or_workout()
        cv2.putText(frame, f"Break: {main_window.remaining_time}s", (cons.window_width // 2, cons.window_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (75, 150, 150), 3)
    @staticmethod      
    def handle_pose_info(main_window, frame):
        if not isinstance(main_window.tcp.landmark, dict):
            return
        pi_data = main_window.tcp.landmark
        if pi_data.get("command") != "PI":
            return


        # 루틴에서 reps / sets 가져오기
        try:
            routine = main_window.routine_queue[main_window.current_index]
            total_reps = routine['reps']
            total_sets = routine['sets']
            done_sets = main_window.reps_done
        except Exception as e:
            print("⚠️ handle_pose_info 루틴 정보 접근 실패:", e)
            return
        
        count = pi_data['count']

        # remaining_reps = max(0, total_reps - count)
        # remaining_sets = max(0, total_sets - done_sets)
        
        if not main_window.is_break:
            ox, oy = pi_data['origin']['x'], pi_data['origin']['y']
            cv2.circle(frame, (ox, oy), 10, (0, 255, 255), -1)

            vx, vy = pi_data['vector']['x'], pi_data['vector']['y']
            cv2.arrowedLine(frame, (ox, oy), (vx, vy), (255, 0, 255), 3)

            for pt in pi_data['landmarks']:
                cv2.circle(frame, (pt['x'], pt['y']), 6, (0, 100, 255), -1)
            # 남은 개수와 세트
            cv2.putText(frame, f"reps: {count}/{total_reps}", 
                        (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
            cv2.putText(frame, f"sets: {done_sets}/{total_sets}", 
                        (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
    @staticmethod    
    def handle_workout_timer(main_window, frame):
        if main_window.is_break: return  # break 중일 땐 pass

        #  1. 현재 운동 Routine 정보 가져오기
        routine = main_window.routine_queue[main_window.current_index]
        # current_reps = routine['reps']
        # count = main_window.classifier.angle_counter.get_count()
        # 2. 카운트가 목표에 도달했을 경우 → break 시작
        # if count >= current_reps:
        #     print(f"🎯 목표 도달! Count {count} / Reps {current_reps}")
        #     main_window.classifier.angle_counter.set_count()  # count 초기화
        #     main_window.reps_done += 1

        #     if main_window.reps_done < routine['sets']:
        #         print(f"➡️ 세트 완료: {main_window.reps_done}/{routine['sets']}")
        #     else:
        #         print(f"✅ 운동 완료: {routine['name']}")
        #         main_window.reps_done = 0
        #         main_window.current_index += 1
        #         main_window.set_current_workout()

        #     main_window.start_break_timer()
        #     return  # 여기서 타이머 갱신 중단
        
        # 3. Timer 처리 
        if main_window.remaining_time > 0:
            now = time.time()
            if now - main_window.last_tick_time >= 1:
                main_window.remaining_time -= 1
                main_window.last_tick_time = now
        else:
            # 시간 초과 시 break 
            main_window.remaining_time = 0
            main_window.is_workout = False
            main_window.reps_done += 1
            print(f"⏰ 시간 초과! 세트 {main_window.reps_done} 강제 종료")

            routine = main_window.routine_queue[main_window.current_index]
            if main_window.reps_done < routine['sets']:
                print("➡ 다음 세트 준비 (30초)")
            else:
                print("✅ 다음 운동으로 (30초)")
                main_window.reps_done = 0
                main_window.current_index += 1
            main_window.start_break_timer()
        # 4. 남은 시간 rendering 
        cv2.putText(frame, f"{main_window.remaining_time}", (cons.window_width - 250, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    @staticmethod   
    def handle_lookup_mode(main_window, frame, lmList):
        number = main_window.hand_detector.count_fingers(lmList)
        cv2.putText(frame, f'{number}', (cons.window_width - 100, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        if 1 <= number <= 5:
            if main_window.current_gesture != number:
                main_window.current_gesture = number
                main_window.gesture_start_time = time.time()
                main_window.selection_confirmed = False
            elif not main_window.selection_confirmed and time.time() - main_window.gesture_start_time >= 3:
                main_window.selection_confirmed = True
                WorkoutHandler.play_selected_workout(main_window, number, main_window.tier)
        else:
            main_window.current_gesture = None
            main_window.gesture_start_time = None
            main_window.selection_confirmed = False
    @staticmethod
    def draw_overlay_ui(main_window, frame):
        if main_window.view:
            main_window.view.appear(frame)
        if main_window.modal_pause_view:
            main_window.modal_pause_view.appear(frame)
        if main_window.modal_exit_view:
            main_window.modal_exit_view.appear(frame)
    @staticmethod
    def send_to_gui(main_window, frame, frame_copy):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
        main_window.lb_cam.setPixmap(QPixmap.fromImage(qt_img))            

    @staticmethod
    def update_gui(main_window):
        if main_window.camera.frame is None: return
    
        frame_copy = main_window.camera.frame.copy()
        frame = main_window.hand_detector.findHands(main_window.camera.frame, draw=False)
        lmList = main_window.hand_detector.findPosition(frame, draw=False)
        Detector.analyze_user(frame)
        hands.set()

        if main_window.is_ready:
            WorkoutHandler.handle_break_time(main_window, frame)
            WorkoutHandler.handle_pose_info(main_window, frame)
            WorkoutHandler.handle_workout_timer(main_window, frame)

            main_window.udp.send_video(frame_copy, main_window.lb_what.text(), main_window.user_id)

        elif main_window.is_lookup:
            WorkoutHandler.handle_lookup_mode(main_window, frame, lmList)

        WorkoutHandler.draw_overlay_ui(main_window, frame)
        WorkoutHandler.send_to_gui(main_window, frame, frame_copy)
        
            #     # print(main_window.tcp.landmark)
            #     if isinstance(main_window.tcp.landmark, dict) and main_window.tcp.landmark.get("command") == "PI":
            #         pi_data = main_window.tcp.landmark

            #         # origin
            #         ox, oy = pi_data['origin']['x'], pi_data['origin']['y']
            #         cv2.circle(frame, (ox, oy), 10, (0, 255, 255), -1)  # 노란 원

            #         # vector
            #         vx, vy = pi_data['vector']['x'], pi_data['vector']['y']
            #         cv2.arrowedLine(frame, (ox, oy), (vx, vy), (255, 0, 255), 3)  # 보라색 벡터 선

            #         # landmarks
            #         for pt in pi_data['landmarks']:
            #             lx, ly = pt['x'], pt['y']
            #             cv2.circle(frame, (lx, ly), 6, (0, 100, 255), -1)  # 주황색 점
            #         # 시간 갱신 
            #         cv2.putText(frame, f"Count: {pi_data['count']}", (10, 180), 
            #                     cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            #     if main_window.is_break:
            #         if main_window.remaining_time > 0:
            #             current_time = time.time()
            #             elapsed = current_time - main_window.last_tick_time
            #             if elapsed >= 1:
            #                 main_window.remaining_time -= 1
            #                 main_window.last_tick_time = current_time
            #         else:
            #             main_window.is_break = False
            #             main_window.workout_handler.next_set_or_workout()
                    
            #     else: 
   
            #         if main_window.remaining_time > 0:
            #             current_time = time.time()
            #             elapsed = current_time - main_window.last_tick_time

            #             if elapsed >= 1 :
            #                 main_window.remaining_time -= 1
            #                 main_window.last_tick_time = current_time
            #         else: 
            #             main_window.remaining_time = 0
            #             main_window.is_workout = False

            #             # ✅ 1세트 완료로 간주 → reps_done 증가
            #             main_window.reps_done += 1
            #             print(f"⏰ 시간 초과! 세트 {main_window.reps_done} 강제 종료")

            #             current_routine = main_window.routine_queue[main_window.current_index]
            #             total_sets = current_routine['sets']

            #             if main_window.reps_done < total_sets:
            #                 print(f"➡ 다음 세트 준비 중... (30초 휴식)")
            #                 main_window.start_break_timer()
            #             else:
            #                 print(f"✅ 운동 '{current_routine['name']}' 완료. 다음 운동으로 이동 중... (30초 휴식)")
            #                 main_window.reps_done = 0
            #                 main_window.current_index += 1
            #                 main_window.start_break_timer()
            #     cv2.putText(frame, f"{main_window.remaining_time}", (cons.window_width - 250, 50),
            #                                     cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # elif main_window.is_lookup:
            #     number = main_window.hand_detector.count_fingers(lmList)
            #     cv2.putText(frame, f' {number}', (cons.window_width - 100, 50),
            #                 cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

            #     if 1 <= number <= 5:
            #         if main_window.current_gesture != number:
            #             main_window.current_gesture = number
            #             main_window.gesture_start_time = time.time()
            #             main_window.selection_confirmed = False
            #             print(f"⏳ 숫자 {number} 인식됨. 유지 중...")
            #         elif not main_window.selection_confirmed and time.time() - main_window.gesture_start_time >= 3:
            #             print(f"🎯 숫자 {number} 확정됨! 운동 시작.")
            #             main_window.selection_confirmed = True
            #             WorkoutHandler.play_selected_workout(main_window, number, main_window.tier)
            #     else:
            #         main_window.current_gesture = None
            #         main_window.gesture_start_time = None
            #         main_window.selection_confirmed = False

            

            # if main_window.view:
            #     main_window.view.appear(frame)
            # if main_window.modal_pause_view:
            #     main_window.modal_pause_view.appear(frame)
            # if main_window.modal_exit_view:
            #     main_window.modal_exit_view.appear(frame)

            # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            # main_window.lb_cam.setPixmap(QPixmap.fromImage(qt_img))
            # if main_window.camera.is_active:
            #     main_window.udp.send_video(frame_copy)

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

        main_window.remaining_time = cons.TIER_TIMES.get(main_window.tier, 80)
        main_window.last_tick_time = time.time()
        main_window.is_workout = True

        main_window.view.set_button_action("pause", lambda: WorkoutHandler.handle_pause(main_window))
        main_window.view.set_button_action("ready", lambda: WorkoutHandler.handle_ready(main_window))
    @staticmethod
    def on_routine_ready(main_window):
        # GR에 대한 응답인지 확인
        
        main_window.routine_queue = main_window.routine.copy()
        main_window.current_index = 0
        main_window.set_current_workout()
        main_window.display_routine_list()
        
        # 이 연결은 한 번만 실행되도록 제거해주면 좋음
        try:
            main_window.tcp.responseReceived.disconnect()
        except Exception as e:
            print("disconnect 실패:", e)
    @staticmethod
    def handle_ready(main_window):
        print("Ready button tapped!")
        main_window.is_ready = True 

        main_window.view.set_button_action("pause", lambda: WorkoutHandler.handle_pause(main_window))
        main_window.view.set_button_action("ready", lambda: WorkoutHandler.handle_ready(main_window))
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
        main_window.workout_list.clear()
        main_window.tier = (main_window.tier + 1) % 3
        main_window.view.tier = main_window.tier
        main_window.label_tier.setText(main_window.tier_list[main_window.tier])

        main_window.view.set_mode("lookup")
        for i in main_window.total_work_list[main_window.tier]:
            main_window.workout_list.addItem(i)
        # main_window.workout_list.itemClicked.connect(main_window.on_item_click)

        main_window.view.set_button_action("next", lambda: WorkoutHandler.handle_next(main_window))
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
        main_window.view.set_button_action("ready", lambda: WorkoutHandler.handle_ready(main_window))

    @staticmethod
    def handle_close_button(main_window):
        print("🔴 Close!")
        main_window.camera.stop()
        main_window.stackedWidget_big.setCurrentWidget(main_window.big_main_page)
        main_window.showNormal()
