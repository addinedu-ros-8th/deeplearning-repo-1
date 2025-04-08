import socket
import json
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import SERVER_PORT, SERVER_IP

class LandmarkSender:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.sock = self.connect()

    def connect(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            print(f"[✓] 서버에 연결됨: {self.host}:{self.port}")
            return sock
        except Exception as e:
            print("[✗] 서버 연결 실패:", e)
            return None

    def send_pose_data(self, user_id, origin, vector, pts):
        if self.sock is None:
            print("소켓이 없음. 데이터 전송 불가.")
            return

        data = {
            "command": "PI",
            "user_id": user_id,
            "origin": {"x": int(origin[0]), "y": int(origin[1])},
            "vector": {"x": int(vector[0]), "y": int(vector[1])},
            "landmarks": [
                {"x": int(pt[0]), "y": int(pt[1])}
                for pt in pts
            ]
        }

        json_str = json.dumps(data)
        try:
            self.sock.sendall((json_str + '\n').encode('utf-8'))  # \n 구분자
            # print("[→] 데이터 전송 완료")
        except Exception as e:
            print("[✗] 데이터 전송 실패:", e)

    def close(self):
        if self.sock:
            self.sock.close()
            print("[✦] 소켓 연결 종료")


# 🔹 사용 예시 (직접 실행 시)
# if __name__ == "__main__":
#     sender = LandmarkSender()

#     # 테스트용 dummy 데이터
#     origin = (100, 200)
#     vector = (150, 250)
#     pts = [(120, 180), (140, 200), (160, 220)]

#     while True:
#         sender.send_pose_data(origin, vector, pts)
#         time.sleep(1)

    # sender.close()  # 필요 시 종료
