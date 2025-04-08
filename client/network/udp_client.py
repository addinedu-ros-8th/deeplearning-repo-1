import cv2
import sys
import numpy as np
from PyQt5.QtNetwork import QUdpSocket, QHostAddress
from PyQt5.QtCore import QCoreApplication

class UdpClient:
    def __init__(self, server_ip="127.0.0.1", server_port=12345):
        self.udp_socket = QUdpSocket()
        self.server_ip = QHostAddress(server_ip)
        self.server_port = server_port
        #self.cap = cv2.VideoCapture(0)  # 웹캠 열기

    def send_video(self, frame, exercise, user_id):
        """ 웹캠에서 프레임을 읽고 UDP로 전송 """
        if frame is None:
            print("[UDP Client] No frame to send")
            return

        # frame = cv2.resize(frame, (640, 640))
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        image_bytes = buffer.tobytes()
        
        img_len = len(image_bytes)
        img_len_bytes = img_len.to_bytes(4)

        frame_bytes = img_len_bytes + image_bytes + exercise.encode('utf-8') + b'||' + user_id.encode('utf-8')
        
        self.udp_socket.writeDatagram(frame_bytes, self.server_ip, self.server_port)
    
    def close(self):
        """ 클라이언트 종료 """
        self.cap.release()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    client = UdpClient(server_ip="127.0.0.1", server_port=12345)

    try:
        client.send_video()
    except KeyboardInterrupt:
        print("[UDP Client] Stopping...")
        client.close()
