from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QHBoxLayout, QMessageBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard
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
        self.initUI()
        
        # Show welcome message for new users
        if not self.task_list:
            self.show_welcome_message()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        # Add icons and tooltips to tabs
        self.input_tab = QWidget()
        self.plot_tab = QWidget()
        self.table_tab = QWidget()
        
        self.tabs.addTab(self.input_tab, "📝 Input Goals")
        self.tabs.addTab(self.plot_tab, "📊 Plot")
        self.tabs.addTab(self.table_tab, "📋 Table")
        
        # Add tooltips to tabs
        self.tabs.setTabToolTip(0, "Add and manage your tasks/goals here.\nYou can type them manually, import from clipboard, or use test data.")
        self.tabs.setTabToolTip(1, "Interactive priority visualization.\nDrag tasks around to adjust their value and time estimates.")
        self.tabs.setTabToolTip(2, "View prioritized results and export to Excel.\nTasks are automatically ranked by priority score.")
        
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.initInputTab()
        self.initPlotTab()
        self.initTableTab()

    def initInputTab(self):
        layout = QVBoxLayout()
        
        # Add helpful instruction label with help button
        instruction_layout = QHBoxLayout()
        instruction_label = QLabel("🎯 Add your tasks and goals below. Start by typing a task name or use the quick import options.")
        instruction_label.setStyleSheet("color: #ffffff; font-weight: bold; padding: 10px; margin-bottom: 5px;")
        
        help_button = QPushButton("❓ Help")
        help_button.clicked.connect(self.show_help)
        help_button.setToolTip("📚 Click for detailed instructions on how to use PriPlot effectively!")
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                font-size: 11px;
                padding: 5px 10px;
                max-width: 60px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        instruction_layout.addWidget(instruction_label)
        instruction_layout.addStretch()
        instruction_layout.addWidget(help_button)
        layout.addLayout(instruction_layout)
        
        form_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("e.g., Complete project proposal, Review code, etc.")
        self.task_input.setToolTip("💡 Enter a task or goal name here.\nPress Enter or click 'Add Goal' to add it to your list.")
        self.task_input.returnPressed.connect(self.add_task)
        
        form_layout.addWidget(QLabel("Task:"))
        form_layout.addWidget(self.task_input)
        
        # Enhanced Add Goal button with icon and tooltip
        self.add_button = QPushButton("➕ Add Goal")
        self.add_button.clicked.connect(self.add_task)
        self.add_button.setToolTip("🎯 Add the task you typed to your goal list.\n\nTip: You can also press Enter in the text field!")
        form_layout.addWidget(self.add_button)
        
        # Enhanced clipboard import button
        self.clipboard_button = QPushButton("📋 Import from Clipboard")
        self.clipboard_button.clicked.connect(self.add_goals_from_clipboard)
        self.clipboard_button.setToolTip("📄 Import multiple tasks at once!\n\n• Copy a list of tasks (one per line) to your clipboard\n• Click this button to import them all\n• Perfect for pasting from documents or emails")
        form_layout.addWidget(self.clipboard_button)
        
        # Enhanced test goals button
        self.test_button = QPushButton("🧪 Load Sample Data")
        self.test_button.clicked.connect(self.add_test_goals)
        self.test_button.setToolTip("🚀 Try the app with sample tasks!\n\n• Loads 20 realistic work tasks\n• Great for exploring features\n• Mix of different priorities and time estimates")
        form_layout.addWidget(self.test_button)
        
        layout.addLayout(form_layout)
        
        # Add helper text for the table
        table_help = QLabel("📌 Your tasks will appear below. You can add as many as you need!")
        table_help.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        layout.addWidget(table_help)
        
        self.input_table = QTableWidget()
        self.input_table.setColumnCount(1)
        self.input_table.setHorizontalHeaderLabels(["📋 Your Tasks"])
        self.input_table.setToolTip("📝 All your tasks are listed here.\n\nTip: Make sure to add all your tasks before proceeding to the plot!")
        layout.addWidget(self.input_table)
        
        # Enhanced Done button
        self.done_button = QPushButton("✅ Ready to Prioritize!")
        self.done_button.clicked.connect(self.finish_input)
        self.done_button.setToolTip("🎯 Ready to visualize your priorities?\n\n• Takes you to the interactive plot\n• You'll be able to drag tasks around\n• Value vs Time visualization helps you prioritize")
        self.done_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        layout.addWidget(self.done_button)
        self.input_tab.setLayout(layout)
        self.refresh_input_table()

    def add_test_goals(self):
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

    def add_task(self):
        task = self.task_input.text().strip()
        if not task:
            QMessageBox.warning(self, "⚠️ Input Required", "🎯 Please enter a task name first!\n\nExample: 'Complete project proposal' or 'Review code changes'")
            return
        # Initialize with default values within our valid range
        self.task_list.append(Task(task, 3.0, 4.0))  # Default to middle of our ranges
        self.task_input.clear()
        self.refresh_input_table()

    def add_goals_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            QMessageBox.warning(self, "📋 Clipboard Empty", "❌ No text found in clipboard!\n\n💡 To use this feature:\n• Copy a list of tasks (one per line)\n• Come back and click this button")
            return
            
        goals = [goal.strip() for goal in text.split('\n') if goal.strip()]
        
        if not goals:
            QMessageBox.warning(self, "❌ No Valid Tasks", "The clipboard text doesn't contain valid tasks.\n\n💡 Make sure each task is on a separate line!")
            return
            
        for goal in goals:
            self.task_list.append(Task(goal, 3.0, 4.0))  # Default to middle of our ranges
            
        self.refresh_input_table()
        QMessageBox.information(self, "✅ Success!", f"🎉 Added {len(goals)} tasks from clipboard!\n\nYou can now add more tasks or proceed to prioritize.")

    def refresh_input_table(self):
        self.input_table.setRowCount(len(self.task_list))
        for i, t in enumerate(self.task_list):
            self.input_table.setItem(i, 0, QTableWidgetItem(t.task))

    def finish_input(self):
        if not self.task_list:
            QMessageBox.warning(self, "❌ No Tasks Added", "🎯 Please add at least one task before proceeding!\n\n💡 You can:\n• Type a task manually\n• Import from clipboard\n• Load sample data to try the app")
            return
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentWidget(self.plot_tab)
        self.update_plot()

    def initPlotTab(self):
        layout = QVBoxLayout()
        
        # Add instructional header
        plot_instruction = QLabel("🎯 Drag tasks around the plot to set their Value (→) and Time Investment (↑)")
        plot_instruction.setStyleSheet("color: #ffffff; font-weight: bold; padding: 10px; text-align: center;")
        layout.addWidget(plot_instruction)
        
        # Add helpful tips
        tips_label = QLabel("💡 Bottom-right = High Value + Low Time = TOP PRIORITY! | Hover over points for details")
        tips_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px; text-align: center;")
        layout.addWidget(tips_label)
        
        self.figure = Figure(figsize=(5, 4), facecolor='#353535')
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
        self.ax.set_xlabel('★ Value (Impact/Importance)', color='white', fontsize=10, fontweight='bold')
        self.ax.set_ylabel('⏰ Time Investment (Hours)', color='white', fontsize=10, fontweight='bold')
        self.ax.set_title('🎯 Interactive Task Priority Matrix', color='white', fontsize=12, fontweight='bold', pad=20)
        
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
        
        self.scatter = self.ax.scatter(
            [t.value for t in self.task_list],
            [t.time for t in self.task_list],
            picker=True,
            alpha=0.7
        )
        
        # Adjust figure layout
        self.figure.tight_layout()
        self.canvas.draw()
        
        layout.addWidget(self.canvas)
        
        # Enhanced Apply button
        self.apply_button = QPushButton('🚀 Generate Priority Ranking')
        self.apply_button.clicked.connect(self.showTable)
        self.apply_button.setToolTip("📊 Create your priority-ranked task list!\n\n• Calculates priority scores based on Value/Time ratio\n• Shows you which tasks to do first\n• Takes you to the results table")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
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

    def on_release(self, event):
        if self.dragging:
            # Do a full redraw when drag is complete
            self.update_plot()
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
            text = f"{task.task}\nValue: {task.value:.1f}\nTime: {task.time:.1f}"
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
        self.ax.set_xlabel('★ Value (Impact/Importance)', color='white', fontsize=10, fontweight='bold')
        self.ax.set_ylabel('⏰ Time Investment (Hours)', color='white', fontsize=10, fontweight='bold')
        self.ax.set_title('🎯 Interactive Task Priority Matrix', color='white', fontsize=12, fontweight='bold', pad=20)
        
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

    def initTableTab(self):
        layout = QVBoxLayout()
        
        # Add results header
        results_header = QLabel("🏆 Your Prioritized Task List - Ranked by Priority Score")
        results_header.setStyleSheet("color: #ffffff; font-weight: bold; padding: 10px; font-size: 14px;")
        layout.addWidget(results_header)
        
        # Add explanation
        explanation = QLabel("📈 Higher priority score = Better Value/Time ratio. Focus on tasks at the top!")
        explanation.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        layout.addWidget(explanation)
        
        self.table = QTableWidget()
        self.table.setToolTip("📋 Your tasks ranked by priority score.\n\n• Top tasks = highest value for time invested\n• Priority Score = Value ÷ Time\n• Focus on the highest scoring tasks first!")
        self.table.setHorizontalHeaderLabels(['📋 Task', '★ Value', '⏰ Time', '🏆 Priority Score'])
        layout.addWidget(self.table)
        
        # Enhanced export button
        self.export_button = QPushButton('📊 Export to Excel')
        self.export_button.clicked.connect(self.export_to_excel)
        self.export_button.setToolTip("💾 Save your prioritized task list!\n\n• Creates a professional Excel spreadsheet\n• Includes all task details and priority scores\n• Perfect for sharing with your team")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        layout.addWidget(self.export_button)
        
        self.table_tab.setLayout(layout)

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

    def showTable(self):
        sorted_tasks = calculate_and_sort_tasks(self.task_list)
        self.table.setRowCount(len(sorted_tasks))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['📋 Task', '★ Value', '⏰ Time', '🏆 Priority Score'])
        for i, t in enumerate(sorted_tasks):
            self.table.setItem(i, 0, QTableWidgetItem(t.task))
            self.table.setItem(i, 1, QTableWidgetItem(f"{t.value:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{t.time:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{t.score:.2f}"))
        self.tabs.setCurrentWidget(self.table_tab)

    def show_help(self):
        help_text = """
🎯 <b>Welcome to PriPlot - Your Task Priority Assistant!</b>

<b>📝 STEP 1: Add Your Tasks</b>
• Type task names manually or import from clipboard
• Use "Load Sample Data" to try the app with example tasks
• Add as many tasks as you need - there's no limit!

<b>📊 STEP 2: Visualize & Prioritize</b>
• Click "Ready to Prioritize!" to open the interactive plot
• Drag tasks around to set their Value (→) and Time Investment (↑)
• Bottom-right corner = High Value + Low Time = TOP PRIORITY!

<b>📋 STEP 3: Get Your Results</b>
• Click "Generate Priority Ranking" to see your sorted task list
• Tasks are ranked by Priority Score (Value ÷ Time)
• Export to Excel to share with your team

<b>💡 Pro Tips:</b>
• Hover over plot points to see task details
• Red points = original position, Blue points = you moved them
• Top 3 priority tasks get special numbered circles
• Focus on high-value, low-time tasks for maximum impact!

<b>🎨 What the Numbers Mean:</b>
• Value (1-6): How important/impactful is this task?
• Time (1-8): How many hours will this take?
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

<b>🚀 Quick Start:</b>
• Add your tasks in the "Input Goals" tab
• Drag them around in the "Plot" tab to set Value vs Time
• Get your prioritized list in the "Table" tab

<b>💡 New to PriPlot?</b>
Click the "❓ Help" button for detailed instructions, or try the "🧪 Load Sample Data" to explore with example tasks.

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