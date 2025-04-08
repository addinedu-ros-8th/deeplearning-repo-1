# main_window.py
import sys
import os 
import time
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
from network.packer import pack_data
import Controller.Detector as Detector
import Constants as cons 
from file_client import FileClient
main_class = uic.loadUiType("client/ui/main_page.ui")[0]
class MainWindow(QMainWindow, main_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.db = FAAdb()
        self.cur = self.db.conn.cursor()
        self.file = FileClient()
        self.tcp = Client()
        self.udp = UdpClient()
        self.hand_detector = Detector.handDetector()
        self.camera = None
        self.profile_cnt = 0

        self.is_ready = False
        self.is_working = False

        self.is_lookup = False
        self.modal_pause_view = None
        self.modal_exit_view = None
        self.video_thread = None
        self.current_gesture = None
        self.gesture_start_time = None
        self.selection_confirmed = False
        self.prev_pi_data = None
        self.current = None

        self.username = None
        self.user_id = None
        self.tier = 0
        self.weight = 0
        self.height_ = 0
        self.score = 0
        self.routine = []

        self.remaining_time = 0 
        self.break_remaining_time = cons.BREAK_TIME
        self.last_tick_time = 0
        self.last_selected_row = -1
        self.is_break = False

        self.reps_done = 0
        self.set_done = False

        self.sets = 0
        self.reps = 0
        self.counts =0 

        self.auth = AuthHandler(self)
        self.btn_profile1.clicked.connect(lambda: self.auth.login_user(self.label_profile1.text()))
        self.btn_profile2.clicked.connect(lambda: self.auth.login_user(self.label_profile2.text()))
        self.btn_profile3.clicked.connect(lambda: self.auth.login_user(self.label_profile3.text()))
        self.btn_profile4.clicked.connect(lambda: self.auth.login_user(self.label_profile4.text()))
        
        self.btn_lastWorkout.clicked.connect(self.bring_video)

        self.record_handler = RecordHandler(self)
        
        UISetupHelper.profiles(self)
        UISetupHelper.buttons(self)
        UISetupHelper.button_stylers(self)
        self.displayScore()

        self.countdown_timer = QTimer()
        self.countdown_time_left = cons.COUNTDOWN 
        self.is_countdown = False 
            
    def start_preworkout_countdown(self):
        self.is_countdown = True
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # 1초마다 timeout 발생
    
    def update_countdown(self):
        if self.countdown_time_left > 0:
            self.countdown_time_left -=1 
        else:
            self.countdown_timer.stop()
            self.countdown_timer.timeout.disconnect(self.update_countdown)
            self.is_countdown = False
            
            self.is_working = True 
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
    def set_user_name(self, name, user_id, weight, height, tier, score):
        self.lb_name.setText(name)
        self.lb_name_2.setText(name)        # account name 

        self.username = name
        self.user_id = user_id
        self.weight = weight
        self.height_ = height
        self.tier = tier
        self.score = score
        
    def set_profile_icon(self, username):
        self.cur.execute("SELECT user_icon FROM user WHERE name = %s", (username,))
        result = self.cur.fetchone()
        
        if result and result[0]:
            pixmap = QPixmap()
            pixmap.loadFromData(result[0])
            self.btn_profile.setIcon(QIcon(pixmap))
            self.btn_profile.setIconSize(QSize(80, 80))
        else:
            self.btn_profile.setIcon(QIcon("./image_folder/User.png"))

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

    def set_current_workout(self):
        if self.current_index >= len(self.routine_queue):
            self.lb_what.setText("운동 완료!")
            self.lb_reps.setText("")
            self.lb_sets.setText("")
            self.lb_thumbnail.clear()
            return

        if not self.routine_queue:
            print("❌ 루틴이 비어 있습니다. 운동을 시작할 수 없습니다.")
            self.lb_what.setText("routine x")
            return
        
        current = self.routine_queue[self.current_index]
        # self.current_workout = current
        # current = self.routine_queue.pop(0)
        self.lb_what.setText(current["name"])
        self.lb_reps.setText(str(current["reps"]))
        self.lb_sets.setText(str(current["sets"]))
        self.set_thumbnail(self.lb_thumbnail, current["name"])
        self.routine_list.setCurrentRow(self.current_index)
        QApplication.processEvents()
        

    def set_thumbnail(self, label: QLabel, workout_name: str):
        gif_path = cons.THUMBNAIL.get(workout_name.lower())

        if gif_path and os.path.exists(gif_path):
            movie = QMovie(gif_path)            
            # label.setFixedSize(250, 500)
            movie.jumpToFrame(0)  # 첫 프레임 강제로 로딩
            original_size = movie.currentPixmap().size()

            scaled_size = QSize(original_size.width() // 3, original_size.height() // 3)
            movie.setScaledSize(scaled_size)
            label.setMovie(movie)
            movie.start()
        else:
            print(f"⚠️ 썸네일 gif가 존재하지 않거나 등록되지 않음: {workout_name}")
    
    def display_routine_list(self):
        self.routine_list.clear()
        for idx, routine in enumerate(self.routine_queue):
            name = routine["name"]
            sets = routine["sets"]
            reps = routine["reps"]
            # item_text = f"{name} - {sets}세트 x {reps}회"
            item = QListWidgetItem(name)
            self.routine_list.addItem(item)
        # self.routine_list.setCurrentRow(self.current_index)
    
    def start_break_timer(self):
        self.break_remaining_time = cons.BREAK_TIME
        self.last_tick_time = time.time()
        self.is_break = True
        self.is_working = False
        # self.lb_what.setText("휴식 중...")  # UI에 표시

    def handle_next_workout(self):
        self.current_index += 1
        self.set_current_workout()

    # Account 
    def show_modify(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_modify)
    def show_goal(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_goal)
    def show_todayrecord(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_record)
    def show_config(self):
        self.stackedWidget_small_2.setCurrentWidget(self.pg_config)
        self.btn_modify_workout.setEnabled(False)
        self.btn_delete_workout.setEnabled(False)
        self.tcp.sendData(pack_data(command="ME", status='0'))

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)
        loop.exec_()

        data = str.split(self.tcp.data['list_data'], '\n')

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        for tmp in data[:-1]:
            tier = ""
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)

            tmp2 = tmp.split(",")
            self.tableWidget.setItem(row, 0, QTableWidgetItem(tmp2[1]))
            if tmp2[2] == "0": tier = "bronze"
            elif tmp2[2] == "1": tier = "silver"
            elif tmp2[2] == "2": tier = "gold"
            self.tableWidget.setItem(row, 1, QTableWidgetItem(tier))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(tmp2[3]))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(tmp2[4]))

    def add_workout(self):
        workout = self.workout_text.text()
        tier = self.combo_tier.currentIndex()
        reps = self.combo_reps.currentText()
        score = self.combo_score.currentText()

        if not workout:
            QMessageBox.warning(self.main_window, "입력오류", "운동 이름을 입력해주세요.")
            return
        
        if self.tableWidget.findItems(workout, Qt.MatchContains):
            QMessageBox.warning(self, "입력오류", "이미 존재하는 운동입니다.")
            return
        
        data = workout + "," + str(tier) + "," + reps + "," + score
        self.tcp.sendData(pack_data("ME", status='1', data=data))

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)
        loop.exec_()

        if self.tcp.result == 1:
            QMessageBox.information(self, "성공", "'" + workout + "' 운동이 추가되었습니다.")
            self.show_config()
            self.tableWidget.scrollToBottom()
            self.workout_text.clear()
            self.combo_tier.setCurrentIndex(0)
            self.combo_reps.setCurrentIndex(0)
            self.combo_score.setCurrentIndex(0)
        elif self.tcp.result == 9:
            QMessageBox.warning(self, "실패", "'" + workout + "' 운동 추가에 실패했습니다.")

    def delete_workout(self):
        item = self.tableWidget.selectedItems()

        if not item:
            QMessageBox.warning(self, "삭제오류", "삭제할 운동을 선택해주세요.")
            return
        
        self.tcp.sendData(pack_data("ME", status='3', data=item[0].text()))

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)
        loop.exec_()

        if self.tcp.result == 3:
            QMessageBox.information(self, "성공", "'" + item[0].text() + "' 운동이 삭제되었습니다.")
            self.show_config()
            self.tableWidget.scrollToTop()
        elif self.tcp.result == 9:
            QMessageBox.warning(self, "실패", "'" + item[0].text() + "' 운동 삭제에 실패했습니다.")\
            
    def modify_workout(self):
        item = self.tableWidget.selectedItems()

        if not item:
            QMessageBox.warning(self, "수정오류", "수정할 운동을 선택해주세요.")
            return
        
        name = item[0].text()
        tier = str(self.combo_tier.currentIndex())
        reps = self.combo_reps.currentText()[:-1]
        score = self.combo_score.currentText()[:-1]

        data = name + "," + tier + "," + reps + "," + score
        self.tcp.sendData(pack_data("ME", status='2', data=data))

        loop = QEventLoop()
        self.tcp.responseReceived.connect(loop.quit)
        loop.exec_()

        if self.tcp.result == 2:
            QMessageBox.information(self, "성공", "'" + name + "' 운동이 수정되었습니다.")
            self.show_config()
        elif self.tcp.result == 9:
            QMessageBox.warning(self, "실패", "'" + name + "' 운동 수정에 실패했습니다.")
    
    def bring_video(self):
        
        data=self.file.pack_data('br',name=self.username)
        self.file.send_data(data)

    def click_tableWidget(self):
        item = self.tableWidget.selectedItems()

        if self.last_selected_row == self.tableWidget.currentRow():
            self.tableWidget.clearSelection()
            self.workout_text.clear()
            self.workout_text.setEnabled(True)
            self.workout_text.setFocus()
            self.combo_tier.setCurrentIndex(0)
            self.combo_reps.setCurrentIndex(0)
            self.combo_score.setCurrentIndex(0)
            self.last_selected_row = -1
            self.btn_add_workout.setEnabled(True)
            self.btn_modify_workout.setEnabled(False)
            self.btn_delete_workout.setEnabled(False)
            return

        self.workout_text.setText(item[0].text())
        self.workout_text.setEnabled(False)
        self.combo_tier.setCurrentText(item[1].text())
        self.combo_reps.setCurrentText(item[2].text() + "회")
        self.combo_score.setCurrentText(item[3].text() + "점")

        self.btn_add_workout.setEnabled(False)
        self.btn_modify_workout.setEnabled(True)
        self.btn_delete_workout.setEnabled(True)

        self.last_selected_row = self.tableWidget.currentRow()
    
    def set_user_tier(self,tier):
        tier_icon_path = cons.TIER_ICONS.get(tier)
        if tier_icon_path: 
            self.lb_tier.setPixmap(QPixmap(tier_icon_path))
            self.lb_tier.setScaledContents(True)
        else:
            print(f"[DEBUG] 티어 아이콘 경로가 잘못되었거나 존재하지 않음: {tier_icon_path}")

    def count(self):
        if self.tcp.result == 'up':
            self.count_up+=1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())
