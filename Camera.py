import cv2
import threading

import mediapipe as mp
import Controller.Detector as detector  # lmks 저장할 모듈

class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.frame = None
        self.stopped = False
        self.thread = threading.Thread(target=self._update) 
        self.thread.daemon = True

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def start(self):
        self.thread.start()

    def _update(self):
        while not self.stopped:
            ret, frame = self.capture.read()
            if ret:
                self.frame = frame
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = self.pose.process(rgb_frame)
                if results.pose_landmarks:
                    detector.lmks = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
                else:
                    detector.lmks = None

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.capture.release()
