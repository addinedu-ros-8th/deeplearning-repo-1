import cv2
import numpy as np
import mediapipe as mp
import threading
import time
import tempfile
import os
import io
from collections import deque
from keras.models import load_model
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from counting import AngleGuid
from tts import TextToSpeechThread
import sys
import  Constants as cons

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class ExerciseClassifier:
    def __init__(self, clients, model_path='./exercise_classifier.h5'):
        self.model = load_model(model_path)
        # self.sequence = deque(maxlen=20)
        # self.lock = threading.Lock()
        self.result = None
        self.pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.exercise_list = ["knee", "shoulder", "squat", "lunge"]
        self.exercise_count={'Standing Knee Raise':'knee',"Shoulder Press":'shoulder',"Squat":'squat'}
        
        # self.frame_delay = 10
        # self.frame_count = 0
        # self.label = None

        self.sequence_size = 30
        
        self.current_routine_idx = 0
        self.current_set = 1
        self.reps_done = 0
        self.break_active = False
        self.break_end_time = 0
        self.tts_active = False
        
        # 같은 운동을 일정 프레임 이상 유지할 때 업데이트
        self.last_exercise = None
        self.consistent_frames = 0
        self.correct = 0
        self.required_frames = 33 # 10프레임 이상 지속되어야 인식
        self.clients = clients
        self.angle_counter = AngleGuid(exercise=None)  # 초기 운동 설정
        
        self.predict_thread = threading.Thread(target=self.run_prediction, daemon=True)
        # self.predict_thread.start()
        self.tts_thread = TextToSpeechThread()
        
        
        self.routine_list = []

    def run_thread(self):
        self.predict_thread.start()

    def set_routine(self, routine):
        self.routine_list = routine
        self.current_routine_idx = 0
        self.current_set = 1
        self.reps_done = 0
        print("[Model] 루틴 저장됨:", self.routine_list)
    
    def get_current_exercise(self):
        if self.current_routine_idx < len(self.routine_list):
            return self.routine_list[self.current_routine_idx]
        return None

    def extract_pose_landmarks(self, results):
        xyz_list = []
        points = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        lm = results.pose_landmarks.landmark
        neck_x = (lm[11].x + lm[12].x) / 2
        neck_y = (lm[11].y + lm[12].y) / 2
        for idx in points:
            x = lm[idx].x - neck_x
            y = lm[idx].y - neck_y
            xyz_list.append([x, y])
        return xyz_list
    
    def run_prediction(self):
        while True:
            for user_id, client in self.clients.items():
                with client.get_lock():
                    if len(client.sequence) == self.sequence_size:
                        input_data = np.array(list(client.sequence)).reshape(1, self.sequence_size, 24)
                    else:
                        input_data = None
                
                if input_data is not None:
                    prediction = self.model.predict(input_data, verbose=0)
                    self.result = prediction
                else:
                    time.sleep(0.01)

    def update_routine_index(self, index):
        self.current_routine_idx = index
        current = self.get_current_exercise()
        if current:
            kor_name = current["name"]
            eng_name = cons.EXERCISE_NAME_MAP.get(kor_name)
            if eng_name:
                self.angle_counter.set_exercise(eng_name)
                print(f"[Model] 현재 운동으로 변경됨: {eng_name}")
            else:
                print(f"⚠️ 운동 매핑 실패: {kor_name}")

    # def start_break(self):
    #     self.break_active = True
    #     self.break_end_time = time.time() + cons.BREAK_DURATION

    # def check_break(self):
    #     if self.break_active and time.time() >= self.break_end_time:
    #         self.break_active = False
    #         return True
    #     return False
    
    def process_frame(self, client, frame, exercise):
        if self.break_active:
            remaining = int(self.break_end_time - time.time())
            cv2.putText(frame, f"Break Time: {remaining}s", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            return frame
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
       
        # 현재 Routine 정보 
        # current_routine = self.get_current_exercise()
        # if not current_routine: return frame
       
        internal_name = cons.EXERCISE_NAME_MAP.get(exercise)
        if internal_name is None:
            print(f"[UDP Server] 알 수 없는 운동 이름: {exercise}")
            return frame
        self.angle_counter.set_exercise(exercise=internal_name)

        if self.angle_counter.exercise is not None and results.pose_landmarks:
            self.angle_counter.draw(client.get_user_id(), frame, results.pose_landmarks.landmark)
            cv2.putText(frame, f"Count: {self.angle_counter.get_count()}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        
        # landmark append 
        if results.pose_landmarks:
            landmarks = self.extract_pose_landmarks(results)
            with client.get_lock():
                # self.sequence.append(landmarks)
                # ClientInfo.append_image_buffer(user_id, landmarks)
                client.sequence.append(landmarks)
        
        # 운동 판별 
        if self.result is not None:
            predict_class = int(np.argmax(self.result))
            predicted_label = self.exercise_list[predict_class]
            print(predicted_label)
            try:
                # if self.exercise_count.get(predicted_label) != internal_name:
                if internal_name != predicted_label:
                    self.consistent_frames += 1
                else:
                    self.correct += 1
                
                if self.consistent_frames >= self.required_frames:
                    self.consistent_frames = 0
                    self.tts_thread.set_text("회원님 다른운동 하지 마세요.")
                    self.tts_thread.start()
                elif self.correct >= 20:
                    self.correct = 0
                    self.tts_thread.set_text("회원님 잘 하고 있어요.")
                    self.tts_thread.start()

            except Exception as e:
                    print("[Predict Error]", e)
            # cv2.putText(frame, f"{internal_name}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)        
        
        # Count 업데이트
        # if self.angle_counter.exercise:
        #     self.angle_counter.draw(frame, results.pose_landmarks.landmark)
        #     cv2.putText(frame, f"Count: {self.angle_counter.get_count()}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        #     #  남은 개수와 세트 계산
        #     remaining_reps = max(0, current_routine['reps'] - self.angle_counter.get_count())
        #     remaining_sets = max(0, current_routine['sets'] - self.reps_done)

        #     #  OpenCV로 표시
        #     cv2.putText(frame, f"Count: {self.angle_counter.get_count()}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        #     cv2.putText(frame, f"reps: {remaining_reps}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        #     cv2.putText(frame, f"sets: {remaining_sets}", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

        #     # set / 운동 완료 체크
        #     if self.angle_counter.get_count() >= current_routine['reps']:
        #         self.angle_counter.set_count()
        #         self.reps_done += 1
        #         print(f"[Model] 세트 완료 ({self.reps_done}/{current_routine['sets']})")
        #         return "BREAK"
        
        # mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        return frame
    
            # exercise=['shoulder', 'squat', 'knee']
        # self.angle_counter.set_exercise(exercise=exercise[0])
        # if self.angle_counter.exercise != None:
        #     self.angle_counter.draw(frame, results.pose_landmarks.landmark)
        #     cv2.putText(frame, f"Count: {self.angle_counter.get_count()}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        # if results.pose_landmarks is None:
        #     return frame
                # if self.exercise_count[predicted_label] != exercise[0]:
                #     #print(predicted_label)
                #     self.consistent_frames += 1
                # else:
                #     self.consistent_frames = 0

        #         if self.consistent_frames >= self.required_frames:
        #             # if self.label != predicted_label:  # 운동이 변경될 때 동작 수행
        #             #     self.label = predicted_label
        #             self.consistent_frames = 0
        #             #print("다른운동하지마세요.")
        #             tts_thread = TextToSpeechThread("다른 운동 하지 마세요.")  # TTS 쓰레드 실행
        #             tts_thread.start()
        #     except:
        #         a=1

        #     cv2.putText(frame, f"{exercise[0]}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        

        
        # mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        # return frame

if __name__ == "__main__":
    classifier = ExerciseClassifier()
    classifier.run()