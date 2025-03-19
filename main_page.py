import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
        self.btn_challenge.setCheckable(True)

        # 버튼 그룹으로 묶어서 exclusive 설정
        self.tab_group = QButtonGroup()
        self.tab_group.addButton(self.btn_workout)
        self.tab_group.addButton(self.btn_record)
        self.tab_group.addButton(self.btn_rank)
        self.tab_group.addButton(self.btn_challenge)
        self.tab_group.setExclusive(True)

        # 페이지 전환 이벤트 연결 
        self.btn_workout.clicked.connect(self.show_main)
        self.btn_record.clicked.connect(self.show_record)
        self.btn_rank.clicked.connect(self.show_rank)
        self.btn_challenge.clicked.connect(self.show_challenge)
        # 첫 화면 기본 설정 
        self.btn_workout.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.main_page)

    # pages 
    def show_main(self):
        self.stackedWidget.setCurrentWidget(self.main_page)

    def show_record(self):
        self.stackedWidget.setCurrentWidget(self.record_page)

        self.radio_day.setChecked(True)
        self.radio_day.toggled.connect(self.switch_graph)
        self.radio_week.toggled.connect(self.switch_graph)
        self.radio_month.toggled.connect(self.switch_graph)
    
    def show_rank(self):
        self.stackedWidget.setCurrentWidget(self.rank_page)


    def show_challenge(self):
        self.stackedWidget.setCurrentWidget(self.challenge_page)

    def switch_graph(self):
        if self.radio_day.isChecked():
            self.stackedGraphs.setCurrentIndex(0)
        elif self.radio_week.isChecked():
            self.stackedGraphs.setCurrentIndex(1)
        elif self.radio_month.isChecked():
            self.stackedGraphs.setCurrentIndex(2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())