from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QCalendarWidget, QTimeEdit, QListWidget, QListWidgetItem,
                             QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer, pyqtSignal, QMimeData
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent
from typing import List, Optional
from datetime import datetime, date

from .interfaces import ICalendarWidget, TaskEventEmitter
from .model import Task

class TimeSelectionDialog(QDialog):
    """Single responsibility: Handle time selection for task scheduling following SRP"""
    
    def __init__(self, task_name: str, selected_date: datetime, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"⏰ Schedule: {task_name}")
        self.setModal(True)
        self.resize(300, 200)
        self._setup_ui(task_name, selected_date)
        
    def _setup_ui(self, task_name: str, selected_date: datetime):
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #353535;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
            QTimeEdit {
                background-color: #555555;
                color: white;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3292ea;
            }
            QPushButton:pressed {
                background-color: #1a72ca;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Date display
        date_label = QLabel(f"📅 Date: {selected_date.strftime('%A, %B %d, %Y')}")
        date_label.setStyleSheet("font-weight: bold; margin-bottom: 10px; color: #2a82da;")
        layout.addWidget(date_label)
        
        # Task name display
        task_label = QLabel(f"📋 Task: {task_name}")
        task_label.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(task_label)
        
        # Time selection form
        form_layout = QFormLayout()
        
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(9, 0))  # Default 9:00 AM
        self.start_time.setDisplayFormat("hh:mm")
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(10, 0))  # Default 10:00 AM  
        self.end_time.setDisplayFormat("hh:mm")
        
        form_layout.addRow("🕐 Start Time:", self.start_time)
        form_layout.addRow("🕐 End Time:", self.end_time)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_times(self) -> tuple[str, str]:
        """Return the selected start and end times as strings"""
        return (self.start_time.time().toString("hh:mm"),
                self.end_time.time().toString("hh:mm"))

