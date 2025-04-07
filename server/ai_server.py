import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import cv2
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QTcpSocket
from PyQt5.QtCore import QByteArray, pyqtSignal, QEventLoop
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
import signal
import threading
import time
import socket
from client.file_client import FileClient
from client.ai_to_main import AitoMain
from exercise_model import ExerciseClassifier
# from counting import AngleGuid
import itertools
#from counting import ExerciseCounter
from collections import deque

class ClientInfo():
    def __init__(self, user_id, lock):
        self.user_id = user_id
        self.sequence = deque(maxlen=30)
        self.lock = lock

    def get_user_id(self):
        return self.user_id
    
    def get_lock(self):
        return self.lock
    
    def get_sequence(self):
        return self.sequence

class AiServer(QWidget):
    def __init__(self, port=12345, record_duration=5):
        super().__init__()
        self.udp_socket = QUdpSocket()
        self.udp_socket.bind(QHostAddress.Any, port)
        self.udp_socket.readyRead.connect(self.receive_data)

        self.client = {}
        self.tcp = AitoMain()
        self.model = ExerciseClassifier(self.client)
        self.recording = False
        self.video_writer = None
        self.record_duration = record_duration  # 녹화 간격 (초)
        self.start_time = None
        self.video_filename = None

        self.prev_count=0
        self.prev_exercise=None
        self.routine = {}

        print(f"[UDP Server] Listening for video on port {port}...")

        # UI 설정
        self.setWindowTitle("UDP Video Server")
        self.setGeometry(200, 200, 640, 480)
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 루틴 전용 TCP 서버 실행
        # threading.Thread(target=self.start_routine_server, daemon=True).start()
    
    def start_routine_server(self, host='127.0.0.1', port=9999):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(1)
        print(f"[AI SERVER] 루틴 수신 대기중: {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=self.handle_routine_connection, args=(conn,), daemon=True).start()

    def handle_routine_connection(self, conn):
        try:
            data = conn.recv(2048).decode('utf-8')
            print("[AI SERVER] 수신된 루틴 문자열:", data)
            routine = []
            for item in data.split(','):
                parts = item.split('|')
                if len(parts) == 3:
                    name, sets, reps = parts
                    routine.append({
                        "name": name,
                        "sets": int(sets),
                        "reps": int(reps)
                    })
            if routine:
                self.model.set_routine(routine)
                print("[AI SERVER] 루틴 세팅 완료:", routine)
            else:
                print("[AI SERVER] 파싱된 루틴 없음")
        except Exception as e:
            print("[AI SERVER] 루틴 파싱 실패:", e)
        finally:
            conn.close()   

    def receive_data(self):
        while self.udp_socket.hasPendingDatagrams():
            data, sender, sender_port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())
            
            img_len = int.from_bytes(data[:4])
            img_bytes = data[4:4+img_len]

            text_data = data[4+img_len:].split(b'||')
            exercise = text_data[0].decode('utf-8')
            user_id = text_data[1].decode('utf-8')

            if user_id not in self.client:
                self.lock = threading.Lock()
                self.client[user_id] = ClientInfo(user_id, self.lock)

            client = self.client[user_id]

            self.process_video_frame(client, img_bytes, exercise)
            if not self.model.predict_thread.is_alive():
                self.model.run_thread()

            # QEventLoop가 한 번만 실행되도록 플래그 사용
            # if not hasattr(self, 'loop_ran'):  # loop_ran이 없으면 실행
            #     loop = QEventLoop()
            #     self.tcp.responseReceived.connect(loop.quit)  # 응답 받으면 이벤트 루프 종료
            #     loop.exec_()
            #     self.loop_ran = True  # 한 번 실행 후 플래그 설정
            # #print(self.tcp.result)
            # if self.tcp.result == "True":
            #     pass
            #     # self.process_video_frame(img_bytes, exercise)
            # if self.tcp.result == "False":
            #     self.loop_ran = False

    def process_video_frame(self, client, frame_bytes, exercise):
        """ 수신한 비디오 프레임을 디코딩 후 화면에 표시 및 녹화 """
        try:
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

            if frame is None:
                print("[UDP Server] Failed to decode frame")
                return
            # if self.start == True:

            frame = self.model.process_frame(client, frame, exercise)
            #self.guid = AngleGuid(exercise=None)
            
            self.display_frame(frame)
            self.record_video(frame)

        except Exception as e:
            print(f"[UDP Server] Error processing frame: {e}")

    def record_video(self, frame):
        """ 프레임을 저장하여 녹화 파일 생성 """
        if not self.recording:
            self.start_new_recording(frame)

        self.video_writer.write(frame)
        current_count = self.model.angle_counter.count
        current_exercise = self.model.angle_counter.exercise

        # if self.prev_count != current_count:
        #     self.prev_count = current_count
        #     data=self.tcp.pack_data(command='CT',data=str(self.model.angle_counter.count))
        #     self.tcp.sendData(data)

        if self.prev_exercise != current_exercise:
            # print(self.prev_exercise)
            self.prev_exercise = current_exercise
            # print(self.prev_exercise)
            joint=self.model.angle_counter.joint_map[self.model.angle_counter.exercise]
            joint_list = list(itertools.chain(*joint))

            data=self.tcp.pack_data(command='CR',joint=joint_list,
                                    angle=self.model.angle_counter.guide_angle[self.model.angle_counter.exercise])
            self.tcp.sendData(data)

        if self.model.angle_counter.count >= 20:
            self.stop_and_send_recording()
            self.model.angle_counter.count=0

            print('녹화완료')

    def start_new_recording(self, frame):
        """ 새로운 비디오 파일 생성하여 녹화 시작 """
        self.recording = True
        self.start_time = time.time()
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.video_filename = f"recorded_{timestamp}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        height, width, _ = frame.shape
        self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (width, height))

        print(f"[UDP Server] Started new recording: {self.video_filename}")

    def stop_and_send_recording(self):
        """ 녹화 종료 후 서버로 전송 """
        if self.recording:
            self.recording = False
            self.video_writer.release()
            self.video_writer = None

            print(f"[UDP Server] Stopped recording. Sending {self.video_filename} to server...")

            # 녹화된 파일을 서버로 전송
            self.send_video_to_server(self.video_filename)

    def send_video_to_server(self, video_path):
        """ 녹화된 비디오 파일을 서버로 전송 후 삭제 """
        try:
            if not os.path.exists(video_path):
                print(f"[UDP Server] Error: File {video_path} not found.")
                return

            print(f"[UDP Server] Initializing FileClient to send {video_path}...")

            # 파일 전송을 별도 스레드에서 실행하여 비동기 처리
            threading.Thread(target=self._send_video, args=(video_path,)).start()

        except Exception as e:
            print(f"[UDP Server] Error sending video to server: {e}")

    def _send_video(self, video_path):
        """파일 전송 실행 및 삭제"""
        try:
            file_client = FileClient(file_path=video_path)
            file_client.send_video()

            print(f"[UDP Server] Successfully sent {video_path} to server.")
            os.remove(video_path)  # 전송 완료 후 파일 삭제

        except Exception as e:
            print(f"[UDP Server] Error during file transmission: {e}")

    def display_frame(self, frame):
        """ OpenCV 프레임을 QLabel에 표시 """
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        q_img = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(q_img))
        self.label.repaint()  # 화면 갱신

if __name__ == "__main__":
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러
    server = AiServer(port=12345)
    server.show()
    sys.exit(app.exec_())