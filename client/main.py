

from PyQt5.QtWidgets import QApplication
import sys
#from auth_window import AuthWindow
from main_window import MainWindow
if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = MainWindow()
    client.show()
    sys.exit(app.exec_())


# import sys
# import os 
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5 import uic
# from PyQt5.QtNetwork import QTcpSocket, QUdpSocket
# from config import SERVER_PORT
# from client.network.socket_client import Client
# from client.network.udp_client import UdpClient
# from server.database import FAAdb

# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
# from PyQt5.QtMultimediaWidgets import QVideoWidget

# import json
# import struct
# from camera import Camera
# from Video import Video
# import Controller.Hands as hands
# import Controller.Detector as Detector

# from View.ViewModal import ViewModalPause,ViewModalExit
# from View.ViewMain import ViewMain
# import Constants as cons

# import cv2
# import time


# second_class = uic.loadUiType("client/ui/auth.ui")[0]
# main_class = uic.loadUiType("client/ui/real_real_main_page.ui")[0]

# class secondWindow(QMainWindow, second_class):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#         self.setWindowTitle("User")
#         self.db = FAAdb()
#         self.cur = self.db.conn.cursor()
#         self.main = mainWindow()
#         self.profile_cnt = 0
#         self.stackedWidget.setCurrentWidget(self.add_profile_page)

#         프로필 설정 화면 버튼 이벤트
#         self.btn_select_profile_img.clicked.connect(self.select_icon)
#         self.btn_profile_save.clicked.connect(self.profile_save)

#     def register_complete(self):
#         id = self.register_input_id.text()
#         passwd = self.register_input_passwd.text()
#         passwd_compare = self.input_passwd_compare.text()
#         email = self.register_input_email.text()
        
#         if passwd == passwd_compare:
#             data = self.pack_data(command="RS", id=id, pw=passwd, email=email)
#             self.tcp.sendData(data)

#             loop = QEventLoop()
#             self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
#             loop.exec_()  # 응답이 올 때까지 여기서 대기

#             if self.tcp.result == 0:
#                 QMessageBox.about(self, "회원가입", "가입 성공")
#                 self.stackedWidget.setCurrentWidget(self.login_page)
#             elif self.tcp.result == 1:
#                 QMessageBox.about(self, "회원가입", "아이디 중복")
#             elif self.tcp.result == 2:
#                 QMessageBox.about(self, "회원가입", "이메일 중복")
#         else:
#             QMessageBox.warning(self, "회원가입", "비밀번호가 일치하지 않습니다.")
    
#     def passwd_reset(self):
#         id = self.id_check_input_id.text()
#         email = self.id_check_input_email.text()

#         new_passwd = self.passwd_reset_input_passwd.text()
#         new_passwd_compare = self.passwd_reset_input_passwd_compare.text()

#         if new_passwd == new_passwd_compare:
#             self.cur.execute("UPDATE user set password = %s where login_id = %s and email = %s",(new_passwd,id,email) )
#             self.db.commit()
#             QMessageBox.about(self, "비밀번호 재설정", "변경이 완료되었습니다.")
#             self.stackedWidget.setCurrentWidget(self.login_page)
#         else:
#             QMessageBox.warning(self, "비밀번호 재설정", "비밀번호가 일치하지 않습니다.")
    

    
#     def select_icon(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "/home/sang/dev_ws/save_file/profile_icon", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")

#         if file_path:
#             pixmap = QPixmap(file_path)
#             self.label.setPixmap(pixmap.scaled(300, 300))  # 크기 조절
#             self.btn_select_profile_img.setStyleSheet(f"""
#                 QPushButton {{
#                     border-image: url({file_path});
#                     min-width: 200px;
#                     min-height: 200px;
#                 }}
#             """)
#         with open(file_path,"rb") as file:
#             self.image_data = file.read()

#     def profile_save(self):
#         name = self.profile_input_name.text()
#         height = self.profile_input_height.text()
#         weight = self.profile_input_weight.text()
#         passwd = self.profile_input_passwd.text()        
#         data = self.main.pack_data(command="RG", name=name, pw=passwd, image_data=self.image_data, height=height, weight= weight)
#         self.main.tcp.sendData(data)  

#         loop = QEventLoop()
#         self.main.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
#         loop.exec_()  # 응답이 올 때까지 여기서 대기

