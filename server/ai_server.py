import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
import numpy as np
import cv2
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QTcpSocket
from PyQt5.QtCore import QByteArray
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
import mediapipe as mp
import struct
from counting import Counting
#from socket_client import Client
from ai_to_main import AitoMain

# from file_client import FileClient


class AiServer(QWidget):
    def __init__(self, port=12345):
        super().__init__()
        self.udp_socket = QUdpSocket()
        self.udp_socket.bind(QHostAddress.Any, port)
        self.udp_socket.readyRead.connect(self.receive_data)

        self.tcp = AitoMain()
        self.counting = Counting(self.on_counter_increase)
        # self.file_server = FileClient()

        print(f"[UDP Server] Listening for video on port {port}...")

        # UI 설정
        self.setWindowTitle("UDP Video Server")
        self.setGeometry(200, 200, 640, 480)
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # self.file_server = FileClient()
        # self.write_status=False

    def on_counter_increase(self, count):
        """ 카운터가 증가할 때 실행될 함수 """
        print(f"[AiServer] 카운트 증가 감지! 현재 카운트: {count}")
        command = self.pack_data("CT",data=str(count))
        self.tcp.sendData(command)
        
    def receive_data(self):
        while self.udp_socket.hasPendingDatagrams():
            data, sender, sender_port = self.udp_socket.readDatagram(self.udp_socket.pendingDatagramSize())

            # 받은 데이터를 프레임으로 변환
            self.process_video_frame(data)

    def process_video_frame(self, frame_bytes):
        """ 수신한 비디오 프레임을 디코딩 후 화면에 표시 """
        try:
            # bytes → numpy 배열 변환 후 디코딩
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

            if frame is None:
                print("[UDP Server] Failed to decode frame")
                return

            frame = self.counting.process_pose(frame)
            self.display_frame(frame)


            # 바로 파일 서버로 전송
            # if self.write_status == True:
            #     self.send_video_to_server(frame)

        except Exception as e:
            print(f"[UDP Server] Error processing frame: {e}")
    
    # def send_video_to_server(self, frame):
    #     """ 프레임을 파일 서버로 직접 전송 """
    #     try:
    #         # OpenCV frame을 JPEG 형식으로 인코딩하여 바이트 데이터로 변환
    #         ret, encoded_frame = cv2.imencode('.jpg', frame)

    #         if ret:
    #             frame_bytes = encoded_frame.tobytes()

    #             # 파일 서버로 전송
    #             #self.file_server.send_video(frame_bytes)  # send_video()는 비디오 데이터를 서버로 전송하는 메서드
    #             self.write_status=False

    #     except Exception as e:
    #         print(f"[UDP Server] Error sending video to server: {e}")
    
    def display_frame(self, frame):
        """ OpenCV 프레임을 QLabel에 표시 """
        # OpenCV에서 읽어온 BGR 이미지를 RGB로 변환
        
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        q_img = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # QLabel에 QPixmap을 설정
        self.label.setPixmap(QPixmap.fromImage(q_img))
        self.label.repaint()  # 화면 갱신
    
    def pack_data(self, command, id=None,pw=None,name=None,email=None,data=None,content=None):
        packed_data = b''
        
        # 명령어 패킹 (길이 + 데이터)
        packed_data += struct.pack('I', len(command)) + command.encode('utf-8')
        
        # ID 패킹 (길이 + 데이터)
        if id is not None:
            packed_data += struct.pack('I', len(id)) + id.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 비밀번호 패킹 (길이 + 데이터)
        if pw is not None:
            packed_data += struct.pack('I', len(pw)) + pw.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이름 패킹 (길이 + 데이터)
        if name is not None:
            packed_data += struct.pack('I', len(name.encode('utf-8'))) + name.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이메일 패킹 (길이 + 데이터)
        if email is not None:
            packed_data += struct.pack('I', len(email)) + email.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 데이터 패킹
        if data is not None:
            data_bytes = data.encode('utf-8')
            packed_data += struct.pack('I', len(data_bytes)) + data_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        # 콘텐트 패킹
        if content is not None:
            content_bytes = content.encode('utf-8')
            packed_data += struct.pack('I', len(content_bytes)) + content_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        
        return packed_data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = AiServer(port=12345)
    server.show()
    sys.exit(app.exec_())
