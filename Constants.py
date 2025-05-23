import os
import cv2
import mediapipe as mp
import logging
from enum import Enum 
logging.basicConfig(level=logging.DEBUG)

# Formats
format_video = '.mp4'

# Files
dir_main = os.path.dirname(__file__)
dir_videos = dir_main + '/assets' + '/videos'
dir_workout = dir_videos + '/workout/'
file_training = 'training.json'

# Video
camera_id = 0
### ▶ 화면/창 관련
window_width = 640
window_height = 480
flip_hor = 1
flip_vert = 0
flip_both = -1

# Colors
clr_black = (0, 0, 0)
clr_white = (255, 255, 255)
clr_red = (0, 0, 255)
clr_green = (0, 255, 0)
clr_blue = (255, 0, 0)
clr_gray = (192,192,192)

# Indexes of all landmarks
NOSE = mp.solutions.pose.PoseLandmark.NOSE.value
LEFT_EYE_INNER = mp.solutions.pose.PoseLandmark.LEFT_EYE_INNER.value
LEFT_EYE = mp.solutions.pose.PoseLandmark.LEFT_EYE.value
LEFT_EYE_OUTER = mp.solutions.pose.PoseLandmark.LEFT_EYE_OUTER.value
RIGHT_EYE_INNER = mp.solutions.pose.PoseLandmark.RIGHT_EYE_INNER.value
RIGHT_EYE = mp.solutions.pose.PoseLandmark.RIGHT_EYE.value
RIGHT_EYE_OUTER = mp.solutions.pose.PoseLandmark.RIGHT_EYE_OUTER.value
LEFT_EAR = mp.solutions.pose.PoseLandmark.LEFT_EAR.value
RIGHT_EAR = mp.solutions.pose.PoseLandmark.RIGHT_EAR.value
MOUTH_LEFT = mp.solutions.pose.PoseLandmark.MOUTH_LEFT.value
MOUTH_RIGHT = mp.solutions.pose.PoseLandmark.MOUTH_RIGHT.value
LEFT_SHOULDER = mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
RIGHT_SHOULDER = mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value
LEFT_ELBOW = mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value
RIGHT_ELBOW = mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value
LEFT_WRIST = mp.solutions.pose.PoseLandmark.LEFT_WRIST.value
RIGHT_WRIST = mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value
LEFT_PINKY = mp.solutions.pose.PoseLandmark.LEFT_PINKY.value
RIGHT_PINKY = mp.solutions.pose.PoseLandmark.RIGHT_PINKY.value
LEFT_INDEX = mp.solutions.pose.PoseLandmark.LEFT_INDEX.value
RIGHT_INDEX = mp.solutions.pose.PoseLandmark.RIGHT_INDEX.value
LEFT_THUMB = mp.solutions.pose.PoseLandmark.LEFT_THUMB.value
RIGHT_THUMB = mp.solutions.pose.PoseLandmark.RIGHT_THUMB.value
LEFT_HIP = mp.solutions.pose.PoseLandmark.LEFT_HIP.value
RIGHT_HIP = mp.solutions.pose.PoseLandmark.RIGHT_HIP.value
LEFT_KNEE = mp.solutions.pose.PoseLandmark.LEFT_KNEE.value
RIGHT_KNEE = mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value
LEFT_ANKLE = mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value
RIGHT_ANKLE = mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value
LEFT_HEEL = mp.solutions.pose.PoseLandmark.LEFT_HEEL.value
RIGHT_HEEL = mp.solutions.pose.PoseLandmark.RIGHT_HEEL.value
LEFT_FOOT_INDEX = mp.solutions.pose.PoseLandmark.LEFT_FOOT_INDEX.value
RIGHT_FOOT_INDEX = mp.solutions.pose.PoseLandmark.RIGHT_FOOT_INDEX.value

# Indexes of landmarks for pose classification and correction
lmks_main = [LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
            LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE,
            RIGHT_KNEE, LEFT_ANKLE, RIGHT_ANKLE]

# Labels
lbl_pose = ' Pose'
lbl_done = 'Done!'
lbl_time_end = 'Time is end!'
lbl_next = 'Next'
lbl_workout = 'Workout'
lbl_correct_limbs = 'Correct red limbs'

lbl_exit = 'Start'
lbl_pause = 'Pause'
# lbl_exit = 'Exit'
# lbl_continue = 'Continue'

