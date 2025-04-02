# extract pose landmarks
"""
    landmark 관리 
"""
import logging
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mpipepose = None
lmks = [-1] * len(mp_pose.PoseLandmark)
segmentation_mask = []

def init(static_image_mode=False, model_complexity=0, smooth_landmarks=True, 
         enable_segmentation=True, smooth_segmentation=True,
         min_detection_confidence=0.5, min_tracking_confidence=0.5):
    global mpipepose
    mpipepose = mp_pose.Pose(
        static_image_mode=static_image_mode,
        model_complexity=model_complexity,
        smooth_landmarks=smooth_landmarks,
        enable_segmentation=enable_segmentation,
        smooth_segmentation=smooth_segmentation,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence
    )

def _ensure_pose_initialized():
    global mpipepose
    if mpipepose is None:
        logging.warning("\u26a0\ufe0f mpipepose was None! Auto-initializing with default settings.")
        init()

def analyze_user(frame):
    global lmks, segmentation_mask
    _ensure_pose_initialized()

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mpipepose.process(imgRGB)
    segmentation_mask = results.segmentation_mask

    try:
        if results.pose_landmarks:
            h, w, _ = frame.shape
            lmks = {}  # lmks를 항상 초기화
            for idx, lm in enumerate(results.pose_landmarks.landmark):
                cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                lmks[idx] = [cx, cy, cz]
        else:
            lmks = {}
    except Exception as e:
        logging.debug(f'Something goes wrong in analyze_user(): {e}')
        lmks = {}


"""
    hand tracking for finger counting 
"""
class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.prev_number = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        return lmList
    def count_fingers(self, lmList):
        fingers = []
        tipIds = [4, 8, 12, 16, 20]
        if len(lmList) == 0:
            return 0

        # 엄지
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 나머지 4손가락
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers.count(1)


