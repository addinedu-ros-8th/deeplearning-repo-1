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

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class ExerciseClassifier:
    def __init__(self, model_path='/home/sang/dev_ws/save_file/exercise_classifier.h5'):
        self.model = load_model(model_path)
        self.sequence = deque(maxlen=20)
        self.lock = threading.Lock()
        self.result = None
        self.exercise_list = ["Standing", "Standing Knee Raise", "Shoulder Press", "Squat", "Side Lunge"]
        self.pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.counter = 0
        self.stage = None
        self.frame_delay = 10
        self.frame_count = 0
        self.last_exercise = None
        self.last_tts_time = 0
        
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
    
    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio = AudioSegment.from_file(fp, format="mp3")
        play(audio)
    
    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        if results.pose_landmarks is None:
            return frame
        
        landmarks = self.extract_pose_landmarks(results)
        with self.lock:
            self.sequence.append(landmarks)
        
        if self.result is not None:
            predict_class = int(np.argmax(self.result))
            label = self.exercise_list[predict_class]
            
            if label != self.last_exercise and time.time() - self.last_tts_time > 5:
                threading.Thread(target=self.text_to_speech, args=(label,)).start()
                self.last_exercise = label
                self.last_tts_time = time.time()
            
            cv2.putText(frame, f"{label}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        return frame

if __name__ == "__main__":
    classifier = ExerciseClassifier()
    classifier.run()