class EnhancedCalendarWidget(QCalendarWidget):
    """Single responsibility: Enhanced calendar display with task scheduling following SRP
    Implements ICalendarWidget protocol methods"""
    
    task_dropped = pyqtSignal(int, datetime)  # task_index, drop_date
    
    def __init__(self, task_list: List[Task], parent=None):
        super().__init__(parent)
        self._task_list = task_list
        self._highlighted_date = None
        self._drag_in_progress = False
        self._setup_calendar()
        self._setup_drag_drop()
        
        # Timer for cleanup
        self.highlight_cleanup_timer = QTimer()
        self.highlight_cleanup_timer.setSingleShot(True)
        self.highlight_cleanup_timer.timeout.connect(self.clear_drop_highlighting)
        
    def _setup_calendar(self):
        """Setup calendar appearance and behavior"""
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setNavigationBarVisible(True)
        
    def _setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.setAcceptDrops(True)
        
    def paintCell(self, painter, rect, date):
        """Override to paint cells with scheduled tasks in bold"""
        has_tasks = self._has_scheduled_tasks_on_date(date)
        
        if has_tasks:
            # Apply bold formatting for dates with tasks
            format = self.dateTextFormat(date)
            font = format.font()
            font.setBold(True)
            format.setFont(font)
            format.setBackground(QColor(42, 130, 218, 40))  # Light blue background
            self.setDateTextFormat(date, format)
        else:
            # Reset to normal format
            format = self.dateTextFormat(date)
            font = format.font()
            font.setBold(False)
            format.setFont(font)
            format.setBackground(QColor())  # Clear background
            self.setDateTextFormat(date, format)
        
        # Call parent for actual painting
        super().paintCell(painter, rect, date)
    
    def _has_scheduled_tasks_on_date(self, qdate: QDate) -> bool:
        """Check if any tasks are scheduled on the given QDate"""
        if not self._task_list:
            return False
        
        target_date = datetime(qdate.year(), qdate.month(), qdate.day()).date()
        
        for task in self._task_list:
            if task.is_scheduled() and task.scheduled_date.date() == target_date:
                return True
        
        return False
    
    def refresh_calendar_display(self) -> None:
        """Implementation of ICalendarWidget interface"""
        current = self.selectedDate()
        self.setSelectedDate(current)
        self.update()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("task_"):
            self._drag_in_progress = True
            event.acceptProposedAction()
            print("🎯 Drag entered calendar area")
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move events over calendar"""
        if self._drag_in_progress and event.mimeData().hasText():
            # Get the date under cursor with improved accuracy
            pos = event.position().toPoint()
            drop_date = self._get_date_at_position(pos)
            
            if drop_date:
                # Only update highlighting if we moved to a different date
                target_qdate = QDate(drop_date.year, drop_date.month, drop_date.day)
                if not self._highlighted_date or self._highlighted_date != target_qdate:
                    self.highlight_date_for_drop(drop_date)
            
            event.acceptProposedAction()
    
    def _get_date_at_position(self, pos):
        """Improved date detection at cursor position"""
        try:
            # Get calendar widget dimensions
            calendar_rect = self.rect()
            current_date = self.selectedDate()
            
            # Account for different possible header heights
            possible_header_heights = [50, 60, 70, 80, 90, 100]
            
            for header_height in possible_header_heights:
                content_height = calendar_rect.height() - header_height
                if content_height <= 0:
                    continue
                    
                # Calculate cell dimensions
                cell_width = calendar_rect.width() / 7.0
                cell_height = content_height / 6.0
                
                # Convert position to grid coordinates
                grid_x = pos.x() / cell_width
                grid_y = (pos.y() - header_height) / cell_height
                
                # Check if position is within the calendar grid
                if 0 <= grid_x < 7 and 0 <= grid_y < 6:
                    col = int(grid_x)
                    row = int(grid_y)
                    
                    # Calculate the actual date
                    year = current_date.year()
                    month = current_date.month()
                    first_day = QDate(year, month, 1)
                    first_weekday = first_day.dayOfWeek() % 7  # Monday = 1, Sunday = 0
                    
                    day_number = row * 7 + col - first_weekday + 1
                    days_in_month = first_day.daysInMonth()
                    
                    # Ensure day is valid for the current month
                    if 1 <= day_number <= days_in_month:
                        target_date = QDate(year, month, day_number)
                        if target_date.isValid():
                            return datetime(target_date.year(), target_date.month(), target_date.day())
            
        except Exception as e:
            print(f"❌ Error detecting date at position: {e}")
        
        # Fallback to currently selected date
        current_selected = self.selectedDate()
        return datetime(current_selected.year(), current_selected.month(), current_selected.day())
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events on calendar"""
        try:
            if event.mimeData().hasText() and event.mimeData().text().startswith("task_"):
                # Extract task index
                task_data = event.mimeData().text()
                task_index = int(task_data.split("_")[1])
                
                # Get the date where the drop occurred
                pos = event.position().toPoint()
                
                # For simplicity, use the currently highlighted date
                # In a more sophisticated implementation, you'd calculate the exact date
                if self._highlighted_date:
                    drop_date = datetime(self._highlighted_date.year(), 
                                       self._highlighted_date.month(), 
                                       self._highlighted_date.day())
                else:
                    current_date = self.selectedDate()
                    drop_date = datetime(current_date.year(), current_date.month(), current_date.day())
                
                print(f"📅 Task {task_index} dropped on {drop_date.strftime('%Y-%m-%d')}")
                
                # Emit signal for task scheduling
                self.task_dropped.emit(task_index, drop_date)
                
                event.acceptProposedAction()
                
                # Clear highlighting
                self.clear_drop_highlighting()
                
            else:
                event.ignore()
        except Exception as e:
            print(f"❌ Error in drop event: {e}")
            event.ignore()
        finally:
            self._drag_in_progress = False
    
    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        self._drag_in_progress = False
        self.clear_drop_highlighting()
        print("🚪 Drag left calendar area")
    
    def update_task_list(self, task_list: List[Task]):
        """Update the task list reference"""
        self._task_list = task_list
        self.refresh_calendar_display()
    
    def highlight_date_for_drop(self, date: datetime) -> None:
        """Implementation of ICalendarWidget interface with enhanced visuals"""
        self.clear_drop_highlighting()
        
        # Convert to QDate
        if isinstance(date, datetime):
            date = date.date()
        
        q_date = QDate(date.year, date.month, date.day)
        self._highlighted_date = q_date
        
        # Create enhanced highlighting with gradient effect
        highlight_format = self.dateTextFormat(q_date)
        
        # Use bright, animated highlighting
        highlight_format.setBackground(QColor(255, 100, 100, 240))  # Bright red with high opacity
        highlight_format.setForeground(QColor(255, 255, 255, 255))  # White text
        
        # Enhanced font styling
        font = highlight_format.font()
        font.setBold(True)
        font.setWeight(900)
        font.setPointSize(font.pointSize() + 4)
        highlight_format.setFont(font)
        
        self.setDateTextFormat(q_date, highlight_format)
        
        # Store original selection for restoration
        if not hasattr(self, 'original_selection'):
            self.original_selection = self.selectedDate()
        
        # Temporarily select the highlighted date for better visual feedback
        self.setSelectedDate(q_date)
        
        # Start pulsing animation
        if not hasattr(self, 'pulse_timer'):
            self.pulse_timer = QTimer()
            self.pulse_timer.timeout.connect(self._pulse_animation)
        
        self.pulse_state = 0
        self.pulse_timer.start(200)  # Pulse every 200ms
        
        print(f"🎯 Enhanced highlighting for date: {q_date.toString()} - Ready for drop!")
        
        # Force immediate update
        self.updateCells()
        self.update()
        
        # Start cleanup timer
        self.highlight_cleanup_timer.start(8000)  # Longer timeout for better UX
    
    def _pulse_animation(self):
        """Create pulsing animation effect for highlighted date"""
        if not self._highlighted_date:
            if hasattr(self, 'pulse_timer'):
                self.pulse_timer.stop()
            return
        
        self.pulse_state = (self.pulse_state + 1) % 4
        
        # Vary the highlighting intensity for pulsing effect
        alpha_values = [240, 200, 160, 200]  # Pulsing alpha values
        colors = [
            QColor(255, 100, 100, alpha_values[self.pulse_state]),
            QColor(255, 150, 100, alpha_values[self.pulse_state]),
            QColor(255, 200, 100, alpha_values[self.pulse_state]),
            QColor(255, 150, 100, alpha_values[self.pulse_state])
        ]
        
        highlight_format = self.dateTextFormat(self._highlighted_date)
        highlight_format.setBackground(colors[self.pulse_state])
        self.setDateTextFormat(self._highlighted_date, highlight_format)
        
        self.updateCells()
        self.update()
    
    def clear_drop_highlighting(self) -> None:
        """Implementation of ICalendarWidget interface with cleanup"""
        # Stop timers
        if hasattr(self, 'highlight_cleanup_timer'):
            self.highlight_cleanup_timer.stop()
        if hasattr(self, 'pulse_timer'):
            self.pulse_timer.stop()
            
        if self._highlighted_date:
            print(f"🧹 Clearing enhanced highlighting for date: {self._highlighted_date.toString()}")
            
            # Clear formatting completely first
            default_format = self.dateTextFormat(QDate())
            self.setDateTextFormat(self._highlighted_date, default_format)
            
            # Restore scheduled task formatting if needed
            if self._has_scheduled_tasks_on_date(self._highlighted_date):
                scheduled_format = self.dateTextFormat(QDate())
                font = scheduled_format.font()
                font.setBold(True)
                scheduled_format.setFont(font)
                scheduled_format.setBackground(QColor(42, 130, 218, 60))  # Light blue background
                self.setDateTextFormat(self._highlighted_date, scheduled_format)
            
            # Restore original selection
            if hasattr(self, 'original_selection'):
                self.setSelectedDate(self.original_selection)
                delattr(self, 'original_selection')
            
            self._highlighted_date = None
            self.updateCells()
            self.update()