#         if self.main.tcp.result == 0:
#             QMessageBox.about(self, "회원가입", "가입 성공")
#             self.close()
#             self.client_main = mainWindow()
#             self.client_main.profile_cnt += 1
#             self.client_main.add_profile(self.client_main.profile_cnt)

#             self.cur.execute("insert into user(name, height, weight, user_icon, password, tier) values(%s, %s, %s, %s, %s,0)",(name,weight,height,self.image_data, passwd))
#         elif self.main.tcp.result == 1:
#             QMessageBox.about(self, "회원가입", "이름 중복")
       
#         self.cur.execute("insert into user(name, height, weight, user_icon, password) values(%s, %s, %s, %s, %s)",(name,weight,height,self.image_data, passwd))
#         self.db.commit()
        

# class mainWindow(QMainWindow, main_class):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#         self.db = FAAdb()
#         self.cur = self.db.conn.cursor()
#         self.tcp = Client()
#         self.udp = UdpClient()
#         self.profile_cnt = 0

#         # 버튼을 toggle 가능하게 변경
#         self.btn_workout.setCheckable(True)
#         self.btn_record.setCheckable(True)
#         self.btn_rank.setCheckable(True)

#         self.is_lookup = False
#         self.hand_detector = Detector.handDetector()
#         self.modal_pause_view = None
#         self.modal_exit_view = None
#         self.video_thread = None
        
#         self.current_gesture = None
#         self.gesture_start_time = None
#         self.selection_confirmed = False

#         # 페이지 전환 이벤트 연결 
#         self.btn_workout.clicked.connect(self.show_main)
#         self.btn_record.clicked.connect(self.show_record)
#         self.btn_rank.clicked.connect(self.show_rank)
        
#         # 첫 화면 기본 설정 
#         self.btn_workout.setChecked(True)
#         self.stackedWidget_big.setCurrentWidget(self.profile_page)
#         self.stackedWidget_small.setCurrentWidget(self.main_page)

#         self.btn_start.clicked.connect(self.go2workout)
#         self.btn_save.clicked.connect(self.save_video)
#         self.btn_work_to_main.clicked.connect(self.back_work_to_main)

#         self.count_up = 0
#         self.tier=0

#         # 프로필 계정 유무확인후 버튼 활성화
#         self.cur.execute("select count(name) from user")
#         cnt = self.cur.fetchall()
#         cnt = int(cnt[0][0])
#         self.cur.execute("select name,user_icon from user where name is not null")
#         name = self.cur.fetchall()
#         #print(name)
#         name_list=[]
#         icon_list=[]
#         if len(name) != 0:
#             for n in name:
#                 name_list.append(n[0])
#                 icon_list.append(n[1])
#         print(cnt)

#         buttons = [self.btn_profile1, self.btn_profile2, self.btn_profile3, self.btn_profile4]
#         labels = [self.label_profile1, self.label_profile2, self.label_profile3, self.label_profile4]

#         # 모든 버튼과 라벨 숨기기
#         for btn, label in zip(buttons, labels):
#             btn.setVisible(False)
#             label.setText("")

#         if cnt == 0:
#             return  # 프로필이 없을 경우 종료

#         icon_size = 200  # 아이콘 크기 설정
#         for i in range(cnt):
#             pixmap = QPixmap()
#             pixmap.loadFromData(icon_list[i])  # 바이너리 데이터를 QPixmap으로 변환
            
#             buttons[i].setIcon(QIcon(pixmap))
#             buttons[i].setIconSize(QSize(icon_size, icon_size))
#             labels[i].setText(name_list[i])
#             buttons[i].setVisible(True)

#         self.profile_cnt = cnt
#         self.btn_plus_profile.setEnabled(cnt < 4)  # 최대 4개까지 추가 가능
        
#         # 계정 생성 버튼 이벤트 연결
#         self.btn_plus_profile.clicked.connect(self.plus_profile)

#         self.btn_profile1.clicked.connect(self.clicked_profile_1)
#         self.btn_profile2.clicked.connect(self.clicked_profile_2)
#         self.btn_profile3.clicked.connect(self.clicked_profile_3)
#         self.btn_profile4.clicked.connect(self.clicked_profile_4)
        
