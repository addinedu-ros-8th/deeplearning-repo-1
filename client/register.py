import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic


class RegisterWindow(QDialog):
    def __init__(self, socket):
        super().__init__()

        self.setWindowTitle("Register")

        