class ScheduledTasksList(QListWidget):
    """Single responsibility: Display scheduled tasks for selected date following SRP"""
    
    task_unscheduled = pyqtSignal(int)  # task_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_list = []
        self._selected_date = None
        self._setup_list()
    
    def _setup_list(self):
        """Setup list appearance"""
        self.setStyleSheet("""
            QListWidget {
                background-color: #404040;
                border-radius: 6px;
                border: 1px solid #555555;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #555555;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
                color: white;
            }
        """)
        
        # Connect double-click to unschedule
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def update_for_date(self, selected_date: date, task_list: List[Task]):
        """Update the list to show tasks scheduled for the given date"""
        self._selected_date = selected_date
        self._task_list = task_list
        
        self.clear()
        
        # Find tasks scheduled for this date
        scheduled_tasks = []
        for i, task in enumerate(task_list):
            if task.is_scheduled() and task.scheduled_date.date() == selected_date:
                scheduled_tasks.append((i, task))
        
        if not scheduled_tasks:
            item = QListWidgetItem("📝 No tasks scheduled for this date")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.addItem(item)
            return
        
        # Add scheduled tasks to list
        for task_index, task in scheduled_tasks:
            time_str = task.scheduled_date.strftime("%H:%M")
            end_time_str = task.scheduled_end_time if task.scheduled_end_time else "End time not set"
            
            item_text = f"📅 {time_str} - {end_time_str}\n    {task.task}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, task_index)  # Store task index
            item.setToolTip(f"Double-click to unschedule\n\nTask: {task.task}\nStart: {time_str}\nEnd: {end_time_str}")
            
            # Color code by priority
            if hasattr(task, 'score'):
                task.calculate_score()
                if task.score > 2.0:
                    item.setBackground(QColor(40, 167, 69, 100))  # Green for high priority
                elif task.score > 1.0:
                    item.setBackground(QColor(255, 193, 7, 100))  # Yellow for medium priority
                else:
                    item.setBackground(QColor(108, 117, 125, 100))  # Gray for low priority
            
            self.addItem(item)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double-click to unschedule task"""
        task_index = item.data(Qt.ItemDataRole.UserRole)
        if task_index is not None:
            # Confirm unscheduling
            if self._task_list and task_index < len(self._task_list):
                task = self._task_list[task_index]
                reply = QMessageBox.question(
                    self, "🗑️ Unschedule Task",
                    f"Remove schedule for:\n\n📋 {task.task}\n\nThe task will remain in your list but won't be scheduled.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.task_unscheduled.emit(task_index)

class CalendarSchedulingWidget(QWidget):
    """Single responsibility: Coordinate calendar and scheduling functionality following SRP
    Implements TaskEventEmitter protocol methods"""
    
    # Signals defined by TaskEventEmitter protocol
    task_scheduled = pyqtSignal(object)  # Task object
    task_unscheduled = pyqtSignal(object)  # Task object
    task_updated = pyqtSignal(object)  # Task object
    date_selected = pyqtSignal(object)  # date object
    
    def __init__(self, task_list: List[Task], parent=None):
        super().__init__(parent)
        self._task_list = task_list
        self._selected_date = date.today()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Calendar section
        calendar_group = QGroupBox("📅 Calendar")
        calendar_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        calendar_layout = QVBoxLayout()
        
        # Enhanced calendar
        self.calendar = EnhancedCalendarWidget(self._task_list)
        calendar_layout.addWidget(self.calendar)
        
        calendar_group.setLayout(calendar_layout)
        layout.addWidget(calendar_group)
        
        # Selected date info
        self.selected_date_label = QLabel()
        self.selected_date_label.setStyleSheet("""
            color: #2a82da;
            font-weight: bold;
            font-size: 14px;
            padding: 8px;
            background-color: #404040;
            border-radius: 6px;
            margin: 5px 0px;
        """)
        layout.addWidget(self.selected_date_label)
        
        # Scheduled tasks section
        tasks_group = QGroupBox("📋 Scheduled Tasks")
        tasks_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        tasks_layout = QVBoxLayout()
        
        # Scheduled tasks list
        self.scheduled_tasks_list = ScheduledTasksList()
        tasks_layout.addWidget(self.scheduled_tasks_list)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_task_button = QPushButton("➕ Add Task Here")
        self.add_task_button.clicked.connect(self._add_task_for_date)
        self.add_task_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(self.add_task_button)
        
        self.clear_button = QPushButton("🗑️ Clear Selected")
        self.clear_button.clicked.connect(self._clear_selected_tasks)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        tasks_layout.addLayout(button_layout)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)
        
        self.setLayout(layout)
        
        # Initialize display
        self._update_selected_date_display()
        self._update_scheduled_tasks_display()
    
    def _connect_signals(self):
        """Connect internal widget signals"""
        self.calendar.selectionChanged.connect(self._on_date_selected)
        self.calendar.task_dropped.connect(self._on_task_dropped)
        self.scheduled_tasks_list.task_unscheduled.connect(self._on_task_unscheduled)
    
    def _on_date_selected(self):
        """Handle calendar date selection"""
        selected_qdate = self.calendar.selectedDate()
        self._selected_date = date(selected_qdate.year(), selected_qdate.month(), selected_qdate.day())
        self._update_selected_date_display()
        self._update_scheduled_tasks_display()
        self.date_selected.emit(self._selected_date)
    
    def _on_task_dropped(self, task_index: int, drop_date: datetime):
        """Handle task dropped on calendar"""
        if task_index >= len(self._task_list):
            QMessageBox.warning(self, "❌ Invalid Task", "The selected task no longer exists.")
            return
        
        task = self._task_list[task_index]
        
        # Show time selection dialog
        time_dialog = TimeSelectionDialog(task.task, drop_date, self)
        
        if time_dialog.exec() == QDialog.DialogCode.Accepted:
            start_time_str, end_time_str = time_dialog.get_times()
            
            # Parse the time strings and create datetime
            try:
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                scheduled_datetime = datetime.combine(drop_date.date(), start_time)
                
                # Schedule the task using the correct method
                task.schedule_on_calendar(scheduled_datetime, start_time_str, end_time_str)
                
                # Update displays
                self.calendar.refresh_calendar_display()
                self._update_scheduled_tasks_display()
                
                # Emit signal
                self.task_scheduled.emit(task)
                
                QMessageBox.information(
                    self, "✅ Task Scheduled!",
                    f"📅 {task.task}\n\n"
                    f"📆 Date: {drop_date.strftime('%A, %B %d, %Y')}\n"
                    f"🕐 Time: {start_time_str} - {end_time_str}"
                )
                
            except ValueError as e:
                QMessageBox.warning(self, "❌ Time Error", f"Invalid time format: {e}")
    
    def _on_task_unscheduled(self, task_index: int):
        """Handle task unscheduling"""
        if task_index < len(self._task_list):
            task = self._task_list[task_index]
            task.clear_schedule()
            
            # Update displays
            self.calendar.refresh_calendar_display()
            self._update_scheduled_tasks_display()
            
            # Emit signal
            self.task_unscheduled.emit(task)
            
            QMessageBox.information(self, "✅ Task Unscheduled", f"Removed schedule for:\n\n📋 {task.task}")
    
    def _add_task_for_date(self):
        """Add a new task directly for the selected date"""
        # This would typically integrate with the main task management system
        # For now, just show a message
        QMessageBox.information(
            self, "➕ Add Task", 
            f"Feature to add tasks directly to {self._selected_date.strftime('%B %d, %Y')} "
            f"would be implemented here.\n\n"
            f"💡 For now, add tasks using the main input area, then drag them here to schedule."
        )
    
    def _clear_selected_tasks(self):
        """Clear all tasks scheduled for the selected date"""
        scheduled_count = sum(1 for task in self._task_list 
                            if task.is_scheduled() and task.scheduled_date.date() == self._selected_date)
        
        if scheduled_count == 0:
            QMessageBox.information(self, "📅 No Tasks", "No tasks are scheduled for this date.")
            return
        
        reply = QMessageBox.question(
            self, "🗑️ Clear All Tasks",
            f"Remove all {scheduled_count} scheduled tasks from {self._selected_date.strftime('%B %d, %Y')}?\n\n"
            f"The tasks will remain in your list but won't be scheduled.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Unschedule all tasks for this date
            tasks_to_unschedule = []
            for task in self._task_list:
                if task.is_scheduled() and task.scheduled_date.date() == self._selected_date:
                    tasks_to_unschedule.append(task)
            
            for task in tasks_to_unschedule:
                task.clear_schedule()
                self.task_unscheduled.emit(task)
            
            # Update displays
            self.calendar.refresh_calendar_display()
            self._update_scheduled_tasks_display()
            
            QMessageBox.information(self, "✅ Tasks Cleared", f"Removed {len(tasks_to_unschedule)} scheduled tasks.")
    
    def _update_selected_date_display(self):
        """Update the selected date display label"""
        formatted_date = self._selected_date.strftime('%A, %B %d, %Y')
        self.selected_date_label.setText(f"📅 Selected: {formatted_date}")
    
    def _update_scheduled_tasks_display(self):
        """Update the scheduled tasks list"""
        self.scheduled_tasks_list.update_for_date(self._selected_date, self._task_list)
    
    def update_task_list(self, task_list: List[Task]):
        """Update the task list reference"""
        self._task_list = task_list
        self.calendar.update_task_list(task_list)
        self._update_scheduled_tasks_display()
    
    def highlight_task_date(self, task: Task):
        """Highlight the date when a task is scheduled"""
        if task.is_scheduled():
            # Select the date on calendar
            task_date = task.scheduled_date.date()
            q_date = QDate(task_date.year, task_date.month, task_date.day)
            self.calendar.setSelectedDate(q_date)
            
            # Refresh display
            self._on_date_selected()
    
    def clear_calendar_highlighting(self):
        """Clear any calendar highlighting"""
        self.calendar.clear_drop_highlighting() 