#         # 버튼 아이콘 설정
#         self.btn_plus_profile.setIcon(QIcon("/home/sang/dev_ws/save_file/image_folder/plus.png"))  # 아이콘 설정
#         self.btn_plus_profile.setIconSize(self.btn_plus_profile.sizeHint())  # 아이콘 크기를 버튼 크기의 절반으로 설정
#         self.btn_plus_profile.setStyleSheet("""
#         QPushButton {
#             border: 2px solid #ccc;
#             background-color: white;
#         }
#         """)
#         # 계정 버튼 아이콘 설정
#         self.btn_profile.setIcon(QIcon("/home/sang/dev_ws/save_file/image_folder/profil_icon.png"))  # 아이콘 설정
#         self.btn_profile.setIconSize(self.btn_plus_profile.sizeHint()*1.5)
#         self.btn_profile.setStyleSheet("""
#         QPushButton {
#             border: 2px solid #ccc;
#             background-color: white;
#         }
#         """)

#         #영상 저장 명령버튼
#         self.btn_save.clicked.connect(self.save_video)

#     def pack_data(self, command, pw=None, name=None, height=None, weight=None, data=None, content=None, image_data=None):
#         packed_data = b''
        
#         # 명령어 패킹 (길이 + 데이터)
#         packed_data += struct.pack('I', len(command)) + command.encode('utf-8')
        
#         # 비밀번호 패킹 (길이 + 데이터)
#         if pw is not None:
#             packed_data += struct.pack('I', len(pw)) + pw.encode('utf-8')
#         else:
#             packed_data += struct.pack('I', 0)
        
#         # 이름 패킹 (길이 + 데이터)
#         if name is not None:
#             packed_data += struct.pack('I', len(name.encode('utf-8'))) + name.encode('utf-8')
#         else:
#             packed_data += struct.pack('I', 0)
        
#         # 키 높이 패킹 (길이 + 데이터)
#         if height is not None:
#             packed_data += struct.pack('I', len(str(height))) + str(height).encode('utf-8')
#         else:
#             packed_data += struct.pack('I', 0)
        
#         # 몸무게 패킹 (길이 + 데이터)
#         if weight is not None:
#             packed_data += struct.pack('I', len(str(weight))) + str(weight).encode('utf-8')
#         else:
#             packed_data += struct.pack('I', 0)
        
#         # 데이터 패킹
#         if data is not None:
#             data_bytes = data.encode('utf-8')
#             packed_data += struct.pack('I', len(data_bytes)) + data_bytes
#         else:
#             packed_data += struct.pack('I', 0)
        
#         # 콘텐트 패킹
#         if content is not None:
#             content_bytes = content.encode('utf-8')
#             packed_data += struct.pack('I', len(content_bytes)) + content_bytes
#         else:
#             packed_data += struct.pack('I', 0)
        
#         # 이미지 데이터 패킹 (이미지 파일을 바이너리로 읽어 전달)
#         if image_data is not None:
#             packed_data += struct.pack('I', len(image_data)) + image_data
#         else:
#             packed_data += struct.pack('I', 0)

#         return packed_data
    
#     main pages 
#     def show_main(self):
#         self.stackedWidget_small.setCurrentWidget(self.main_page)

#     def show_record(self):
#         self.stackedWidget_small.setCurrentWidget(self.record_page)

#         self.radio_day.setChecked(True)
#         self.radio_day.toggled.connect(self.switch_graph)
#         self.radio_week.toggled.connect(self.switch_graph)
#         self.radio_month.toggled.connect(self.switch_graph)
    
#     def show_rank(self):
#         self.stackedWidget_small.setCurrentWidget(self.rank_page)


#     def switch_graph(self):
#         if self.radio_day.isChecked():
#             self.stackedGraphs.setCurrentIndex(0)
#         elif self.radio_week.isChecked():
#             self.stackedGraphs.setCurrentIndex(1)
#         elif self.radio_month.isChecked():
#             self.stackedGraphs.setCurrentIndex(2)
    
    
#     def plus_profile(self):
#         self.second=secondWindow()
#         self.second.show()
#         self.second.stackedWidget.setCurrentWidget(self.second.add_profile_page)
    
#     def add_profile(self, profile_cnt):
#         self.db.conn.reconnect(attempts=3, delay=2) #db 새로고침
#         print(profile_cnt)
#         self.cur.execute("SELECT user_icon, name FROM user WHERE name IS NOT NULL")
#         profiles = self.cur.fetchall()
        
#         profile_buttons = [
#             (self.btn_profile1, self.label_profile1),
#             (self.btn_profile2, self.label_profile2),
#             (self.btn_profile3, self.label_profile3),
#             (self.btn_profile4, self.label_profile4)
#         ]
        
