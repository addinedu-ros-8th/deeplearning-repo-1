from PyQt5.QtWidgets import QVBoxLayout
from Record import RecordGraph

class RecordHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.graph_day = RecordGraph("day")
        self.graph_week = RecordGraph("week")
        self.graph_month = RecordGraph("month")
        self.current_graph = self.graph_day

        self.graph_container_layout = QVBoxLayout(self.main_window.graph_container)
        self.graph_container_layout.addWidget(self.graph_day)

        self.setup_radio_buttons()
    
    def setup_radio_buttons(self):
        self.main_window.radio_day.setChecked(True)
        self.main_window.radio_day.clicked.connect(lambda: self.switch_graph(self.graph_day, "day"))
        self.main_window.radio_week.clicked.connect(lambda: self.switch_graph(self.graph_week, "week"))
        self.main_window.radio_month.clicked.connect(lambda: self.switch_graph(self.graph_month, "month"))

    def switch_graph(self, new_graph, mode):
        self.graph_container_layout.removeWidget(self.current_graph)
        self.current_graph.hide() 
        self.graph_container_layout.addWidget(new_graph)
        new_graph.set_mode(mode)
        new_graph.show()
        self.current_graph = new_graph


