import time
import sys
import random

import pyqtgraph as py_graph
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import QTimer
import ui_graph_widget

fav_colors = (
    '#196ab4', '#f1c232', '#f44336', '#8fce00'
)


class HomeWindow(QWidget, ui_graph_widget.Ui_Form):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.setupUi(self)

        self.graph_widget: 'py_graph.PlotWidget' = py_graph.PlotWidget()
        self.graph_widget.showGrid(x=True, y=True, alpha=1.0)
        self.graph_widget.setTitle("Multiple Line Plots")
        self.graph_widget.setLabel('bottom', 'Hour')
        self.graph_widget.setBackground("#FDE3CF")
        self.gridLayout_3 = QGridLayout(self.widget)
        self.widget.setLayout(self.gridLayout_3)
        self.gridLayout_3.addWidget(self.graph_widget)

        self.start_button = QPushButton()
        self.start_button.setText("START")
        self.start_button.setMaximumSize(120, 50)
        self.gridLayout.addWidget(self.start_button, 1, 0)

        self.start_button.clicked.connect(self.start_timer)

        self.plot_items = []
        self.plot_coordinates = []
        self.start_time = time.time()
        self.a = 1
        self.b = 5
        self.timer = None

    def start_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.generate_data)
        self.timer.start()
        self.generate_data()

    def add_data(self, x, y, plot_num: int = 0):
        if plot_num < len(self.plot_items):
            self.plot_coordinates[plot_num]['x'] += [x]
            self.plot_coordinates[plot_num]['y'] += [y]
            self.plot_items[plot_num].setData(self.plot_coordinates[plot_num]['x'],
                                              self.plot_coordinates[plot_num]['y'])
        else:
            self.plot_coordinates.append({'x': [x], 'y': [y]})
            self.plot_items.append(self.graph_widget.plot([x], [y], symbol='o', symbolBrush=fav_colors[plot_num]))

    def generate_data(self):
        def plot():
            for index, y in enumerate((y1, y2, y3, y4)):
                self.add_data(x, y, index)

        self.a = self.a + random.randint(0, 5) * random.choice([-1, 1, 1, 1, -1])
        self.b = self.a + random.randint(5, 15) * random.choice([-1, 1, 1, 1, -1])

        if self.a == self.b:
            self.a = random.randint(self.a, self.a+3)
            self.b = random.randint(self.b, self.b+3)
        elif self.a > self.b:
            self.a, self.b = self.b, self.a

        x = time.time() - self.start_time

        y1 = random.randint(self.a, self.b)
        y2 = random.randint(self.a, self.b)
        y3 = random.randint(self.a, self.b)
        y4 = random.randint(self.a, self.b)

        plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = HomeWindow()
    w.show()
    sys.exit(app.exec())