#         icon_size = 200  # 버튼 크기 설정
        
#         for i in range(min(profile_cnt, len(profiles))):
#             user_icon, name = profiles[i]
#             pixmap = QPixmap()
#             pixmap.loadFromData(user_icon)  # 바이너리 데이터를 QPixmap으로 변환
            
#             btn, label = profile_buttons[i]
#             btn.setIcon(QIcon(pixmap))
#             btn.setIconSize(QSize(icon_size, icon_size))
#             label.setText(name)
#             btn.setVisible(True)
    
#         self.btn_plus_profile.setEnabled(profile_cnt < 4)
    
#     def clicked_profile_1(self):
#         self.move_main_page(self.label_profile1.text())
#     def clicked_profile_2(self):
#         self.move_main_page(self.label_profile2.text())
#     def clicked_profile_3(self):
#         self.move_main_page(self.label_profile3.text())
#     def clicked_profile_4(self):
#         self.move_main_page(self.label_profile4.text())
    
#     def move_main_page(self,name):
#         input_passwd, ok = QInputDialog.getText(self, '계정 비밀번호', '비밀번호를 입력하세요 :')
    
#         if not ok or not input_passwd:
#             QMessageBox.warning(self, "계정 비밀번호", "비밀번호를 입력해야 합니다.")
#             return
        
#         self.cur.execute("SELECT password FROM user WHERE name = %s and password = %s", (name, input_passwd))
#         result = self.cur.fetchall()
        
#         if not result:
#             QMessageBox.warning(self, "계정 비밀번호", "비밀번호가 일치하지 않습니다.")
#             return
        
#         passwd = result[0][0]
#         data = self.pack_data(command="LI", name=name, pw=passwd)
#         self.tcp.sendData(data)

#         loop = QEventLoop()
#         self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
#         loop.exec_()
    
#         if self.tcp.result == 0:
#             print("로그인 성공")
#             self.stackedWidget_big.setCurrentWidget(self.big_main_page)
#             self.set_user_name(name)
#         else:
#             QMessageBox.warning(self, "계정 비밀번호", "로그인 정보가 틀렸습니다.")
    
#     def set_user_name(self,name):
#         self.lb_name.setText(name)
    
#     def go2workout(self):
#         self.modal_exit_view = None
#         self.modal_pause_view = None
#         self.lb_cam.clear()
#         QApplication.processEvents()

#         # 1. Page switch
#         self.stackedWidget_big.setCurrentWidget(self.workout_page)
#         self.showFullScreen()
#         self.lookup_frame.hide()
#         self.lb_cam = self.workout_page.findChild(QLabel, "lb_cam")
#         self.lb_cam.setScaledContents(True)
        
#         # Hide widget which contains workout list 
#         #self.workout_list_widget.hide()
#         # 2. Video widget 
#         self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
#         self.video_widget = QVideoWidget()
#         self.video_player.setVideoOutput(self.video_widget)
        
#         #self.workout_list.layout().addWidget(self.video_widget)
#         self.video_widget.hide()

#         # 3. Camera 시작 
#         self.camera = Camera()
#         self.camera.start()

#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_gui)
#         self.timer.start(30)
        
#         # 4. bttn View 구성 
#         self.view = ViewMain()
#         self.view.set_mode("main")
#         self.view.set_button_action("start", self.handle_start)
#         self.view.set_button_action("exit", self.handle_exit)
#         self.view.set_button_action("lookup", self.handle_lookup)

#     def on_item_click(self, item):
#         # 클릭된 항목에 따라 재생할 비디오 경로 지정
#         video_map = {
#             "Front Lunge": "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
#             "Side Lunge": "/home/sang/dev_ws/save_file/Asset/side-lunge.mp4",
#             "Squat": "/home/sang/dev_ws/save_file/Asset/squat.mp4"
#         }
        
#         # 클릭된 항목의 텍스트를 가져와서 해당 비디오 경로로 비디오 재생
#         video_path = video_map.get(item.text(), "")
#         print(video_path)
#         if video_path:
#             self.play_workout_video(video_path)
    
#     def play_workout_video(self, video_path):
#         # 비디오 재생 코드 (예시로 출력만 합니다)
#         print(f"Playing workout video: {video_path}")

