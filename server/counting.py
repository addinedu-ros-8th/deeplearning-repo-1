import cv2
import numpy as np
import threading
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
from send_landmark import LandmarkSender

class AngleGuid():
    def __init__(self, exercise):
        self.vectors = {0: None, 1: None}
        self.initialized = {0: False, 1: False}
        self.count = 0
        self.up_angle=0
        self.down_angle=0
        self.limit_angle=0
        self.frame_count = 0
        
        self.sendLand = LandmarkSender()

        self.lock = threading.Lock()

        self.joint_map = {
            "shoulder": [(12, 14, 16), (11, 13, 15)],
            "squat": [(24, 26, 28), (23, 25, 27)],
            "knee": [(24, 26, 28), (23, 25, 27)]
        }

        self.guide_angle = {
            "shoulder": lambda idx: -120 * (1 if idx == 0 else -1),
            "squat": lambda idx: 90 * (1 if idx == 1 else -1),
            "knee": lambda idx: -98
        }

        self.r = (0, 0, 255)
        self.g = (0, 255, 0)
        self.b = (255, 0, 0)
        self.p = (147, 20, 255)

        self.state = {0: "up", 1: "down"}
        self.exercise = exercise

        self.last_tts_time = 0
        self.last_time = 0
        self.tts_play = False

        if self.exercise == "squat":
            self.squat_init()
        elif self.exercise == "shoulder":
            self.shoulder_press_init()
        elif self.exercise == "knee":
            self.knee_raise_init()
        else:
            return
    
    def squat_init(self):
        self.up_angle = 160
        self.down_angle = 130

    def shoulder_press_init(self):
        self.up_angle = 130
        self.down_angle = 50
        self.limit_angle = 110

    def knee_raise_init(self):
        self.up_angle = 70
        self.down_angle = 160

    def update(self, index, angle, passing):
        if passing: return

        if self.exercise == "shoulder":
            if self.state[index] == "up" and angle > self.up_angle:
                self.state[index] = "down"

                if self.state[0] == "down" and self.state[1] == "down":
                    self.count +=1
            elif self.state[index] == "down":
                if angle < self.down_angle:
                    self.state[index] = "up"
        elif self.exercise == "squat":
            if self.state[index] == "down" and angle < self.down_angle:
                self.state[index] = "up"

                if self.state[0] == "up" and self.state[1] == "up":
                    self.count += 1
            elif self.state[index] == "up" and angle > self.up_angle:
                self.state[index] = "down"
        elif self.exercise == "knee":
            if self.state[index] == "up" and angle < self.up_angle:
                self.state[index] = "down"
                self.count += 0.5
            elif self.state[index] == "down" and angle > self.down_angle:
                self.state[index] = "up"

    def to_pixel(self, frame, idx, landmarks):
        return np.array([
            landmarks[idx].x * frame.shape[1],
            landmarks[idx].y * frame.shape[0]
        ], dtype=np.float32)

    def calculate_angle(self, a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        return np.degrees(angle)
    
    def get_point_by_angle(self, origin, center, from_point, angle_deg, length=None):
        vec = from_point - center
        if length is None:
            length = np.linalg.norm(vec)

        # 단위 벡터
        unit_vec = vec / (np.linalg.norm(vec) + 1e-6)

        # 회전 각도: 관절 기준이라 180도에서 빼야 함
        theta = np.radians(angle_deg)

        rot_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta),  np.cos(theta)]
        ])

        rotated_vec = rot_matrix @ unit_vec
        target_point = origin + rotated_vec * length
        return target_point


    def draw_exercise_line(self, user_id, frame, landmarks):
        self.joint_map = {
            "shoulder": [(12, 14, 16), (11, 13, 15)],
            "squat": [(24, 26, 28), (23, 25, 27)],
            "knee": [(24, 26, 28), (23, 25, 27)]
        }

        self.guide_angle = {
            "shoulder": lambda idx: -50 * (1 if idx == 0 else -1),
            "squat": lambda idx: 90 * (1 if idx == 1 else -1),
            "knee": lambda idx: -98
        }

        joint_data = []  # 좌우 joint 데이터 모음

        for idx, (a, b, c) in enumerate(self.joint_map[self.exercise]):
            passing = False
            pt1 = self.to_pixel(frame, a, landmarks)
            pt2 = self.to_pixel(frame, b, landmarks)
            pt3 = self.to_pixel(frame, c, landmarks)
            pts = [pt1, pt2, pt3]

            # 운동 종류에 따라 초기화
            if self.exercise == "squat":
                self.squat_init()
            elif self.exercise == "shoulder":
                self.shoulder_press_init()
            elif self.exercise == "knee":
                self.knee_raise_init()
            else:
                return

            # 각도 계산
            angle = self.calculate_angle(landmarks[a], landmarks[b], landmarks[c])
            if (landmarks[c].y > landmarks[a].y and self.exercise == "shoulder"):
                passing = True

            self.update(idx, angle, passing)

            # 각 운동 별 벡터 구성
            if self.exercise == "shoulder":
                origin, center, point = pt1, pt2, pt1
            elif self.exercise == "squat":
                origin, center, point = pt2, pt2, pt3
            elif self.exercise == "knee":
                origin, center, point = pt1, pt2, pt1

            # 가이드 벡터 초기화
            if not self.initialized[idx]:
                self.vectors[idx] = self.get_point_by_angle(origin, center, point, self.guide_angle[self.exercise](idx))
                self.initialized[idx] = True

            # 가이드 라인 그리기
            cv2.line(frame, tuple(origin.astype(int)), tuple(self.vectors[idx].astype(int)), self.p, 2)

            # 관절 색상 결정
            if self.exercise == "shoulder":
                color = self.g if angle > self.up_angle and landmarks[c].y < landmarks[a].y else self.r
            elif self.exercise == "knee":
                color = self.g if angle < self.up_angle else self.r
            elif self.exercise == "squat":
                color = self.r if angle > self.down_angle else self.g

            # 관절 선
            cv2.line(frame, tuple(pt1.astype(int)), tuple(pt2.astype(int)), color, 2)
            cv2.line(frame, tuple(pt2.astype(int)), tuple(pt3.astype(int)), color, 2)

            # 관절 점 & 각도 표시
            for pt in [pt1, pt2, pt3]:
                cv2.circle(frame, tuple(pt.astype(int)), 4, self.b, -1)
            cv2.putText(frame, str(int(angle)), (int(pt2[0]), int(pt2[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # joint 데이터 수집
            joint_data.append({
                "origin": origin.tolist(),
                "guide": self.vectors[idx].tolist(),
                "points": [pt.tolist() for pt in pts]
            })

        self.frame_count += 1

        # 일정 프레임 주기마다 한 번만 전송
        if self.frame_count % 33 == 0:
            self.sendLand.send_pose_data(user_id, joint_data)
    
    def set_exercise(self, exercise):
        with self.lock:
            self.exercise = exercise

    def draw(self, client, frame, landmarks):
        with self.lock:
            self.draw_exercise_line(client, frame, landmarks)

    def get_count(self):
        with self.lock:
            return self.count
    
    def set_count(self):
        with self.lock:
            self.count = 0

    def get_current_angles(self):
        with self.lock:
            return self.current_angle
        
    def get_state(self):
        with self.lock:
            return self.state