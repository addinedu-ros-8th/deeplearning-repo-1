
import cv2
from cv2 import destroyAllWindows
import mediapipe as mp
import numpy as np
import threading
import mediapipe as mp
from gtts import gTTS
import io
from pydub import AudioSegment
from pydub.playback import play

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

class Counting:
    def __init__(self, callback=None):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.counter = 0
        self.stage = None
        self.callback = callback
        self.frame_delay = 10  # 최소 10프레임 지나야 다시 카운트
        self.frame_count = 0  # 프레임 카운터
    
    def input_angle_text(self,image, angle, point,w,h):
        cv2.putText(image, str(angle),
                    (int(point[0] * w), int(point[1] * h)),  # 상대 좌표 → 픽셀 변환
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    
    def input_coordinate_text(self,image, point, w, h):
        cv2.putText(image, str(point),
                    (int(point[0] * w), int(point[1] * h)),  # 상대 좌표 → 픽셀 변환
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    def calculate_angle(self, a, b, c):
        """ 세 점으로 각도 계산 """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle
        return round(angle, 2)

    def process_pose(self, frame):
        """ Mediapipe를 이용해 포즈를 추출하고, 랜드마크를 화면에 그린다 """
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        landmark = self.get_landmark(results)
        self.current_execise('pushup',landmark)

        h, w, _ = image.shape  # 현재 프레임의 높이, 너비
        if self.frame_count < self.frame_delay:  # 카운트된 후 기다림
            self.frame_count += 1
            return

        if landmark['right_shoulder'][0] > landmark['right_hip'][0]:
                    #pushup_elbow_angle_list.append(angle_right_elbow)

            if self.angle_right_elbow > 150:
                self.stage = "up"
                
            if self.angle_right_elbow <= 90 and self.stage == 'up':
                self.stage = "down"
            if self.angle_right_elbow > 140 and self.stage == 'down':
                self.stage = "up"
                self.counter += 1
                self.frame_count = 0
                self.text_to_speech("나덕윤 회원님 한개만 더")
                if self.callback:
                    self.callback(self.counter)

            self.input_angle_text(image, self.angle_right_elbow, landmark['right_elbow'],w,h)
            self.input_coordinate_text(image,landmark['right_knee'],w,h)
            self.input_coordinate_text(image,landmark['right_hip'],w,h)
            self.input_coordinate_text(image,landmark['right_shoulder'],w,h)
        else:
            if self.angle_left_elbow > 150:
                self.stage = "up"
            if self.angle_left_elbow <= 90 and self.stage == 'up':
                self.stage = "down"
            if self.angle_left_elbow > 140 and self.stage == 'down':
                self.stage = "up"
                self.counter += 1
                self.frame_count = 0
                self.text_to_speech("덕윤이형 나이스")
                if self.callback:
                    self.callback(self.counter)
            
            self.input_angle_text(image, self.angle_left_elbow, landmark['left_elbow'],w,h)
            self.input_coordinate_text(image,landmark['left_knee'],w,h)
            self.input_coordinate_text(image,landmark['left_hip'],w,h)
            self.input_coordinate_text(image,landmark['left_shoulder'],w,h)
        
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)    
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2), 
                            mp_drawing.DrawingSpec(color=(203,17,17), thickness=2, circle_radius=2) 
                                )    

        
        return image
    
    def get_landmark(self, results):
        landmarks=results.pose_landmarks.landmark
        landmarks_dict = {
            "right_shoulder": [
                round(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, 2)
            ],
            "left_shoulder": [
                round(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y, 2)
            ],
            "right_elbow": [
                round(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y, 2)
            ],
            "left_elbow": [
                round(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y, 2)
            ],
            "right_wrist": [
                round(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y, 2)
            ],
            "left_wrist": [
                round(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y, 2)
            ],
            "right_hip": [
                round(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, 2)
            ],
            "left_hip": [
                round(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y, 2)
            ],
            "right_knee": [
                round(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, 2)
            ],
            "left_knee": [
                round(landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y, 2)
            ],
            "right_ankle": [
                round(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y, 2)
            ],
            "left_ankle": [
                round(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, 2),
                round(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y, 2)
            ]
        }
    
        return landmarks_dict
    
    def current_execise(self, execise, landmark):
        if execise == 'pushup':
            self.angle_right_elbow = self.calculate_angle(landmark['right_shoulder'],
                                                     landmark['right_elbow'],
                                                     landmark['right_wrist'])
            self.angle_left_elbow = self.calculate_angle(landmark['left_shoulder'],
                                                    landmark['left_elbow'],
                                                    landmark['left_wrist'])
            
    def text_to_speech(self, text: str) -> None:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio = AudioSegment.from_file(fp, format="mp3")
        play(audio)
        print("음성 재생이 완료되었습니다.")