import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class DraggableScatter:
    def __init__(self, scatter, update_callback):
        self.scatter = scatter
        self.update_callback = update_callback
        self.press = None
        self.cidpress = scatter.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = scatter.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = scatter.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.selected_index = None

    def on_press(self, event):
        if event.inaxes != self.scatter.axes:
            return
        contains, attrd = self.scatter.contains(event)
        if not contains:
            return
        ind = attrd['ind'][0]
        self.selected_index = ind
        self.press = (self.scatter.get_offsets()[ind], event.xdata, event.ydata)

    def on_motion(self, event):
        if self.press is None or self.selected_index is None:
            return
        if event.inaxes != self.scatter.axes:
            return
        x0, y0 = self.press[0]
        dx = event.xdata - self.press[1]
        dy = event.ydata - self.press[2]
        new_x = x0 + dx
        new_y = y0 + dy
        offsets = self.scatter.get_offsets()
        offsets[self.selected_index] = [new_x, new_y]
        self.scatter.set_offsets(offsets)
        self.scatter.figure.canvas.draw_idle()
        self.update_callback(self.selected_index, new_x, new_y)

    def on_release(self, event):
        self.press = None
        self.selected_index = None

class PriorityPlotWidget(QWidget):
    def __init__(self, task_list):
        super().__init__()
        self.task_list = task_list
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.plot_tab = QWidget()
        self.table_tab = QWidget()
        self.tabs.addTab(self.plot_tab, "Plot")
        self.tabs.addTab(self.table_tab, "Table")
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.initPlotTab()
        self.initTableTab()

    def initPlotTab(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('Time (hours)')
        self.ax.set_title('Task Priority Plot')
        self.scatter = self.ax.scatter(
            [t['value'] for t in self.task_list],
            [t['time'] for t in self.task_list],
            picker=True
        )
        self.annot = self.ax.annotate(
            "",
            xy=(0,0),
            xytext=(10,10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        self.annot.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.canvas.draw()
        layout.addWidget(self.canvas)
        self.apply_button = QPushButton('Apply')
        self.apply_button.clicked.connect(self.showTable)
        layout.addWidget(self.apply_button)
        self.plot_tab.setLayout(layout)
        self.draggable = DraggableScatter(self.scatter, self.update_task_from_plot)

    def update_task_from_plot(self, idx, new_x, new_y):
        self.task_list[idx]['value'] = max(0.1, new_x)
        self.task_list[idx]['time'] = max(0.1, new_y)

    def initTableTab(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.table_tab.setLayout(layout)

    def showTable(self):
        # Calculate scores
        for t in self.task_list:
            t['score'] = t['value'] / math.log(max(2.718, t['time']))
        sorted_tasks = sorted(self.task_list, key=lambda t: t['score'], reverse=True)
        self.table.setRowCount(len(sorted_tasks))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Task', 'Score'])
        for i, t in enumerate(sorted_tasks):
            self.table.setItem(i, 0, QTableWidgetItem(t['task']))
            self.table.setItem(i, 1, QTableWidgetItem(f"{t['score']:.2f}"))
        self.tabs.setCurrentWidget(self.table_tab)

    def on_hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.scatter.contains(event)
            if cont:
                idx = ind["ind"][0]
                pos = self.scatter.get_offsets()[idx]
                self.annot.xy = pos
                text = self.task_list[idx]["task"]
                self.annot.set_text(text)
                self.annot.get_bbox_patch().set_alpha(0.8)
                self.annot.set_visible(True)
                self.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.canvas.draw_idle()

def plot(task_list=None):
    if task_list is None:
        # Fictive task list
        task_list = [
            {'task': 'Write report', 'value': 8, 'time': 2},
            {'task': 'Email client', 'value': 5, 'time': 1},
            {'task': 'Prepare slides', 'value': 7, 'time': 3},
            {'task': 'Team meeting', 'value': 4, 'time': 2},
            {'task': 'Code review', 'value': 6, 'time': 4},
        ]
    app = QApplication(sys.argv)
    main = QMainWindow()
    widget = PriorityPlotWidget(task_list)
    main.setCentralWidget(widget)
    main.setWindowTitle('Priority Plot')
    main.resize(700, 500)
    main.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    plot() 