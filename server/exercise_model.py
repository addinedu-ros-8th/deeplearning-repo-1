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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class ExerciseClassifier:
    def __init__(self, model_path='./exercise_classifier.h5'):
        self.model = load_model(model_path)
        self.sequence = deque(maxlen=20)
        self.lock = threading.Lock()
        self.result = None
        self.exercise_list = ["Standing", "Standing Knee Raise", "Shoulder Press", "Squat", "Side Lunge"]
        self.exercise_count={'Standing Knee Raise':'knee',"Shoulder Press":'shoulder',"Squat":'squat'}
        self.pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.frame_delay = 10
        self.frame_count = 0
        self.label = None
        
        # 같은 운동을 일정 프레임 이상 유지할 때 업데이트
        self.last_exercise = None
        self.consistent_frames = 0
        self.required_frames = 33 # 10프레임 이상 지속되어야 인식

        self.angle_counter = AngleGuid(exercise=None)  # 초기 운동 설정
        
        self.predict_thread = threading.Thread(target=self.run_prediction, daemon=True)
        self.predict_thread.start()
    
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
            with self.lock:
                if len(self.sequence) == 20:
                    input_data = np.array(list(self.sequence)).reshape(1, 20, 24)
                else:
                    input_data = None
            
            if input_data is not None:
                prediction = self.model.predict(input_data, verbose=0)
                self.result = prediction
            else:
                time.sleep(0.01)
    
    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        
        exercise=['shoulder', 'squat', 'knee']
        self.angle_counter.set_exercise(exercise=exercise[0])
        if self.angle_counter.exercise != None:
            self.angle_counter.draw(frame, results.pose_landmarks.landmark)
            cv2.putText(frame, f"Count: {self.angle_counter.get_count()}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        if results.pose_landmarks is None:
            return frame
        
        landmarks = self.extract_pose_landmarks(results)
        with self.lock:
            self.sequence.append(landmarks)
        
        if self.result is not None:
            predict_class = int(np.argmax(self.result))
            predicted_label = self.exercise_list[predict_class]
            try:
                if self.exercise_count[predicted_label] != exercise[0]:
                    #print(predicted_label)
                    self.consistent_frames += 1
                else:
                    self.consistent_frames = 0

                if self.consistent_frames >= self.required_frames:
                    # if self.label != predicted_label:  # 운동이 변경될 때 동작 수행
                    #     self.label = predicted_label
                    self.consistent_frames = 0
                    #print("다른운동하지마세요.")
                    tts_thread = TextToSpeechThread("다른 운동 하지 마세요.")  # TTS 쓰레드 실행
                    tts_thread.start()
            except:
                a=1

            cv2.putText(frame, f"{exercise[0]}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        

        
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        return frame
    

if __name__ == "__main__":
    classifier = ExerciseClassifier()
    classifier.run()