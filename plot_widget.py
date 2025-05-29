from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHBoxLayout, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from model import Task, calculate_and_sort_tasks
import numpy as np

class PriorityPlotWidget(QWidget):
    def __init__(self, task_list=None):
        super().__init__()
        self.task_list = task_list if task_list is not None else []
        self.dragging = False
        self.drag_index = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.input_tab = QWidget()
        self.plot_tab = QWidget()
        self.table_tab = QWidget()
        self.tabs.addTab(self.input_tab, "Input Goals")
        self.tabs.addTab(self.plot_tab, "Plot")
        self.tabs.addTab(self.table_tab, "Table")
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.initInputTab()
        self.initPlotTab()
        self.initTableTab()

    def initInputTab(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Task name")
        form_layout.addWidget(QLabel("Task:"))
        form_layout.addWidget(self.task_input)
        self.add_button = QPushButton("Add Goal")
        self.add_button.clicked.connect(self.add_task)
        form_layout.addWidget(self.add_button)
        
        # Add test goals button
        self.test_button = QPushButton("Add Test Goals")
        self.test_button.clicked.connect(self.add_test_goals)
        form_layout.addWidget(self.test_button)
        
        layout.addLayout(form_layout)
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(1)
        self.input_table.setHorizontalHeaderLabels(["Task"])
        layout.addWidget(self.input_table)
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.finish_input)
        layout.addWidget(self.done_button)
        self.input_tab.setLayout(layout)
        self.refresh_input_table()

    def add_test_goals(self):
        test_goals = [
            ("Complete Project Proposal", 4.5, 3.0),
            ("Review Code Changes", 3.0, 2.0),
            ("Team Meeting", 2.5, 1.5),
            ("Update Documentation", 3.5, 4.0),
            ("Bug Fixing", 4.0, 2.5)
        ]
        
        for task_name, value, time in test_goals:
            self.task_list.append(Task(task_name, value, time))
        
        self.refresh_input_table()

    def add_task(self):
        task = self.task_input.text().strip()
        if not task:
            QMessageBox.warning(self, "Input Error", "Task name cannot be empty.")
            return
        # Initialize with default values within our valid range
        self.task_list.append(Task(task, 3.0, 4.0))  # Default to middle of our ranges
        self.task_input.clear()
        self.refresh_input_table()

    def refresh_input_table(self):
        self.input_table.setRowCount(len(self.task_list))
        for i, t in enumerate(self.task_list):
            self.input_table.setItem(i, 0, QTableWidgetItem(t.task))

    def finish_input(self):
        if not self.task_list:
            QMessageBox.warning(self, "No Tasks", "Please add at least one task.")
            return
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentWidget(self.plot_tab)
        self.update_plot()

    def initPlotTab(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('Time (hours)')
        self.ax.set_title('Task Priority Plot')
        
        # Set fixed axis limits
        self.ax.set_xlim(1, 6)
        self.ax.set_ylim(1, 8)
        
        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        self.scatter = self.ax.scatter(
            [t.value for t in self.task_list],
            [t.time for t in self.task_list],
            picker=True
        )
        self.canvas.draw()
        layout.addWidget(self.canvas)
        self.apply_button = QPushButton('Apply')
        self.apply_button.clicked.connect(self.showTable)
        layout.addWidget(self.apply_button)
        self.plot_tab.setLayout(layout)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        contains, ind = self.scatter.contains(event)
        if contains:
            self.dragging = True
            self.drag_index = ind["ind"][0]

    def on_motion(self, event):
        if not self.dragging or self.drag_index is None or event.inaxes != self.ax:
            return
        
        # Update task values
        self.task_list[self.drag_index].value = event.xdata
        self.task_list[self.drag_index].time = event.ydata
        
        # Update scatter plot data directly for smooth movement
        x_data = [t.value for t in self.task_list]
        y_data = [t.time for t in self.task_list]
        self.scatter.set_offsets(np.column_stack([x_data, y_data]))
        
        # Update the annotation position
        for i, annotation in enumerate(self.ax.texts):
            if i == self.drag_index:
                annotation.set_position((event.xdata, event.ydata))
        
        self.canvas.draw_idle()  # Use draw_idle for smoother updates

    def on_release(self, event):
        if self.dragging:
            # Do a full redraw when drag is complete
            self.update_plot()
        self.dragging = False
        self.drag_index = None

    def update_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('Time (hours)')
        self.ax.set_title('Task Priority Plot')
        
        # Maintain fixed axis limits
        self.ax.set_xlim(1, 6)
        self.ax.set_ylim(1, 8)
        
        self.scatter = self.ax.scatter(
            [t.value for t in self.task_list],
            [t.time for t in self.task_list],
            picker=True
        )
        
        # Add task labels
        for i, t in enumerate(self.task_list):
            self.ax.annotate(t.task, (t.value, t.time), xytext=(5, 5), textcoords='offset points')
        
        self.canvas.draw()

    def initTableTab(self):
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.table_tab.setLayout(layout)

    def showTable(self):
        sorted_tasks = calculate_and_sort_tasks(self.task_list)
        self.table.setRowCount(len(sorted_tasks))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Task', 'Value', 'Time'])
        for i, t in enumerate(sorted_tasks):
            self.table.setItem(i, 0, QTableWidgetItem(t.task))
            self.table.setItem(i, 1, QTableWidgetItem(f"{t.value:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{t.time:.2f}"))
        self.tabs.setCurrentWidget(self.table_tab) 