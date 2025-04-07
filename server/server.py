import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
import signal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from config import SERVER_PORT
from database import FAAdb
import struct
import random 
import datetime 
from functools import partial
import json
import socket 
from client_info import ClientInfo

class FAAServer(QTcpServer):
    def __init__(self):
        super(FAAServer, self).__init__()
        self.client_list = []
        #self.ai_server = AitoMain()
        self.db = FAAdb()
        self.cur = self.db.conn.cursor(buffered=True)
        
        self.score = 0
        self.ai_socket= None

    def start_server(self):
        if self.listen(QHostAddress.Any, SERVER_PORT): print(f"Server listening on port {SERVER_PORT}")
        else: print(f"Failed to listen on port {SERVER_PORT}")

    def incomingConnection(self, socketDescriptor):
        client_socket = QTcpSocket(self)
        client_socket.setSocketDescriptor(socketDescriptor)
        print(f"클라이언트 연결됨: {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")
        
        ClientInfo(client_socket)

        # 각 소켓에 대해 개별적으로 처리되도록 설정
        client_socket.readyRead.connect(partial(self.receive_data, client_socket))
        client_socket.disconnected.connect(partial(self.disconnected, client_socket))

    def receive_data(self, client_socket):
        while client_socket.bytesAvailable() > 0:
            data = client_socket.readAll().data()
            print(data)
            # AI 서버가 자기소개 할 경우
            if data == b'AI_HELLO':
                self.ai_socket = client_socket
                ClientInfo.remove_client(client_socket)
                print(f"[Server] AI 서버로 등록됨: {client_socket.peerAddress().toString()}")
                return
            
            # JSON 형식인 경우 예외적으로 로그만 찍고 무시
            if data.startswith(b'{'):
                try:
                    json_str = data.decode('utf-8')
                    json_data = json.loads(json_str)
                    if json_data.get('command') == 'PI':
                        # print(f"[Server] [JSON - PI 명령 수신]: {json_data}")
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
                    self.login(client_socket)
                elif self.data['command'] == "RG":
                    print("회원가입")
                    self.register(client_socket)
                elif self.data['command'] == "CT":
                    print("카운팅")
                    self.counting(client_socket, self.data['data'])
                elif self.data['command'] == "RC":
                    print("녹화시작")
                    self.record_start()
                elif self.data['command'] == "RR":
                    print("루틴 생성 요청")
                    self.create_routine(client_socket)

                elif self.data['command'] == 'GR':
                    self.send_routine(client_socket)
                elif self.data['command'] == 'CR':
                    print(self.data)
                    self.draw_guidline()
                elif self.data['command'] == "ME":
                    self.modify_exercise(client_socket)
            except Exception as e:
                print(f"[✗] 바이너리 데이터 처리 오류: {e}")

    def send_exercise_to_ai(self, exercise):
        try:
            if self.ai_socket and self.ai_socket.state() == QTcpSocket.ConnectedState:
                json_msg = json.dumps({"command": "EX", "exercise": exercise})
                self.ai_socket.write(json_msg.encode('utf-8'))
                self.ai_socket.flush()
                print(f"[Server] AI 서버에게 운동 전송: {exercise}")
            else:
                print("[Server] AI 소켓이 연결되지 않았습니다.")
        except Exception as e:
            print(f"[Server] AI 운동 전송 실패: {e}")        
    
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
        status = unpack_string()
        pw = unpack_string()
        name = unpack_string()
        height = unpack_string()
        weight = unpack_string()
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
            'status': status,
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
    
    def send_data(self, client_socket, response_data):
        if client_socket.state() == QTcpSocket.ConnectedState:
            client_socket.write(response_data)
            client_socket.flush()
            # print(f"[Server] 클라이언트로 응답 전송: {response_data}")
        else:
            print("[Server] 클라이언트와의 연결이 끊어져 응답을 전송할 수 없습니다.")

    def disconnected(self, client_socket):
        client_socket = self.sender()  # 현재 신호를 보낸 객체 가져오기
        if isinstance(client_socket, QTcpSocket):
            print("[Server] Client disconnected:", client_socket.peerAddress().toString())
        ClientInfo.remove_client(client_socket)
        client_socket.deleteLater()  # 안전하게 객체 삭제
    
    def login(self, socket):
        if self.data['status'] == '0':
            self.cur.execute("SELECT id, name, weight, height, tier, score FROM user where name = %s and password = %s",(self.data['name'],self.data['pw']))
            rows = self.cur.fetchone()

            if rows is None:
                data = self.pack_data("LI",status='1', err="Invalid credentials")
            else:
                ClientInfo.set_user_info(socket, rows[0], rows[1], rows[2], rows[3], rows[4], rows[5])
                list_data = str(rows[2]) + "," + str(rows[3]) + "," + str(rows[4]) + "," + str(rows[5])
                data = self.pack_data("LI", status='0', name=rows[1], id=str(rows[0]), list_data=list_data)
            self.send_data(socket, data)
    
    def register(self, socket):
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM user WHERE name = %s)",(self.data['name'],))
        duplication_name = int(self.cur.fetchall()[0][0])

        print(duplication_name)
        if duplication_name == 1:
            data = self.pack_data("RG",status='1')
        
        if duplication_name == 0:
            self.cur.execute("insert into user(name, height, weight, user_icon, password) values(%s, %s, %s, %s, %s)",(self.data['name'],int(self.data['height']),int(self.data['weight']),self.data['image_data'], self.data['pw']))
            self.db.commit()
            data = self.pack_data("RG",status='0')
               
        self.send_data(socket, data)
    
    def counting(self, socket, count):
        data = self.pack_data("CT",status=count)
        self.send_data(socket,data)

    def record_start(self):
        if self.data['data'] == 'True':
            data = self.pack_data("RC",status='True')
            self.send_data(self.ai_socket, data)
        elif self.data['data'] == 'False':
            data = self.pack_data("RC",status='False')
            self.send_data(self.ai_socket,data)
    
    def create_routine(self, socket):
        name = self.data['name']   

        # look up user tier 
        # self.cur.execute("SELECT id, tier FROM user WHERE name = %s", (name,))
        # result = self.cur.fetchone()
        # if not result: 
        #     data = self.pack_data("RR", status='1')
        #     print("no user in db")
        #     self.send_data(socket, data)
        #     return 
        
        # user_id, tier = result
        # print(f"DEBUG, ID: {user_id}, 티어: {tier}")

        user_id = ClientInfo.get_user_id(socket)
        tier = ClientInfo.get_tier(socket)

        # does the routine duplicate ? 
        today = datetime.datetime.now().date()  # 현재 날짜
        self.cur.execute("SELECT id FROM routine WHERE user_id = %s AND DATE(date) = %s", 
                                            (user_id, today))
        existing = self.cur.fetchone()
        if not existing:
            print("금일 routine 이미 존재")
            # data = self.pack_data("RR", status='1')         # duplicate 
            # self.send_data(socket, data)
            self.cur.execute("INSERT INTO routine (user_id, status, date) VALUES (%s, %s, %s)",
                                                        (user_id, 0, datetime.datetime.now()))
            routine_id = self.cur.lastrowid

            # get a list of exercises that fit one's tier 
            self.cur.execute("SELECT id, name, reps FROM workout WHERE tier = %s", (tier,))
            workout_list = self.cur.fetchall()
            selected_workouts = workout_list

            # add single routine in routine_workout table 
            for workout_id, workout_name, reps in selected_workouts:
                sets = random.randint(3, 5)
                self.cur.execute("INSERT INTO routine_workout (routine_id, workout_id, sets, status) VALUES (%s, %s, %s, %s)",
                                (routine_id, workout_id, sets, 0))
            self.db.commit()

            print("Routine 생성 완료")

        sql = """
            SELECT rw.id, w.name, rw.sets, w.reps
            FROM routine r, routine_workout rw, workout w
            where Date(r.date) = %s
            and r.user_id = %s
            and rw.routine_id = r.id
            and rw.workout_id = w.id
            """
        self.cur.execute(sql, (today, user_id))
        results = self.cur.fetchall()
        
        formatted = ",".join([f"{id}|{name}|{sets}|{reps}" for id, name, sets, reps in results])
        for item in formatted.split(','):
            id, name, sets, reps = item.strip().split('|')
            ClientInfo.set_routine(socket, {
                'id': id,
                'name': name,
                'sets': int(sets),
                'reps': int(reps)
            })

        data = self.pack_data("RR", status='0', list_data=formatted)
        self.send_data(socket, data)

    def modify_exercise(self, socket):
        status = self.data['status']

        if status == '0': # 운동 정보 요청
            self.cur.execute("SELECT * from workout")
            result = self.cur.fetchall()
            if not result:
                data = self.pack_data("ME", status=9, err="운동 정보가 없습니다.")
                self.send_data(socket, data)
                return
            
            tmp = ""
            for data in result:
                for tmp2 in data:
                    tmp += str(tmp2) + ","
                tmp += "\n"

            self.send_data(socket, self.pack_data("ME", status='0', list_data=tmp))
        elif status == '1': # 운동 정보 추가
            data = self.data['data'].split(",")

            exercise_name = data[0]
            tier = data[1]
            reps = data[2][:-1]
            score = data[3][:-1]

            try:
                self.cur.execute("INSERT INTO workout (name, tier, reps, score) VALUES (%s, %s, %s, %s)", (exercise_name, tier, reps, score))
                self.db.commit()

                data = self.pack_data("ME", status='1')
                self.send_data(socket, data)
            except:
                data = self.pack_data("ME", status='9')
                self.send_data(socket, data)
                return
            
        elif status == '2': # 운동 정보 수정
            data = self.data['data'].split(",")

            try:
                self.cur.execute("UPDATE workout SET tier = %s, reps = %s, score = %s WHERE name = %s", (data[1], data[2], data[3], data[0]))
                self.db.commit()

                data = self.pack_data("ME", status='2')
                self.send_data(socket, data)
            except:
                data = self.pack_data("ME", status='9')
                self.send_data(socket, data)
        elif status == '3': # 운동 정보 삭제
            data = self.data['data']
            
            try:
                self.cur.execute("DELETE FROM workout WHERE name = %s", (data,))
                self.db.commit()

                data = self.pack_data("ME", status='3')
                self.send_data(socket, data)
            except:
                data = self.pack_data("ME", status='9')
                self.send_data(socket, data)

    def send_routine(self, socket):
        name = self.data['name']

        # 1. user ID 조회
        # self.cur.execute("SELECT id FROM user WHERE name = %s", (name,))
        # result = self.cur.fetchone()
        # if not result:
        #     print("❌ User 없음")
        #     data = self.pack_data("GR", status='1', err="User를 찾을 수 없습니다.")
        #     self.send_data(socket, data)
        #     return

        # user_id = result[0]
        user_id = ClientInfo.get_user_id(socket)

        # 2. 최신 Routine ID 조회
        self.cur.execute("SELECT id FROM routine WHERE user_id = %s ORDER BY date DESC LIMIT 1", (user_id,))
        result = self.cur.fetchone()
        if not result:
            print("❌ Routine 없음")
            data = self.pack_data("GR", status='1', err="Routine 정보가 없습니다.")
            self.send_data(socket, data)
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
            self.send_data(socket, data)
            return

        # 4. 문자열 formatiing 후 client에게 전송
        formatted = ",".join([f"{name}|{sets}|{reps}" for name, sets, reps in routine_data])
        print("Routine 전송:", formatted)
        ai_routine = ",".join([f"{name.lower().replace(' ', '')}|{sets}|{reps}" for name, sets, reps in routine_data])
        self.send_routine_to_ai(ai_routine)
        data = self.pack_data("GR", status='0', list_data=formatted)
        self.send_data(socket, data)


    def send_routine_to_ai(self, routine_str):
        try:
            ai_ip = "127.0.0.1"
            ai_port = 9999  # ai_server.py에서 열어둔 포트
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ai_ip, ai_port))
            sock.send(routine_str.encode('utf-8'))
            sock.close()
            print("[Main Server] AI 서버에 루틴 전송 완료 (TCP):", routine_str)
        except Exception as e:
            print(f"[Main Server] 루틴 전송 실패: {e}")


    
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