#     def back_work_to_main(self):
#         self.camera.stop()
#         self.stackedWidget_big.setCurrentWidget(self.big_main_page)
#         self.showNormal()

#     def play_selected_workout(self, index, tier):
#         if tier == 0:
#             videos = {
#                 1: "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
#                 2: "/home/sang/dev_ws/save_file/Asset/squat.mp4",
#                 3: "/home/sang/dev_ws/save_file/Asset/shoulder_press.mp4",
#                 4: "/home/sang/dev_ws/save_file/Asset/knee-up.mp4"
#             }
#         elif tier == 1:
#             videos = {
#                 1: "/home/sang/dev_ws/save_file/Asset/push-up.mp4",
#                 2: "/home/sang/dev_ws/save_file/Asset/bridge.mp4",
#                 3: "/home/sang/dev_ws/save_file/Asset/standing-bicycle.mp4",
#                 4: "/home/sang/dev_ws/save_file/Asset/side-lunge.mp4"
#             }
#         elif tier == 2:
#             videos = {
#                 1: "/home/sang/dev_ws/save_file/Asset/front-lunge.mp4",
#                 2: "/home/sang/dev_ws/save_file/Asset/squat.mp4",
#                 3: "/home/sang/dev_ws/save_file/Asset/shoulder_press.mp4",
#                 4: "/home/sang/dev_ws/save_file/Asset/knee-up.mp4"
#             }   
#         if index in videos:
#             self.play_workout_video(videos[index])
#         else:
#             print(f"❌ {index}번 운동은 정의되지 않았습니다.")

#     def play_workout_video(self, video_path):
#         # 이전 재생 중이면 중단
#         if self.video_thread and self.video_thread.isRunning():
#             self.video_thread.stop()
#             self.video_thread.wait()

#         self.lb_cam.clear()
#         self.timer.stop()

#         self.video_thread = Video(video_path,self.lb_cam.size())
#         self.video_thread.frame_ready.connect(self.display_video_frame)
#         self.video_thread.finished.connect(self.resume_camera)
#         self.video_thread.start()

#     def handle_start(self):
#         print("🟢 START button tapped!")
#         self.view.set_mode("working")
#         self.lookup_frame.hide()
#         self.save_video()
#         QApplication.processEvents()
#         self.view.set_button_action("pause", self.handle_pause)
#         self.view.set_button_action("next", self.handle_next)

#     def handle_exit(self):
#         print("EXIT button tapped!")

#         self.modal_exit_view = ViewModalExit()
#         self.modal_exit_view.bttn_yes.action = self.handle_close_button
#         self.modal_exit_view.bttn_no.action = self.handle_back_to_main

#     def handle_lookup(self):
#         print(" Lookup button tapped!")
#         # show workout list 
#         self.total_work_list=[]
#         bronze_work_list=['Front Lunge', 'Squat', 'Sholder-press', 'Knee-up']
#         silver_work_list=['Push-up', 'Bridge', 'Standing Bicycle', 'Side lunge']
#         gold_work_list=['Sit-up', 'Side-plank', 'One-leg-knee-up', 'V-up']

#         self.tier_list=['BRONZE', 'SILVER', 'GOLD']
#         self.total_work_list.append(bronze_work_list)
#         self.total_work_list.append(silver_work_list)
#         self.total_work_list.append(gold_work_list)

#         self.mode = "lookup"
#         self.is_lookup = True
#         self.view.set_mode("lookup")
#         # lookup btns
#         self.lookup_frame.show()
#         self.workout_list.clear()
#         self.label_tier.setText(self.tier_list[self.tier])
        
#         for i in self.total_work_list[self.tier]:
#             self.workout_list.addItem(i)
#         self.workout_list.itemClicked.connect(self.on_item_click)

#         self.view.set_button_action("next", self.handle_next)
#         self.view.set_button_action("back", self.handle_back_to_main)

#     def handle_pause(self):
#         print("⏸️ PAUSE button tapped!")

#         self.modal_pause_view = ViewModalPause()
#         self.modal_pause_view.bttn_back.action = self.handle_back_to_main
#         self.modal_pause_view.bttn_continue.action = self.handle_continue_button

#     def handle_next(self):
#         print("Next button tapped!")
#         self.workout_list.clear()
#         self.tier += 1
#         if self.tier == 3:
#             self.tier = 0
#         self.view.tier = self.tier
#         self.label_tier.setText(self.tier_list[self.tier])
#         self.view.set_mode("lookup")
#         for i in self.total_work_list[self.tier]:
#             self.workout_list.addItem(i)
#         self.workout_list.itemClicked.connect(self.on_item_click)