# Font 
font = cv2.FONT_HERSHEY_DUPLEX
fnt_scale_menu = 1
fnt_thick = 2

# Time
time_wait_close_window = 10 # milliseconds
time_tap = 1 # seconds

# Keyboard
kbrd_quit = 'q'

# View
vw_train_circle_rad = 10
vw_train_circle_filled_rad = 5
vw_bttn_spacing = 10
vw_bttn_width = int(0.3 * window_width)
vw_bttn_height = int(0.185 * window_height)
vw_bttn_frame_thick = 6

# Training
exercise_states = ['start', 'end']

########################################

### ▶ 버튼 공통 설정
vw_bttn_width = 200
vw_bttn_height = 80


### ▶ 색상 (BGR)
clr_black = (0, 0, 0)
clr_white = (255, 255, 255)
clr_green = (0, 255, 0)
clr_blue  = (255, 0, 0)
clr_red   = (0, 0, 255)

### ▶ 폰트 관련
font = 0  # cv2.FONT_HERSHEY_SIMPLEX
fnt_scale_menu = 1.0
fnt_thick = 2

### ▶ 프레임 관련
vw_bttn_frame_thick = 2

### ▶ 키보드 입력 관련
kbrd_quit = 'q'
time_wait_close_window = 5

### ▶ 버튼 레이블 (문자열 상수)
lbl_pause = "PAUSE"
lbl_exit = "EXIT"
lbl_continue = "CONTINUE"
lbl_start = "START"

### ▶ 버튼 위치 (예: pause modal)
# 중앙 기준 좌우 버튼 배치 계산 시 사용
modal_btn_y = int(window_height * 0.4)


######################################
THUMBNAIL_PATH = "./Asset/thumbnails"

THUMBNAIL = {
    "스탠딩 니업": os.path.join(THUMBNAIL_PATH, "스탠딩 니업.gif"),
    "숄더프레스": os.path.join(THUMBNAIL_PATH, "숄더프레스.gif"),
    "스쿼트": os.path.join(THUMBNAIL_PATH, "스쿼트.gif"),
    "프론트 런지": os.path.join(THUMBNAIL_PATH, "프론트 런지.gif"),


    "standing-bicycle": os.path.join(THUMBNAIL_PATH, "standing-bicycle.gif"),
    "side-lunge": os.path.join(THUMBNAIL_PATH, "side-lunge.gif")
}
videos = {
    0: {
        1: "./Asset/front-lunge.mp4",
        2: "./Asset/squat.mp4",
        3: "./Asset/shoulder_press.mp4",
        4: "./Asset/knee-up.mp4"
    },
    1: {
        1: "./Asset/push-up.mp4",
        2: "./Asset/bridge.mp4",
        3: "./Asset/standing-bicycle.mp4",
        4: "./Asset/side-lunge.mp4"
    },
    2: {
        1: "./Asset/front-lunge.mp4",
        2: "./Asset/squat.mp4",
        3: "./Asset/shoulder_press.mp4",
        4: "./Asset/knee-up.mp4"
    }
}

TIER_ICONS = {
    0: "./image_folder/bronze-medal.png",
    1: "./image_folder/silver-medal.png",
    2: "./image_folder/gold-medal.png"
}

TIER_TIMES = {
    0: 30,
    1: 90,
    2: 60
}

EXERCISE_NAME_MAP = {
    '스탠딩 니업': 'knee',
    '숄더프레스': 'shoulder',
    '스쿼트': 'squat',
    '프론트 런지': 'lunge'
}

BREAK_TIME = 3
COUNTDOWN = 3

class HourOfDay(Enum):
    H00 = "00:00"; H03 = "03:00"; H06 = "06:00"; H09 = "09:00"; 
    H12 = "12:00"; H15 = "15:00"; H18 = "18:00"; H21 = "21:00"; 

class DayOfweek(Enum):
    MON = "Mon"; TUE = "Tue"; WED = "Wed"; THU = "Thu"
    FRI = "Fri"; SAT = "Sat" ;SUN = "Sun"
class Month(Enum):
    JAN = "Jan";FEB = "Feb";MAR = "Mar"
    APR = "Apr";MAY = "May";JUN = "Jun"
    JUL = "Jul";AUG = "Aug";SEP = "Sep"
    OCT = "Oct";NOV = "Nov";DEC = "Dec"
    