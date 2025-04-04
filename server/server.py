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

class FAAServer(QTcpServer):
    def __init__(self):
        super(FAAServer, self).__init__()
        self.client_list = []
        self.ai_server = AitoMain()
        self.db = FAAdb()
        self.cur = self.db.conn.cursor()

    def start_server(self):
        if self.listen(QHostAddress.Any, SERVER_PORT): print(f"Server listening on port {SERVER_PORT}")
        else: print(f"Failed to listen on port {SERVER_PORT}")

    def incomingConnection(self, socketDescriptor):
        self.client_socket = QTcpSocket(self)
        self.client_socket.setSocketDescriptor(socketDescriptor)
        print(f"클라이언트 연결됨: {self.client_socket.peerAddress().toString()}:{self.client_socket.peerPort()}")

        # 클라이언트 연결 및 데이터 수신, 종료 핸들러 등록
        self.client_socket.readyRead.connect(lambda: self.receive_data(self.client_socket))
        self.client_socket.disconnected.connect(lambda: self.disconnected(self.client_socket))

        self.client_list.append(self.client_socket)
        print(self.client_list)

    def receive_data(self, client_socket):
        while client_socket.bytesAvailable() > 0:
            data = client_socket.readAll().data()
            self.data = self.unpack_data(data)
            print(f"[Server] 클라이언트 메세지 : {self.data}")
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
            elif self.data['command'] == "GR":
                print("루틴 조회 요청")
                self.send_routine()
            
    
    def unpack_data(self, binary_data):
        offset = 0
        
        # 명령어 언팩 (길이 + 데이터)
        command_len = struct.unpack_from('I', binary_data, offset)[0]
        offset += 4
        command = binary_data[offset:offset + command_len].decode('utf-8')
        offset += command_len
        
        def unpack_string():
            nonlocal offset
            length = struct.unpack_from('I', binary_data, offset)[0]
            offset += 4
            if length > 0:
                value = binary_data[offset:offset + length].decode('utf-8')
                offset += length
                return value
            return None
        
        # 각 필드 언팩
        pw = unpack_string()
        name = unpack_string()
        height = unpack_string()  # 높이
        weight = unpack_string()  # 몸무게
        data = unpack_string()
        content = unpack_string()

        # 이미지 데이터 언팩 (이미지 파일을 바이너리로 읽어 반환)
        image_data_len = struct.unpack_from('I', binary_data, offset)[0]
        offset += 4
        if image_data_len > 0:
            image_data = binary_data[offset:offset + image_data_len]
            offset += image_data_len
        else:
            image_data = None
        
        return {
            'command': command,
            'pw': pw,
            'name': name,
            'height': height,
            'weight': weight,
            'data': data,
            'content': content,
            'image_data': image_data
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
        self.cur.execute("SELECT password FROM user where name = %s and password = %s",(self.data['name'],self.data['pw']))
        rows = self.cur.fetchall()
        #print(rows)
        if len(rows) == 0:
            print('로그인정보가 틀렸습니다.')
            data = self.pack_data("LI",status='1',err="Invalid credentials")
        else:
            print(rows[0][0])
            data = self.pack_data("LI",status='0')
        self.send_data(self.client_socket,data)
    
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
               
        self.send_data(self.client_socket,data)
    
    def counting(self,count):
        data = self.pack_data("CT",status=count)
        self.send_data(self.client_list[2],data)
    def record_start(self):
        data = self.pack_data("RC",status='True')
        self.send_data(self.client_list[1],data)
    
    def create_routine(self):
        name = self.data['name']   

        # look up user tier 
        self.cur.execute("SELECT id, tier FROM user WHERE name = %s", (name,))
        result = self.cur.fetchone()
        if not result: 
            data = self.pack_data("RR", status='1')
            print("no user in db")
            self.send_data(self.client_socket, data)
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
            self.send_data(self.client_socket, data)
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
            self.send_data(self.client_socket, data)
            return

        user_id = result[0]

        # 2. 최신 Routine ID 조회
        self.cur.execute("SELECT id FROM routine WHERE user_id = %s ORDER BY date DESC LIMIT 1", (user_id,))
        result = self.cur.fetchone()
        if not result:
            print("❌ Routine 없음")
            data = self.pack_data("GR", status='1', err="Routine 정보가 없습니다.")
            self.send_data(self.client_socket, data)
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
            self.send_data(self.client_socket, data)
            return

        # 4. 문자열 포맷팅 후 전송
        routine_text = '\n'.join([f"{name}: {sets}세트 x {reps}회" for name, sets, reps in routine_data])
        print("Routine 전송:", routine_text)
        data = self.pack_data("GR", status='0', list_data=routine_text)
        self.send_data(self.client_socket, data)


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러

    conn = FAAdb()
    server = FAAServer()
    server.start_server()

    app.exec_()