#         self.view.set_button_action("next", self.handle_next)
#         self.view.set_button_action("back", self.handle_back_to_main)

#     def handle_back_to_main(self):
#         print("🔙 BACK button tapped!")
#         # hide workout list 
#         #self.workout_list_widget.hide()
#         self.is_paused = False
#         self.is_lookup = False
#         self.modal_pause_view = None
#         self.modal_exit_view = None
        
#         self.view.set_mode("main")
#         self.lookup_frame.hide()
#         self.view.set_button_action("start",  self.handle_start)
#         self.view.set_button_action("exit",   self.handle_exit)
#         self.view.set_button_action("lookup", self.handle_lookup)


#     def handle_continue_button(self):
#         print("▶️ CONTINUE button tapped!")
#         self.modal_pause_view = None

#         self.view.set_mode("working")
#         self.lookup_frame.hide()
#         self.view.set_button_action("pause", self.handle_pause)
#         self.view.set_button_action("next", self.handle_next)

#     def handle_close_button(self):
#         print("🔴 Close!")
#         self.camera.stop()
#         self.stackedWidget_big.setCurrentWidget(self.big_main_page)
#         self.showNormal()

#         # self.close()

#     def handle_show(self):
#         print("show button tapped! ")
#         """
#         Need to implement 
#         """
#     def display_video_frame(self, img):
#         if isinstance(img, QImage):  # img가 QImage인 경우
#             pixmap = QPixmap.fromImage(img)
#         elif isinstance(img, QPixmap):  # img가 이미 QPixmap이면 변환 필요 없음
#             pixmap = img
#         else:
#             print("❌ Error: img 타입이 QImage나 QPixmap이 아닙니다.")
#             return

#         self.lb_cam.setPixmap(pixmap)

#     def resume_camera(self):
#         print("🎬 Video done. Switching back to camera.")
#         self.lb_cam.clear()
#         self.lb_cam.setPixmap(QPixmap())
#         self.lb_cam.show()
#         self.timer.start(30)

#     def count(self):
#         if client.tcp.result == 'up':
#             #print(self.tcp.result)
#             self.count_up+=1

#     def update_gui(self):
#         if self.camera.frame is not None:
#             frame_copy = self.camera.frame.copy()
#             # 1. Mediapipe로 손 키포인트 추출
#             frame = self.hand_detector.findHands(self.camera.frame, draw=False)
#             lmList = self.hand_detector.findPosition(frame, draw=False)
#             Detector.analyze_user(frame)

#             hands.set()
#             # 👆 손가락 제스처로 운동 선택
#             if self.is_lookup:
#                 number = self.hand_detector.count_fingers(lmList)
#                 cv2.putText(frame, f' {number}', (cons.window_width - 100, 50),
#                             cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

#                 if 1 <= number <= 5:
#                     if self.current_gesture != number:
#                         self.current_gesture = number
#                         self.gesture_start_time = time.time()
#                         self.selection_confirmed = False
#                         print(f"⏳ 숫자 {number} 인식됨. 유지 중...")

#                     elif not self.selection_confirmed and time.time() - self.gesture_start_time >= 5:
#                         print(f"🎯 숫자 {number} 확정됨! 운동 시작.")
#                         self.selection_confirmed = True
#                         self.play_selected_workout(number, self.tier)

#                 else:
#                     # 손가락이 0개이거나 범위 바깥이면 초기화
#                     self.current_gesture = None
#                     self.gesture_start_time = None
#                     self.selection_confirmed = False

#             # 2. 버튼 그리기
#             if self.view:
#                 self.view.appear(frame)
#             if self.modal_pause_view :
#                 self.modal_pause_view.appear(frame)
#             if self.modal_exit_view is not None:
#                 self.modal_exit_view.appear(frame) 

#             # 3. PyQt에 이미지 보여주기
#             img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)

#             self.lb_cam.setPixmap(QPixmap.fromImage(qt_img))
#             if self.camera.is_active == True:
#                 self.udp.send_video(frame_copy)
    
#     def save_video(self):
#         self.udp.video_writer=True
#         data=self.pack_data("RC",data='True')
#         self.tcp.sendData(data)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     client = mainWindow()
#     client.show()
#     sys.exit(app.exec_())
