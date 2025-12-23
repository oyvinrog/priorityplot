from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List
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
        self.task_input.setPlaceholderText("Add a task (Ctrl+V to paste in bulk)")
        self.task_input.returnPressed.connect(self._on_return_pressed)
        layout.addWidget(self.task_input)
        
        self.add_button = QPushButton("Add")
        self.add_button.setProperty("variant", "primary")
        self.add_button.clicked.connect(self._on_add_clicked)
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

class TaskInputTable(QTableWidget):
    """Single responsibility: Display input tasks in table format following SRP
    Implements ITaskDisplayWidget protocol"""
    
    task_delete_requested = pyqtSignal(int)  # Emit when task deletion is requested
    task_renamed = pyqtSignal(int, str)  # Emit when task name is edited
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ignore_item_changes = False
        self._setup_table()
    
    def _setup_table(self):
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Task", "Remove"])
        self.setMaximumHeight(200)
        self.setColumnWidth(1, 90)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.itemChanged.connect(self._on_item_changed)
    
    def refresh_display(self, tasks: List[Task]) -> None:
        """Implementation of ITaskDisplayWidget protocol"""
        self._ignore_item_changes = True
        self.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            # Task name
            self.setItem(i, 0, QTableWidgetItem(task.task))
            
            # Delete button
            delete_btn = QPushButton("Remove")
            delete_btn.setProperty("variant", "danger")
            delete_btn.clicked.connect(lambda checked, idx=i: self.task_delete_requested.emit(idx))
            self.setCellWidget(i, 1, delete_btn)
        self._ignore_item_changes = False
    
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

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._ignore_item_changes:
            return
        if item.column() != 0:
            return
        self.task_renamed.emit(item.row(), item.text())

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
        header_label = QLabel("Tasks")
        header_label.setStyleSheet("color: #E6EAF0; font-weight: 600; font-size: 17px; padding: 10px 6px 6px 6px;")
        layout.addWidget(header_label)
        
        # Task input field
        self.task_input_field = TaskInputField()
        layout.addWidget(self.task_input_field)

        # Import from clipboard
        self.import_button = QPushButton("Import from Clipboard")
        self.import_button.setProperty("variant", "secondary")
        self.import_button.clicked.connect(self._import_from_clipboard)
        layout.addWidget(self.import_button)
        
        # Task list
        list_label = QLabel("Task list")
        list_label.setStyleSheet("color: #C9D2DD; font-weight: 600; font-size: 12px; margin-top: 14px; margin-bottom: 6px;")
        layout.addWidget(list_label)
        
        self.task_table = TaskInputTable()
        layout.addWidget(self.task_table)
        
        # Show results button
        self.show_results_button = QPushButton("Open Plot")
        self.show_results_button.setProperty("variant", "primary")
        self.show_results_button.clicked.connect(self.show_results_requested.emit)
        layout.addWidget(self.show_results_button)
        self.show_results_button.hide()
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _connect_signals(self):
        self.task_input_field.task_added.connect(self._add_task)
        self.task_table.task_delete_requested.connect(self._delete_task)
        self.task_table.task_renamed.connect(self._rename_task)
    
    def _add_task(self, task_name: str):
        """Add a single task"""
        try:
            new_task = TaskValidator.create_validated_task(task_name)
            self._tasks.append(new_task)
            self._update_display()
            self._update_ui_state()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Task", f"Could not create task:\n{str(e)}")
    
    def _delete_task(self, task_index: int):
        """Delete a task by index"""
        if 0 <= task_index < len(self._tasks):
            del self._tasks[task_index]
            self._update_display()
            self._update_ui_state()

    def _rename_task(self, task_index: int, task_name: str):
        """Rename a task by index"""
        if not (0 <= task_index < len(self._tasks)):
            return
        clean_name = TaskValidator.sanitize_task_name(task_name)
        if not TaskValidator.validate_task_name(clean_name):
            QMessageBox.warning(self, "Invalid Task", "Task name cannot be empty.")
            self._update_display()
            return
        if self._tasks[task_index].task == clean_name:
            return
        self._tasks[task_index].task = clean_name
        self._update_display()
    
    def _import_from_clipboard(self):
        """Import tasks from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            QMessageBox.warning(self, "Clipboard Empty", "No text found in clipboard.")
            return
        
        new_tasks = SampleDataGenerator.create_tasks_from_text(text)
        
        if not new_tasks:
            QMessageBox.warning(self, "No Valid Tasks", "The clipboard text doesn't contain valid tasks.")
            return
            
        self._tasks.extend(new_tasks)
        self._update_display()
        self._update_ui_state()
        
        self.task_input_field.set_placeholder_text(f"Added {len(new_tasks)} tasks.")
    
    def _update_display(self):
        """Update the task table display"""
        self.task_table.refresh_display(self._tasks)
        self.tasks_updated.emit(self._tasks)
    
    def _update_ui_state(self):
        """Update UI state based on number of tasks"""
        if len(self._tasks) >= 1:
            self.show_results_button.show()
            
        # Update placeholder text (always include Ctrl+V hint)
        if len(self._tasks) == 0:
            self.task_input_field.set_placeholder_text("Add a task (Ctrl+V to paste in bulk)")
        elif len(self._tasks) == 1:
            self.task_input_field.set_placeholder_text("Add another task or view the plot (Ctrl+V to paste)")
        elif len(self._tasks) >= 3:
            self.task_input_field.set_placeholder_text("View the plot when ready (Ctrl+V to paste more)")
        else:
            self.task_input_field.set_placeholder_text("Add another task (Ctrl+V to paste in bulk)")
    
    def get_tasks(self) -> List[Task]:
        """Get current task list"""
        return self._tasks.copy()
    
    def set_tasks(self, tasks: List[Task]):
        """Set task list (for external updates)"""
        self._tasks = tasks.copy()
        self._update_display()
        self._update_ui_state() 
