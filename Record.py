from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import koreanize_matplotlib
import Constants as cons
import random # 일단 임의의 점수가 필요함 

class RecordGraph(QWidget):
    def __init__(self, mode="day",parent=None):
        super().__init__(parent)
        self.mode= mode 
        self.canvas = FigureCanvas(Figure(figsize=(2, 2)))  
        self.ax =self.canvas.figure.add_subplot(111)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.update_graph()

    def update_graph(self):
        if self.mode == "day":
            self.draw_daily()
        elif self.mode == "week":
            self.draw_weekly()
        elif self.mode == "month":
            self.draw_monthly()

    def draw_daily(self):
        self.ax.clear()
        hours = [h.value for h in cons.HourOfDay]
        # self.ax.tick_params(axis='x', rotation=30)

        scores = [random.randint(10, 100) for _ in hours]
        self.ax.plot(hours, scores, marker='o')
        self.ax.set_xlabel("시간대")
        self.ax.set_ylabel("점수")

        self.canvas.draw()
    def draw_weekly(self):
        self.ax.clear()
        days = [d.value for d in cons.DayOfweek]

        scores = [random.randint(10, 100) for _ in days]
        self.ax.plot(days, scores, marker='s', linestyle='--')
        self.ax.set_xlabel("요일")
        self.ax.set_ylabel("점수")
        self.canvas.draw()

    def draw_monthly(self):
        self.ax.clear()
        months = [m.value for m in cons.Month]
        scores = [random.randint(10, 100) for _ in months]
        
        self.ax.bar(months, scores)
        self.ax.set_xlabel("월")
        self.ax.set_ylabel("점수")
        self.canvas.draw()


    def set_mode(self, mode: str):
        self.mode = mode
        self.update_graph()