from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHBoxLayout, QMessageBox, QFileDialog, QSplitter, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QClipboard, QColor
from .model import Task, calculate_and_sort_tasks
import numpy as np
from openpyxl import Workbook
from datetime import datetime
from PyQt6.QtWidgets import QApplication

class PriorityPlotWidget(QWidget):
    def __init__(self, task_list=None):
        super().__init__()
        self.task_list = task_list if task_list is not None else []
        self.dragging = False
        self.drag_index = None
        self.moved_points = set()  # Track which points have been moved
        self.current_annotation = None  # Track current hover annotation
        self.auto_update_timer = QTimer()  # Timer for real-time updates
        self.auto_update_timer.timeout.connect(self.update_priority_display)
        self.auto_update_timer.setSingleShot(True)
        self.initUI()
        
        # Show welcome message for new users
        if not self.task_list:
            self.show_welcome_message()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Create main splitter for side-by-side layout when tasks exist
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel for input (will be hidden after tasks are added)
        self.input_panel = QWidget()
        self.input_panel.setMaximumWidth(400)
        self.input_panel.setMinimumWidth(350)
        
        # Right panel for plot and results
        self.plot_panel = QWidget()
        
        self.main_splitter.addWidget(self.input_panel)
        self.main_splitter.addWidget(self.plot_panel)
        
        # Initially show only input panel
        self.plot_panel.hide()
        
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)
        
        self.initInputPanel()
        self.initPlotPanel()

    def initInputPanel(self):
        layout = QVBoxLayout()
        
        # Streamlined header
        header_label = QLabel("🎯 Add Your Tasks")
        header_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 16px; padding: 15px 10px 10px 10px;")
        layout.addWidget(header_label)
        
        # Quick start options in a more prominent layout
        quick_start_frame = QFrame()
        quick_start_frame.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)
        quick_layout = QVBoxLayout()
        
        quick_label = QLabel("🚀 Quick Start:")
        quick_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-bottom: 8px;")
        quick_layout.addWidget(quick_label)
        
        # Horizontal layout for quick start buttons
        quick_buttons_layout = QHBoxLayout()
        
        # Enhanced test goals button (most prominent)
        self.test_button = QPushButton("🧪 Try Sample Tasks")
        self.test_button.clicked.connect(self.add_test_goals_and_proceed)
        self.test_button.setToolTip("🚀 Instantly try the app with 20 realistic work tasks!")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-weight: bold;
                font-size: 13px;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        quick_buttons_layout.addWidget(self.test_button)
        
        # Enhanced clipboard import button
        self.clipboard_button = QPushButton("📋 Import List")
        self.clipboard_button.clicked.connect(self.add_goals_from_clipboard_and_proceed)
        self.clipboard_button.setToolTip("📄 Paste a list of tasks from your clipboard!")
        self.clipboard_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                font-weight: bold;
                font-size: 13px;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        quick_buttons_layout.addWidget(self.clipboard_button)
        
        quick_layout.addLayout(quick_buttons_layout)
        quick_start_frame.setLayout(quick_layout)
        layout.addWidget(quick_start_frame)
        
        # Separator
        separator = QLabel("─── or add manually ───")
        separator.setStyleSheet("color: #888888; text-align: center; margin: 15px 0px;")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separator)
        
        # Simplified manual input
        form_layout = QVBoxLayout()
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Type a task and press Enter...")
        self.task_input.setToolTip("💡 Type a task name and press Enter to add it quickly!")
        self.task_input.returnPressed.connect(self.add_task_and_auto_proceed)
        self.task_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border-radius: 6px;
                border: 2px solid #555555;
            }
            QLineEdit:focus {
                border: 2px solid #2a82da;
            }
        """)
        form_layout.addWidget(self.task_input)
        
        # Add button (less prominent since Enter is preferred)
        self.add_button = QPushButton("➕ Add Task")
        self.add_button.clicked.connect(self.add_task_and_auto_proceed)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        form_layout.addWidget(self.add_button)
        
        layout.addLayout(form_layout)
        
        # Task list (more compact)
        list_label = QLabel("📋 Your Tasks:")
        list_label.setStyleSheet("color: #ffffff; font-weight: bold; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(list_label)
        
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(1)
        self.input_table.setHorizontalHeaderLabels(["Task"])
        self.input_table.setMaximumHeight(200)  # Limit height
        self.input_table.setStyleSheet("""
            QTableWidget {
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.input_table)
        
        # Help button (smaller, less prominent)
        help_button = QPushButton("❓ Help")
        help_button.clicked.connect(self.show_help)
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                font-size: 11px;
                padding: 6px 12px;
                border-radius: 4px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(help_button)
        
        layout.addStretch()
        self.input_panel.setLayout(layout)
        self.refresh_input_table()

    def initPlotPanel(self):
        layout = QVBoxLayout()
        
        # Header with real-time priority info
        self.priority_header = QLabel("🎯 Drag tasks to prioritize • Top 3 priorities shown below")
        self.priority_header.setStyleSheet("color: #ffffff; font-weight: bold; padding: 10px; font-size: 14px;")
        layout.addWidget(self.priority_header)
        
        # Create splitter for plot and live results
        plot_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Plot area
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        
        self.figure = Figure(figsize=(6, 4), facecolor='#353535')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Set modern plot style
        self.ax.set_facecolor('#353535')
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['top'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        self.ax.spines['right'].set_color('#555555')
        
        # Set labels with modern styling
        self.ax.set_xlabel('* Value (Impact/Importance)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Time Investment (Hours)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_title('Interactive Priority Matrix', color='white', fontsize=13, fontweight='bold', pad=15)
        
        # Style the ticks
        self.ax.tick_params(colors='white', which='both')
        
        # Set fixed axis limits
        self.ax.set_xlim(0, 6)
        self.ax.set_ylim(0, 8)
        
        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        
        plot_layout.addWidget(self.canvas)
        plot_widget.setLayout(plot_layout)
        
        # Live results area
        results_widget = QWidget()
        results_widget.setMaximumHeight(200)
        results_layout = QVBoxLayout()
        
        # Live priority list header
        live_header = QLabel("🏆 Live Priority Ranking")
        live_header.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px; padding: 5px;")
        results_layout.addWidget(live_header)
        
        # Compact results table
        self.live_table = QTableWidget()
        self.live_table.setColumnCount(4)
        self.live_table.setHorizontalHeaderLabels(['🏆', 'Task', 'Value', 'Score'])
        self.live_table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                border-radius: 4px;
            }
            QHeaderView::section {
                padding: 4px;
                font-size: 10px;
            }
        """)
        # Hide row numbers and make it more compact
        self.live_table.verticalHeader().setVisible(False)
        self.live_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.live_table)
        
        # Export button (always visible)
        self.export_button = QPushButton('📊 Export to Excel')
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setToolTip("💾 Save your prioritized task list to Excel")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        results_layout.addWidget(self.export_button)
        
        results_widget.setLayout(results_layout)
        
        # Add to splitter
        plot_splitter.addWidget(plot_widget)
        plot_splitter.addWidget(results_widget)
        plot_splitter.setSizes([300, 200])  # Give more space to plot
        
        layout.addWidget(plot_splitter)
        self.plot_panel.setLayout(layout)

    def add_test_goals_and_proceed(self):
        """Add test goals and automatically proceed to plot view"""
        test_goals = [
            ("Complete Project Proposal", 4.5, 3.0),
            ("Review Code Changes", 3.0, 2.0),
            ("Team Meeting", 2.5, 1.5),
            ("Update Documentation", 3.5, 4.0),
            ("Bug Fixing", 4.0, 2.5),
            ("Client Presentation", 5.0, 4.0),
            ("Code Refactoring", 3.5, 5.0),
            ("Unit Testing", 4.0, 3.0),
            ("Performance Optimization", 4.5, 6.0),
            ("Security Audit", 5.0, 4.5),
            ("Database Migration", 4.0, 7.0),
            ("API Integration", 3.5, 3.5),
            ("User Training", 3.0, 2.0),
            ("System Backup", 2.5, 1.0),
            ("Deployment Planning", 4.0, 2.0),
            ("Code Review", 3.5, 1.5),
            ("Feature Implementation", 4.5, 5.0),
            ("Technical Documentation", 3.0, 4.0),
            ("Bug Triage", 3.5, 2.0),
            ("System Monitoring", 2.5, 1.5)
        ]
        
        for task_name, value, time in test_goals:
            self.task_list.append(Task(task_name, value, time))
        
        self.refresh_input_table()
        self.proceed_to_plot()

    def add_goals_from_clipboard_and_proceed(self):
        """Add goals from clipboard and automatically proceed if successful"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            QMessageBox.warning(self, "📋 Clipboard Empty", "❌ No text found in clipboard!\n\n💡 Copy a list of tasks (one per line) and try again.")
            return
            
        goals = [goal.strip() for goal in text.split('\n') if goal.strip()]
        
        if not goals:
            QMessageBox.warning(self, "❌ No Valid Tasks", "The clipboard text doesn't contain valid tasks.\n\n💡 Make sure each task is on a separate line!")
            return
            
        for goal in goals:
            self.task_list.append(Task(goal, 3.0, 4.0))  # Default to middle of our ranges
            
        self.refresh_input_table()
        
        # Auto-proceed if we have a reasonable number of tasks
        if len(goals) >= 3:
            self.proceed_to_plot()
        else:
            QMessageBox.information(self, "✅ Tasks Added!", f"Added {len(goals)} tasks. Add more or click a task to start prioritizing!")

    def add_task_and_auto_proceed(self):
        """Add a task and auto-proceed to plot if we have enough tasks"""
        task = self.task_input.text().strip()
        if not task:
            QMessageBox.warning(self, "⚠️ Input Required", "🎯 Please enter a task name first!")
            return
        
        self.task_list.append(Task(task, 3.0, 4.0))  # Default to middle of our ranges
        self.task_input.clear()
        self.refresh_input_table()
        
        # Auto-proceed if we have 3 or more tasks
        if len(self.task_list) >= 3:
            self.proceed_to_plot()
        elif len(self.task_list) == 1:
            # Give encouraging feedback for first task
            self.task_input.setPlaceholderText("Great! Add 2 more tasks to start prioritizing...")

    def proceed_to_plot(self):
        """Smoothly transition to the plot view"""
        if not self.task_list:
            return
            
        # Show both panels
        self.plot_panel.show()
        self.main_splitter.setSizes([350, 650])  # Give more space to plot
        
        # Update plot and live results
        self.update_plot()
        self.update_priority_display()
        
        # Minimize input panel after a moment (optional)
        QTimer.singleShot(2000, lambda: self.main_splitter.setSizes([250, 750]))

    def update_priority_display(self):
        """Update the live priority ranking table"""
        if not self.task_list:
            return
            
        # Calculate scores
        for task in self.task_list:
            task.calculate_score()
            
        # Sort by score
        sorted_tasks = sorted(self.task_list, key=lambda t: t.score, reverse=True)
        
        # Update live table (show top 10)
        display_count = min(10, len(sorted_tasks))
        self.live_table.setRowCount(display_count)
        
        for i, task in enumerate(sorted_tasks[:display_count]):
            # Rank
            rank_item = QTableWidgetItem(f"#{i+1}")
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.live_table.setItem(i, 0, rank_item)
            
            # Task name (truncated if too long)
            task_name = task.task if len(task.task) <= 25 else task.task[:22] + "..."
            self.live_table.setItem(i, 1, QTableWidgetItem(task_name))
            
            # Value
            value_item = QTableWidgetItem(f"{task.value:.1f}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.live_table.setItem(i, 2, value_item)
            
            # Score
            score_item = QTableWidgetItem(f"{task.score:.2f}")
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.live_table.setItem(i, 3, score_item)
            
            # Highlight top 3
            if i < 3:
                for col in range(4):
                    item = self.live_table.item(i, col)
                    if item:
                        item.setBackground(QColor(42, 130, 218, 100))  # Light blue highlight
        
        # Auto-resize columns
        self.live_table.resizeColumnsToContents()

    def refresh_input_table(self):
        self.input_table.setRowCount(len(self.task_list))
        for i, t in enumerate(self.task_list):
            self.input_table.setItem(i, 0, QTableWidgetItem(t.task))

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
        self.task_list[self.drag_index].value = max(0, min(6, event.xdata))  # Clamp to valid range
        self.task_list[self.drag_index].time = max(0, min(8, event.ydata))   # Clamp to valid range
        self.moved_points.add(self.drag_index)  # Mark this point as moved
        
        # Update scatter plot data directly for smooth movement
        x_data = [t.value for t in self.task_list]
        y_data = [t.time for t in self.task_list]
        self.scatter.set_offsets(np.column_stack([x_data, y_data]))
        
        # Update the annotation position
        for i, annotation in enumerate(self.ax.texts):
            if i == self.drag_index:
                annotation.set_position((event.xdata, event.ydata))
        
        self.canvas.draw_idle()  # Use draw_idle for smoother updates
        
        # Trigger real-time priority update with a small delay
        self.auto_update_timer.start(100)  # Update after 100ms of no movement

    def on_release(self, event):
        if self.dragging:
            # Do a full redraw when drag is complete
            self.update_plot()
            # Update priority display immediately
            self.update_priority_display()
        self.dragging = False
        self.drag_index = None

    def on_hover(self, event):
        if event.inaxes != self.ax:
            if self.current_annotation:
                self.current_annotation.set_visible(False)
                self.current_annotation = None
                self.canvas.draw_idle()
            return

        contains, ind = self.scatter.contains(event)
        if contains:
            pos = ind["ind"][0]
            task = self.task_list[pos]
            
            # Remove previous annotation if it exists
            if self.current_annotation:
                self.current_annotation.set_visible(False)
            
            # Create new annotation with task name and values
            priority_score = task.value / task.time if task.time > 0 else 0
            text = f"{task.task}\nValue: {task.value:.1f}\nTime: {task.time:.1f}\nPriority: {priority_score:.2f}"
            self.current_annotation = self.ax.annotate(
                text,
                xy=(task.value, task.time),
                xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    fc='#2a82da',
                    ec='#555555',
                    alpha=0.9
                ),
                color='white',
                fontsize=9,
                fontweight='bold',
                arrowprops=dict(
                    arrowstyle='->',
                    connectionstyle='arc3,rad=0.2',
                    color='#555555',
                    linewidth=1.5
                )
            )
            self.canvas.draw_idle()
        elif self.current_annotation:
            self.current_annotation.set_visible(False)
            self.current_annotation = None
            self.canvas.draw_idle()

    def update_plot(self):
        self.ax.clear()
        
        # Reapply modern styling
        self.ax.set_facecolor('#353535')
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['top'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        self.ax.spines['right'].set_color('#555555')
        
        # Set labels with modern styling
        self.ax.set_xlabel('* Value (Impact/Importance)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Time Investment (Hours)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_title('Interactive Priority Matrix', color='white', fontsize=13, fontweight='bold', pad=15)
        
        # Style the ticks
        self.ax.tick_params(colors='white', which='both')
        
        # Maintain fixed axis limits
        self.ax.set_xlim(0, 6)
        self.ax.set_ylim(0, 8)
        
        # Create arrays for all points
        x_data = [t.value for t in self.task_list]
        y_data = [t.time for t in self.task_list]
        
        # Calculate scores and find the top 3 tasks
        for task in self.task_list:
            task.calculate_score()
        
        # Get indices sorted by score (highest first)
        sorted_indices = sorted(range(len(self.task_list)), key=lambda i: self.task_list[i].score, reverse=True)
        top_3_indices = sorted_indices[:3]  # Get top 3 tasks
        
        # Create color array based on whether points have been moved
        colors = ['#2a82da' if i in self.moved_points else '#e74c3c' for i in range(len(self.task_list))]
        
        # Create scatter plot for all points except the top 3
        non_top_indices = [i for i in range(len(self.task_list)) if i not in top_3_indices]
        if non_top_indices:
            self.ax.scatter(
                [x_data[i] for i in non_top_indices],
                [y_data[i] for i in non_top_indices],
                c=[colors[i] for i in non_top_indices],
                picker=True,
                alpha=0.7,
                s=100
            )
        
        # Plot the top 3 tasks with circled numbers
        for rank, task_index in enumerate(top_3_indices, 1):
            if task_index < len(self.task_list):  # Safety check
                task_x = x_data[task_index]
                task_y = y_data[task_index]
                self.ax.plot(task_x, task_y, 'o', markersize=20, markerfacecolor='none', 
                            markeredgecolor=colors[task_index], markeredgewidth=2)
                self.ax.text(task_x, task_y, str(rank), ha='center', va='center', 
                            fontsize=14, fontweight='bold', color=colors[task_index])
        
        # Update the scatter reference for event handling
        self.scatter = self.ax.scatter(x_data, y_data, c=colors, picker=True, alpha=0)
        
        # Adjust figure layout
        self.figure.tight_layout()
        self.canvas.draw()

    def export_to_excel(self):
        if not self.task_list:
            QMessageBox.warning(self, "❌ No Data", "There are no tasks to export!\n\n🎯 Add some tasks and prioritize them first.")
            return
            
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "💾 Save Priority Report",
            f"priority_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
            
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Task Priorities"
            
            # Add headers
            headers = ['📋 Task', '★ Value', '⏰ Time (hours)', '🏆 Priority Score']
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Add data
            sorted_tasks = calculate_and_sort_tasks(self.task_list)
            for row, task in enumerate(sorted_tasks, 2):
                ws.cell(row=row, column=1, value=task.task)
                ws.cell(row=row, column=2, value=task.value)
                ws.cell(row=row, column=3, value=task.time)
                ws.cell(row=row, column=4, value=task.score)
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column[0].column_letter].width = adjusted_width
            
            wb.save(file_path)
            QMessageBox.information(self, "✅ Export Successful!", f"🎉 Your priority analysis has been saved!\n\n📁 File location: {file_path}\n\n💡 You can now share this with your team or use it for planning.")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Export Error", f"😞 Failed to export your data:\n\n{str(e)}\n\n💡 Try saving to a different location or check file permissions.")

    def show_help(self):
        help_text = """
🎯 <b>Welcome to PriPlot - Your Task Priority Assistant!</b>

<b>🚀 Quick Start Options:</b>
• "🧪 Try Sample Tasks" - Instantly explore with 20 realistic work tasks
• "📋 Import List" - Paste tasks from your clipboard (one per line)
• Type manually and press Enter to add tasks one by one

<b>📊 Interactive Prioritization:</b>
• Once you have 3+ tasks, the plot automatically appears
• Drag tasks around to set their Value (→) and Time Investment (↑)
• Bottom-right corner = High Value + Low Time = TOP PRIORITY!
• See live priority rankings update as you drag

<b>🏆 Understanding Your Results:</b>
• Priority Score = Value ÷ Time (higher is better)
• Top 3 tasks get special numbered circles on the plot
• Live ranking table shows your current priorities
• Export to Excel anytime to save your analysis

<b>💡 Pro Tips:</b>
• Hover over plot points to see task details and priority scores
• Red points = original position, Blue points = you moved them
• Focus on high-value, low-time tasks for maximum impact
• The interface adapts as you work - no need to click through tabs!

<b>🎨 What the Numbers Mean:</b>
• Value (0-6): How important/impactful is this task?
• Time (0-8): How many hours will this take?
• Priority Score: Automatically calculated as Value ÷ Time

Happy prioritizing! 🚀
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("📚 PriPlot User Guide")
        msg.setText(help_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #353535;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
                min-width: 500px;
            }
        """)
        msg.exec()

    def show_welcome_message(self):
        welcome_text = """
🎉 <b>Welcome to PriPlot!</b>

Transform your task management with smart priority visualization!

<b>🚀 New Streamlined Experience:</b>
• Choose "🧪 Try Sample Tasks" for instant exploration
• Or "📋 Import List" to paste your own tasks
• Add 3+ tasks and the plot appears automatically
• See live priority updates as you drag tasks around

<b>💡 No more clicking through tabs!</b>
Everything flows naturally as you work. The interface adapts to show you exactly what you need, when you need it.

Ready to boost your productivity? 🎯
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("🎯 Welcome to PriPlot!")
        msg.setText(welcome_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #353535;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
                min-width: 400px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 8px;
            }
        """)
        msg.exec() 