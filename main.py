import sys
import os
import signal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "client")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from client.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Ctrl+C 핸들러
    client = MainWindow()

    client.show()
    sys.exit(app.exec_())
