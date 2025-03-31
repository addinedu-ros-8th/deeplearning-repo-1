import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtNetwork import QTcpSocket, QUdpSocket
from config import SERVER_PORT, SERVER_PORT
from socket_client import Client
from udp_client import UdpClient
from server.database import FAAdb
import json
import struct
from camera import Camera
import cv2

src = uic.loadUiType("/home/sang/dev_ws/git_ws/deeplearning-repo-1/client/testss.ui")[0]

class MainWindow(QMainWindow, src):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("User")


        pixmap = QPixmap()
        self.btn_plus_profile.setIcon(QIcon("/home/sang/dev_ws/save_file/image_folder/plus.png"))
        self.btn_profile.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0)) #lambda: self.stackedWidget.setCurrentIndex(0)

        # self.btn_workout.clicked.connect(self.show_main)
        # self.btn_record.clicked.connect(self.show_record)
        # self.btn_rank.clicked.connect(self.show_rank)
        #pixmap.loadFromData(icon_list[0])  # 바이너리 데이터를 QPixmap으로 변환
        # 버튼 스타일을 border-image 대신 QIcon으로 설정
        # icon_size = 200  # 버튼 크기
        # self.btn_profile1.setIcon(QIcon(pixmap))
        # self.btn_profile1.setIconSize(QSize(icon_size, icon_size))
        # self.label_profile1.setText(name_list[0])
        # self.btn_profile1.setVisible(True)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    src =  MainWindow()
    src.show()
    sys.exit(app.exec_())
