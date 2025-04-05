import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
import signal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from config import SERVER_PORT
from database import FAAdb
from client.ai_to_main import AitoMain
import struct
import random 
import datetime 
from functools import partial
import json

class FAAServer(QTcpServer):
    def __init__(self):
        super(FAAServer, self).__init__()
        self.client_list = []
        #self.ai_server = AitoMain()
        self.db = FAAdb()
        self.cur = self.db.conn.cursor()

        self.name=None
        self.score = 0

    def start_server(self):
        if self.listen(QHostAddress.Any, SERVER_PORT): print(f"Server listening on port {SERVER_PORT}")
        else: print(f"Failed to listen on port {SERVER_PORT}")

    def incomingConnection(self, socketDescriptor):
        client_socket = QTcpSocket(self)
        client_socket.setSocketDescriptor(socketDescriptor)
        print(f"클라이언트 연결됨: {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")

        # 각 소켓에 대해 개별적으로 처리되도록 설정
        client_socket.readyRead.connect(partial(self.receive_data, client_socket))
        client_socket.disconnected.connect(partial(self.disconnected, client_socket))

        self.client_list.append(client_socket)
        print(self.client_list)

    def receive_data(self, client_socket):
        while client_socket.bytesAvailable() > 0:
            data = client_socket.readAll().data()

            # JSON 형식인 경우 예외적으로 로그만 찍고 무시
            if data.startswith(b'{'):
                try:
                    json_str = data.decode('utf-8')
                    json_data = json.loads(json_str)
                    if json_data.get('command') == 'PI':
                        print(f"[Server] [JSON - PI 명령 수신]: {json_data}")
                        self.send_data(self.client_list[3],data)
                        current_count = json_data.get('count')

                        # 이전 count와 비교해서 20 -> 0으로 떨어졌는지 확인
                        if hasattr(self, 'prev_count') and self.prev_count == 20 and current_count == 0:
                            self.score += 10
                            self.cur.execute("UPDATE user SET score = %s WHERE name = %s", (self.score, self.name))
                            self.db.commit()
                            print(f"[Server] 🎯 점수 증가! 현재 점수: {self.score}")

                        # 현재 count 값을 다음 비교를 위해 저장
                        self.prev_count = current_count
                    else:
                        print(f"[Server] [무시된 JSON 명령]: {json_data.get('command')}")
                    return
                except Exception as e:
                    print(f"[!] JSON 형식으로 보이지만 파싱 실패: {e}")
                    return

            # ✅ 나머지는 전부 바이너리라고 보고 기존 방식대로 처리
            try:
                self.data = self.unpack_data(data)
                print(f"[Server] 클라이언트 바이너리 메시지: {self.data}")

                if self.data['command'] == "LI":
                    print("로그인")
                    self.login()
                elif self.data['command'] == "RG":
                    print("회원가입")
                    self.register()
                elif self.data['command'] == "CT":
                    print("카운팅")
                    self.counting(self.data['data'])
                elif self.data['command'] == "RC":
                    print("녹화시작")
                    self.record_start()
                elif self.data['command'] == "RR":
                    print("루틴 생성 요청")
                    self.create_routine()
                elif self.data['command'] == 'CR':
                    print(self.data )
                    self.draw_guidline()
                elif self.data['command'] == 'GR':
                    self.send_routine()

            except Exception as e:
                print(f"[✗] 바이너리 데이터 처리 오류: {e}")
            
    def unpack_data(self, binary_data):
        offset = 0

        def unpack_string():
            nonlocal offset
            length = struct.unpack_from('I', binary_data, offset)[0]
            offset += 4
            if length > 0:
                value = binary_data[offset:offset + length].decode('utf-8')
                offset += length
                return value
            return None

        # 명령어 언팩
        command = unpack_string()
        pw = unpack_string()
        name = unpack_string()
        height = unpack_string()  # 높이
        weight = unpack_string()  # 몸무게
        data = unpack_string()
        content = unpack_string()

        # 이미지 데이터 언팩
        image_data_len = struct.unpack_from('I', binary_data, offset)[0]
        offset += 4
        image_data = binary_data[offset:offset + image_data_len] if image_data_len > 0 else None
        offset += image_data_len if image_data_len > 0 else 0

        # joint 리스트 언팩
        joint_len = struct.unpack_from('I', binary_data, offset)[0]
        offset += 4
        joint = [struct.unpack_from('I', binary_data, offset + (i * 4))[0] for i in range(joint_len)]
        offset += joint_len * 4

        # ✅ angle 언팩 (람다로 변환하되, 출력 시 문자열 유지)
        angle_str = unpack_string()
        if angle_str:
            try:
                angle = eval(angle_str)  # 람다로 변환
            except:
                angle = angle_str  # 변환 실패하면 문자열 유지
        else:
            angle = None

        # ✅ 로그 출력용 (람다 함수일 경우 문자열로 변환)
        angle_display = angle_str if isinstance(angle, str) else f"lambda function ({angle_str})"

        print(f"[Server] 클라이언트 메세지 : {{'command': {command}, 'angle': {angle_display}}}")

        return {
            'command': command,
            'pw': pw,
            'name': name,
            'height': height,
            'weight': weight,
            'data': data,
            'content': content,
            'image_data': image_data,
            'joint': joint,
            'angle': angle
        }

    def pack_data(self, command, status=None, name=None, err=None, id=None, list_data=None, routine_number=None, total_day=None, total_time=None,email=None):
        packed_data = b''
        
        # 명령어 패킹 (길이 + 데이터)
        packed_data += struct.pack('I', len(command)) + command.encode('utf-8')
        
        # ID 패킹 (길이 + 데이터)
        if id is not None:
            packed_data += struct.pack('I', len(id)) + id.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 상태 패킹 (길이 + 데이터)
        if status is not None:
            packed_data += struct.pack('I', len(status)) + status.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이름 패킹 (길이 + 데이터)
        if name is not None:
            packed_data += struct.pack('I', len(name.encode('utf-8'))) + name.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 에러 메시지 패킹 (길이 + 데이터)
        if err is not None:
            packed_data += struct.pack('I', len(err)) + err.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 리스트 데이터 패킹
        if list_data is not None:
            list_bytes = list_data.encode('utf-8')
            packed_data += struct.pack('I', len(list_bytes)) + list_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        # 루틴 번호 패킹
        if routine_number is not None:
            packed_data += struct.pack('I', len(routine_number)) + routine_number.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 총 일수 패킹
        if total_day is not None:
            packed_data += struct.pack('I', len(total_day)) + total_day.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 총 시간 패킹
        if total_time is not None:
            packed_data += struct.pack('I', len(total_time)) + total_time.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        if email is not None:
            packed_data += struct.pack('I', len(email)) + email.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        return packed_data
    
    def send_data(self,client_socket, response_data):
        if client_socket.state() == QTcpSocket.ConnectedState:
            client_socket.write(response_data)
            client_socket.flush()
            print(f"[Server] 클라이언트로 응답 전송: {response_data}")
        else:
            print("[Server] 클라이언트와의 연결이 끊어져 응답을 전송할 수 없습니다.")

    def disconnected(self, client_socket):
        client_socket = self.sender()  # 현재 신호를 보낸 객체 가져오기
        if isinstance(client_socket, QTcpSocket):
            print("[Server] Client disconnected:", client_socket.peerAddress().toString())
        client_socket.deleteLater()  # 안전하게 객체 삭제
    
    def login(self):
        self.name=self.data['name']
        self.cur.execute("SELECT password FROM user where name = %s and password = %s",(self.data['name'],self.data['pw']))
        rows = self.cur.fetchall()
        #print(rows)
        if len(rows) == 0:
            print('로그인정보가 틀렸습니다.')
            data = self.pack_data("LI",status='1',err="Invalid credentials")
        else:
            print(rows[0][0])
            data = self.pack_data("LI",status='0')
        self.send_data(self.client_list[3],data)
    
    def register(self):
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM user WHERE name = %s)",(self.data['name'],))
        duplication_name = int(self.cur.fetchall()[0][0])

        print(duplication_name)
        if duplication_name == 1:
            data = self.pack_data("RG",status='1')
        
        if duplication_name == 0:
            self.cur.execute("insert into user(name, height, weight, user_icon, password) values(%s, %s, %s, %s, %s)",(self.data['name'],int(self.data['height']),int(self.data['weight']),self.data['image_data'], self.data['pw']))
            self.db.commit()
            data = self.pack_data("RG",status='0')
               
        self.send_data(self.client_list[3],data)
    
    def counting(self,count):
        data = self.pack_data("CT",status=count)
        self.send_data(self.client_list[3],data)

    def record_start(self):
        if self.data['data'] == 'True':
            data = self.pack_data("RC",status='True')
            self.send_data(self.client_list[0],data)
        elif self.data['data'] == 'False':
            data = self.pack_data("RC",status='False')
            self.send_data(self.client_list[0],data)
    
    def create_routine(self):
        name = self.data['name']   

        # look up user tier 
        self.cur.execute("SELECT id, tier FROM user WHERE name = %s", (name,))
        result = self.cur.fetchone()
        if not result: 
            data = self.pack_data("RR", status='1')
            print("no user in db")
            self.send_data(self.client_list[3], data)
            return 
        
        user_id, tier = result
        print(f"DEBUG, ID: {user_id}, 티어: {tier}")

        # insert routine
        self.cur.execute("INSERT INTO routine (user_id, status, date) VALUES (%s, %s, %s)",
                                                    (user_id, 0, datetime.datetime.now()))
        routine_id = self.cur.lastrowid

        # get a list of exercises that fit one's tier 
        self.cur.execute("SELECT id, name, reps FROM workout WHERE tier = %s", (tier,))
        workout_list = self.cur.fetchall()
        if not workout_list :
            print("운동 없음")
            data = self.pack_data("RR", status='1')
            self.send_data(self.client_list[3], data)
            return 
        # select workout randomly 
        selected_workouts = workout_list

        # add single routine in routine_workout table 
        for workout_id, workout_name, reps in selected_workouts:
            sets = random.randint(3, 5)
            self.cur.execute("INSERT INTO routine_workout (user_id, routine_id, workout_id, sets, status) VALUES (%s, %s, %s, %s, %s)",
                            (user_id,routine_id, workout_id, sets, 0)) 

        self.db.commit()
        print("Routine 생성 완료")
        # data = self.pack_data("RR", status='0')
        # self.send_data(self.client_socket, data)

    def send_routine(self):
        name = self.data['name']

        # 1. user ID 조회
        self.cur.execute("SELECT id FROM user WHERE name = %s", (name,))
        result = self.cur.fetchone()
        if not result:
            print("❌ User 없음")
            data = self.pack_data("GR", status='1', err="User를 찾을 수 없습니다.")
            self.send_data(self.client_list[3], data)
            return

        user_id = result[0]

        # 2. 최신 Routine ID 조회
        self.cur.execute("SELECT id FROM routine WHERE user_id = %s ORDER BY date DESC LIMIT 1", (user_id,))
        result = self.cur.fetchone()
        if not result:
            print("❌ Routine 없음")
            data = self.pack_data("GR", status='1', err="Routine 정보가 없습니다.")
            self.send_data(self.client_list[3], data)
            return

        routine_id = result[0]

        # 3. Routine 상세 운동 정보 조회
        self.cur.execute("""
            SELECT w.name, rw.sets, w.reps
            FROM routine_workout rw
            JOIN workout w ON rw.workout_id = w.id
            WHERE rw.routine_id = %s
        """, (routine_id,))
        routine_data = self.cur.fetchall()

        if not routine_data:
            print("❌ Routine 내용 없음")
            data = self.pack_data("GR", status='1', err="Routine 상세 정보가 없습니다.")
            self.send_data(self.cclient_list[3], data)
            return
        
        # 4. 문자열 포맷으로 보냄 (ex: "squat|3|15, push-up|4|12")
        formatted = ",".join([f"{name}|{sets}|{reps}" for name, sets, reps in routine_data])
        print("Routine 전송:", formatted)
        data = self.pack_data("GR", status='0', list_data=formatted)
        self.send_data(self.client_list[3], data)
        self.send_data(self.client_socket, data)

    def draw_guidline(self):
        #print(self.data['joint'])
        left_joint = self.data['joint'][:3]
        right_joint = self.data['joint'][3:]
        joint = [tuple(left_joint), tuple(right_joint)]
        print(joint)
        
    

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러

    conn = FAAdb()
    server = FAAServer()
    server.start_server()

    app.exec_()