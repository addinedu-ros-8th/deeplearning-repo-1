
import sys
import os
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from camera import Camera
from_class = uic.loadUiType("./ui/main_page.ui")[0]

class MainWindow(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Main")
        
        # 버튼을 toggle 가능하게 변경
        self.btn_workout.setCheckable(True)
        self.btn_record.setCheckable(True)
        self.btn_rank.setCheckable(True)

        # 버튼 그룹으로 묶어서 exclusive 설정
        self.tab_group = QButtonGroup()
        self.tab_group.addButton(self.btn_workout)
        self.tab_group.addButton(self.btn_record)
        self.tab_group.addButton(self.btn_rank)
        self.tab_group.setExclusive(True)

        
        # 페이지 전환 이벤트 연결 
        ## left tab 
        self.btn_workout.clicked.connect(self.page_main)
        self.btn_record.clicked.connect(self.page_record)
        self.btn_rank.clicked.connect(self.page_rank)
        ## other buttons  
        self.btn_start.clicked.connect(self.go2workout)

        # 첫 화면 기본 설정 
        self.btn_workout.setChecked(True)
        self.stackedWidget_small.setCurrentWidget(self.main_page)

    # pages 
    def page_main(self):
        self.stackedWidget_small.setCurrentWidget(self.main_page)
    def page_record(self):
        self.stackedWidget_small.setCurrentWidget(self.record_page)
        self.radio_day.setChecked(True)
        self.radio_day.toggled.connect(self.switch_page)
        self.radio_week.toggled.connect(self.switch_page)
        self.radio_month.toggled.connect(self.switch_page)
    def page_rank(self):
        self.stackedWidget_small.setCurrentWidget(self.rank_page)
    def switch_page(self):
        if self.radio_day.isChecked():
            self.stackedGraphs.setCurrentIndex(0)
        elif self.radio_week.isChecked():
            self.stackedGraphs.setCurrentIndex(1)
        elif self.radio_month.isChecked():
            self.stackedGraphs.setCurrentIndex(2)

    # workout 
    def go2workout(self):
        self.stackedWidget_big.setCurrentWidget(self.page_workout)
        self.lb_cam = self.page_workout.findChild(QLabel, "lb_cam")

        self.camera = Camera()
        self.camera.start()

        self.timer = QTimer(self)  # 명확히 parent 설정
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(30)

    def update_gui(self):
        if self.camera.frame is not None:
            img = cv2.cvtColor(self.camera.frame, cv2.COLOR_BGR2RGB)
            qt_img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            self.lb_cam.setPixmap(QPixmap.fromImage(qt_img))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())