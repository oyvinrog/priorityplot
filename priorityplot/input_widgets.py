from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                             QLabel, QFrame, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional, Callable
from .interfaces import ITaskInputWidget, ITaskDisplayWidget
from .model import Task, SampleDataGenerator, TaskValidator

class TaskInputField(QWidget):
    """Single responsibility: Handle individual task input following SRP
    Implements ITaskInputWidget protocol"""
    
    task_added = pyqtSignal(str)  # Emit when task is added
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Type a task and press Enter...")
        self.task_input.setToolTip("💡 Type a task name and press Enter to add it quickly!")
        self.task_input.returnPressed.connect(self._on_return_pressed)
        self.task_input.setStyleSheet("""
            QLineEdit {
                padding: 14px 16px;
                font-size: 14px;
                border-radius: 10px;
                border: 2px solid #2D3139;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F2228, stop:1 #181A1F);
                color: #E5E7EB;
                selection-background-color: #4F46E5;
            }
            QLineEdit:focus {
                border: 2px solid #6366F1;
                background: #252830;
            }
            QLineEdit:hover {
                border: 2px solid #3F4451;
            }
        """)
        layout.addWidget(self.task_input)
        
        self.add_button = QPushButton("➕ Add Task")
        self.add_button.clicked.connect(self._on_add_clicked)
        self.add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
                padding: 10px 16px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                color: #E5E7EB;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B7280, stop:1 #4B5563);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
            }
        """)
        layout.addWidget(self.add_button)
        
        self.setLayout(layout)
    
    def get_current_task_text(self) -> str:
        """Implementation of ITaskInputWidget protocol"""
        return self.task_input.text().strip()
    
    def clear_input(self) -> None:
        """Implementation of ITaskInputWidget protocol"""
        self.task_input.clear()
    
    def set_placeholder_text(self, text: str) -> None:
        """Implementation of ITaskInputWidget protocol"""
        self.task_input.setPlaceholderText(text)
    
    def _on_return_pressed(self):
        self._add_task()
    
    def _on_add_clicked(self):
        self._add_task()
    
    def _add_task(self):
        task_text = self.get_current_task_text()
        if task_text:
            self.task_added.emit(task_text)
            self.clear_input()

class QuickStartWidget(QWidget):
    """Single responsibility: Handle quick start options following SRP"""
    
    sample_tasks_requested = pyqtSignal()
    clipboard_import_requested = pyqtSignal()
    mindmap_import_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        # Quick start frame
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252830, stop:1 #1F2228);
                border-radius: 12px;
                padding: 16px;
                margin: 8px;
                border: 1px solid #2D3139;
            }
        """)
        
        layout = QVBoxLayout()
        
        quick_label = QLabel("🚀 Quick Start")
        quick_label.setStyleSheet("color: #F3F4F6; font-weight: 700; font-size: 14px; margin-bottom: 10px; letter-spacing: 0.5px;")
        layout.addWidget(quick_label)
        
        # Horizontal layout for buttons
        buttons_layout = QHBoxLayout()
        
        self.test_button = QPushButton("🧪 Try Sample Tasks")
        self.test_button.clicked.connect(self.sample_tasks_requested.emit)
        self.test_button.setToolTip("🚀 Instantly try the app with 20 realistic work tasks!")
        self.test_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10B981, stop:1 #059669);
                font-weight: 700;
                font-size: 13px;
                padding: 14px 18px;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34D399, stop:1 #10B981);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        buttons_layout.addWidget(self.test_button)
        
        self.clipboard_button = QPushButton("📋 Import List")
        self.clipboard_button.clicked.connect(self.clipboard_import_requested.emit)
        self.clipboard_button.setToolTip("📄 Paste a list of tasks from your clipboard!")
        self.clipboard_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3B82F6, stop:1 #2563EB);
                font-weight: 700;
                font-size: 13px;
                padding: 14px 18px;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60A5FA, stop:1 #3B82F6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563EB, stop:1 #1D4ED8);
            }
        """)
        buttons_layout.addWidget(self.clipboard_button)
        
        self.mindmap_button = QPushButton("🧠 Import Mindmap")
        self.mindmap_button.clicked.connect(self.mindmap_import_requested.emit)
        self.mindmap_button.setToolTip("🌳 Import tasks from indented mindmap structure!\nExample:\nMain Task\n    Sub Task 1\n        Sub Sub Task\n    Sub Task 2")
        self.mindmap_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6, stop:1 #7C3AED);
                font-weight: 700;
                font-size: 13px;
                padding: 14px 18px;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A78BFA, stop:1 #8B5CF6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7C3AED, stop:1 #6D28D9);
            }
        """)
        buttons_layout.addWidget(self.mindmap_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

class TaskInputTable(QTableWidget):
    """Single responsibility: Display input tasks in table format following SRP
    Implements ITaskDisplayWidget protocol"""
    
    task_delete_requested = pyqtSignal(int)  # Emit when task deletion is requested
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()
    
    def _setup_table(self):
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Task", "Actions"])
        self.setMaximumHeight(200)
        self.setColumnWidth(1, 80)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setStyleSheet("""
            QTableWidget {
                border-radius: 10px;
                font-size: 13px;
                background: #181A1F;
                border: 2px solid #2D3139;
            }
            QTableWidget::item {
                padding: 8px;
                color: #E5E7EB;
            }
            QTableWidget::item:hover {
                background-color: #252830;
            }
        """)
    
    def refresh_display(self, tasks: List[Task]) -> None:
        """Implementation of ITaskDisplayWidget protocol"""
        self.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            # Task name
            self.setItem(i, 0, QTableWidgetItem(task.task))
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Remove this task")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #EF4444, stop:1 #DC2626);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #F87171, stop:1 #EF4444);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #DC2626, stop:1 #B91C1C);
                }
            """)
            delete_btn.clicked.connect(lambda checked, idx=i: self.task_delete_requested.emit(idx))
            self.setCellWidget(i, 1, delete_btn)
    
    def highlight_task(self, task_index: int) -> None:
        """Implementation of ITaskDisplayWidget protocol"""
        if task_index < self.rowCount():
            self.selectRow(task_index)
    
    def clear_highlighting(self) -> None:
        """Implementation of ITaskDisplayWidget protocol"""
        self.clearSelection()
    
    def keyPressEvent(self, event):
        """Handle keyboard events for task deletion"""
        from PyQt6.QtCore import Qt
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            # Get currently selected row
            selected_rows = self.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                self.task_delete_requested.emit(row)
        else:
            super().keyPressEvent(event)

class TaskInputCoordinator(QWidget):
    """Single responsibility: Coordinate task input operations following SRP"""
    
    tasks_updated = pyqtSignal(list)  # Emit when task list changes
    show_results_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_label = QLabel("Add Your Tasks")
        header_label.setStyleSheet("color: #F3F4F6; font-weight: 700; font-size: 20px; padding: 20px 12px 12px 12px; letter-spacing: 0.5px;")
        layout.addWidget(header_label)
        
        # Quick start widget
        self.quick_start_widget = QuickStartWidget()
        layout.addWidget(self.quick_start_widget)
        
        # Separator
        separator = QLabel("or add manually")
        separator.setStyleSheet("color: #6B7280; text-align: center; margin: 18px 0px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separator)
        
        # Task input field
        self.task_input_field = TaskInputField()
        layout.addWidget(self.task_input_field)
        
        # Task list
        list_label = QLabel("📋 Your Tasks")
        list_label.setStyleSheet("color: #F3F4F6; font-weight: 700; font-size: 14px; margin-top: 24px; margin-bottom: 8px; letter-spacing: 0.5px;")
        layout.addWidget(list_label)
        
        self.task_table = TaskInputTable()
        layout.addWidget(self.task_table)
        
        # Show results button
        self.show_results_button = QPushButton("Show Priority Chart →")
        self.show_results_button.clicked.connect(self.show_results_requested.emit)
        self.show_results_button.setToolTip("💡 Ready to prioritize? Click to see your interactive chart!")
        self.show_results_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10B981, stop:1 #059669);
                color: white;
                font-weight: 700;
                font-size: 15px;
                padding: 16px 24px;
                border-radius: 12px;
                margin: 20px 0px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #34D399, stop:1 #10B981);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #047857);
                padding: 17px 24px 15px 24px;
            }
        """)
        layout.addWidget(self.show_results_button)
        self.show_results_button.hide()
        
        # Help button
        help_button = QPushButton("❓ Help")
        help_button.clicked.connect(self._show_help)
        help_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 8px;
                margin-top: 12px;
                color: #E5E7EB;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B7280, stop:1 #4B5563);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1F2937);
            }
        """)
        layout.addWidget(help_button)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _connect_signals(self):
        self.quick_start_widget.sample_tasks_requested.connect(self._add_sample_tasks)
        self.quick_start_widget.clipboard_import_requested.connect(self._import_from_clipboard)
        self.quick_start_widget.mindmap_import_requested.connect(self._import_mindmap_from_clipboard)
        self.task_input_field.task_added.connect(self._add_task)
        self.task_table.task_delete_requested.connect(self._delete_task)
    
    def _add_task(self, task_name: str):
        """Add a single task"""
        try:
            new_task = TaskValidator.create_validated_task(task_name)
            self._tasks.append(new_task)
            self._update_display()
            self._update_ui_state()
        except ValueError as e:
            QMessageBox.warning(self, "❌ Invalid Task", f"Could not create task:\n\n{str(e)}")
    
    def _delete_task(self, task_index: int):
        """Delete a task by index"""
        if 0 <= task_index < len(self._tasks):
            del self._tasks[task_index]
            self._update_display()
            self._update_ui_state()
    
    def _add_sample_tasks(self):
        """Add sample tasks"""
        sample_tasks = SampleDataGenerator.get_sample_tasks()
        self._tasks.extend(sample_tasks)
        self._update_display()
        self._update_ui_state()
        self.task_input_field.set_placeholder_text("20 sample tasks added! Click 'Show Results' to prioritize.")
    
    def _import_from_clipboard(self):
        """Import tasks from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            QMessageBox.warning(self, "📋 Clipboard Empty", "❌ No text found in clipboard!\n\n💡 Copy a list of tasks (one per line) and try again.")
            return
        
        new_tasks = SampleDataGenerator.create_tasks_from_text(text)
        
        if not new_tasks:
            QMessageBox.warning(self, "❌ No Valid Tasks", "The clipboard text doesn't contain valid tasks.\n\n💡 Make sure each task is on a separate line!")
            return
            
        self._tasks.extend(new_tasks)
        self._update_display()
        self._update_ui_state()
        
        self.task_input_field.set_placeholder_text(f"{len(new_tasks)} tasks added! Click 'Show Results' to prioritize.")
        QMessageBox.information(self, "✅ Tasks Added!", f"Added {len(new_tasks)} tasks from clipboard.\n\n💡 Click 'Show Results' when ready to prioritize!")
    
    def _import_mindmap_from_clipboard(self):
        """Import tasks from mindmap-style indented clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            QMessageBox.warning(self, "📋 Clipboard Empty", "❌ No text found in clipboard!\n\n💡 Copy indented mindmap text and try again.")
            return
        
        new_tasks = SampleDataGenerator.create_tasks_from_mindmap(text)
        
        if not new_tasks:
            QMessageBox.warning(self, "❌ No Valid Tasks", 
                              "The clipboard text doesn't contain valid mindmap structure.\n\n"
                              "💡 Expected format:\n"
                              "Main Task\n"
                              "    Sub Task 1\n"
                              "        Sub Sub Task\n"
                              "    Sub Task 2\n\n"
                              "This creates tasks like:\n"
                              "• Main Task->Sub Task 1\n"
                              "• Sub Task 1->Sub Sub Task\n"
                              "• Main Task->Sub Task 2")
            return
            
        self._tasks.extend(new_tasks)
        self._update_display()
        self._update_ui_state()
        
        self.task_input_field.set_placeholder_text(f"{len(new_tasks)} mindmap tasks added! Click 'Show Results' to prioritize.")
        QMessageBox.information(self, "🧠 Mindmap Tasks Added!", 
                              f"✅ Added {len(new_tasks)} tasks from mindmap structure.\n\n"
                              "🌳 Tasks represent parent->child relationships.\n\n"
                              "💡 Click 'Show Results' when ready to prioritize!")
    
    def _update_display(self):
        """Update the task table display"""
        self.task_table.refresh_display(self._tasks)
        self.tasks_updated.emit(self._tasks)
    
    def _update_ui_state(self):
        """Update UI state based on number of tasks"""
        if len(self._tasks) >= 1:
            self.show_results_button.show()
            
        # Update placeholder text
        if len(self._tasks) == 1:
            self.task_input_field.set_placeholder_text("Great! Add more tasks or click 'Show Results'...")
        elif len(self._tasks) >= 3:
            self.task_input_field.set_placeholder_text("Ready to prioritize? Click 'Show Results' below!")
        else:
            self.task_input_field.set_placeholder_text("Add another task...")
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
🎯 <b>Welcome to PriPlot - Your Task Priority Assistant!</b>

<b>🚀 Quick Start Options:</b>
• "🧪 Try Sample Tasks" - Instantly add 20 realistic work tasks
• "📋 Import List" - Paste tasks from your clipboard (one per line)
• Type manually and press Enter to add tasks one by one
• <b>Click "Show Results" when ready to see your priority chart</b>

<b>💡 Pro Tips:</b>
• Add all your tasks first, then click "Show Results" for full control
• Focus on getting all your tasks in before prioritizing
• You can always come back to add more tasks later

Happy prioritizing! 🚀📅
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("📚 PriPlot Input Guide")
        msg.setText(help_text)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F2228, stop:1 #181A1F);
                color: #E5E7EB;
                border: 2px solid #4F46E5;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #E5E7EB;
                font-size: 13px;
                min-width: 500px;
            }
            QMessageBox QPushButton {
                min-width: 100px;
                padding: 10px 16px;
            }
        """)
        msg.exec()
    
    def get_tasks(self) -> List[Task]:
        """Get current task list"""
        return self._tasks.copy()
    
    def set_tasks(self, tasks: List[Task]):
        """Set task list (for external updates)"""
        self._tasks = tasks.copy()
        self._update_display()
        self._update_ui_state() 