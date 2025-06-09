from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, 
                             QListWidget, QListWidgetItem, QPushButton, QTimeEdit,
                             QDialog, QDialogButtonBox, QCalendarWidget, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime
from .model import Task, TaskValidator


class ScheduleCalendarWidget(QCalendarWidget):
    """Custom calendar widget that shows days with scheduled tasks in bold"""
    
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.highlighted_date = None  # Track currently highlighted date during drag
        self.drag_in_progress = False  # Track if we're currently in a drag operation
        
        # Timer to clean up highlighting if drag events don't fire properly
        self.highlight_cleanup_timer = QTimer()
        self.highlight_cleanup_timer.setSingleShot(True)
        self.highlight_cleanup_timer.timeout.connect(self.clear_drop_highlighting)
        
        # Prevent month changes during drag operations
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setNavigationBarVisible(True)
    
    def paintCell(self, painter, rect, date):
        """Override to paint cells with scheduled tasks in bold"""
        has_tasks = self.has_scheduled_tasks_on_date(date)
        
        if has_tasks:
            format = self.dateTextFormat(date)
            font = format.font()
            font.setBold(True)
            format.setFont(font)
            format.setBackground(QColor(42, 130, 218, 40))  # Light blue background
            self.setDateTextFormat(date, format)
        else:
            format = self.dateTextFormat(date)
            font = format.font()
            font.setBold(False)
            format.setFont(font)
            format.setBackground(QColor())  # Clear background
            self.setDateTextFormat(date, format)
        
        super().paintCell(painter, rect, date)
    
    def has_scheduled_tasks_on_date(self, qdate):
        """Check if any tasks are scheduled on the given QDate"""
        if not hasattr(self.task_manager, 'get_tasks') or not self.task_manager.get_tasks():
            return False
        
        target_date = datetime(qdate.year(), qdate.month(), qdate.day()).date()
        
        for task in self.task_manager.get_tasks():
            if task.is_scheduled() and task.scheduled_date.date() == target_date:
                return True
        
        return False
    
    def refresh_calendar_display(self):
        """Force refresh of the calendar to update bold formatting"""
        current = self.selectedDate()
        self.setSelectedDate(current)
        self.update()

    def highlight_date_for_drop(self, target_date):
        """Highlight a specific date during drag operations with enhanced animation"""
        self.clear_drop_highlighting()
        
        if isinstance(target_date, datetime):
            target_date = target_date.date()
        
        q_date = QDate(target_date.year, target_date.month, target_date.day)
        self.highlighted_date = q_date
        
        highlight_format = self.dateTextFormat(q_date)
        # Use enhanced highlighting with better colors
        highlight_format.setBackground(QColor(255, 100, 100, 240))  # Bright red-orange with high opacity
        highlight_format.setForeground(QColor(255, 255, 255, 255))  # White text
        
        font = highlight_format.font()
        font.setBold(True)
        font.setWeight(900)
        font.setPointSize(font.pointSize() + 5)  # Even larger font
        highlight_format.setFont(font)
        
        self.setDateTextFormat(q_date, highlight_format)
        
        # Change selection for additional visual feedback
        current_selection = self.selectedDate()
        if current_selection != q_date:
            if not hasattr(self, 'original_selection'):
                self.original_selection = current_selection
            self.setSelectedDate(q_date)
        
        # Enhanced animation effect with improved timing
        if not hasattr(self, 'highlight_timer'):
            self.highlight_timer = QTimer()
            self.highlight_timer.timeout.connect(self.pulse_highlight)
        
        self.highlight_timer.start(180)  # Faster pulse for better responsiveness
        self.pulse_state = 0  # Track pulse animation state
        
        print(f"🎯 Enhanced calendar highlighting for {q_date.toString()} - Drop target ready!")
        
        self.update()
        self.highlight_cleanup_timer.start(8000)  # Longer timeout
    
    def pulse_highlight(self):
        """Enhanced pulse highlight animation"""
        if not hasattr(self, 'highlighted_date') or not self.highlighted_date:
            if hasattr(self, 'highlight_timer'):
                self.highlight_timer.stop()
            return
        
        self.pulse_state = (self.pulse_state + 1) % 6  # 6 states for smoother animation
        
        # More sophisticated color animation
        base_colors = [
            QColor(255, 100, 100, 240),  # Red
            QColor(255, 130, 100, 220),  # Red-orange
            QColor(255, 160, 100, 200),  # Orange
            QColor(255, 180, 100, 220),  # Light orange
            QColor(255, 140, 100, 240),  # Back to red-orange
            QColor(255, 110, 100, 250)   # Bright red
        ]
        
        highlight_format = self.dateTextFormat(self.highlighted_date)
        highlight_format.setBackground(base_colors[self.pulse_state])
        
        # Also pulse the font size slightly
        font = highlight_format.font()
        size_offset = [5, 6, 7, 6, 5, 4][self.pulse_state]
        font.setPointSize(font.pointSize() - font.pointSize() % 10 + size_offset)
        highlight_format.setFont(font)
        
        self.setDateTextFormat(self.highlighted_date, highlight_format)
        self.updateCells()
        self.update()
    
    def clear_drop_highlighting(self):
        """Clear any drag drop highlighting"""
        # Stop timers
        if hasattr(self, 'highlight_cleanup_timer'):
            self.highlight_cleanup_timer.stop()
        if hasattr(self, 'highlight_timer'):
            self.highlight_timer.stop()
            
        if self.highlighted_date:
            # Clear the date format
            self.setDateTextFormat(self.highlighted_date, self.dateTextFormat(QDate()))
            
            # Reapply scheduled task formatting if needed
            if self.has_scheduled_tasks_on_date(self.highlighted_date):
                scheduled_format = self.dateTextFormat(QDate())
                font = scheduled_format.font()
                font.setBold(True)
                scheduled_format.setFont(font)
                scheduled_format.setBackground(QColor(42, 130, 218, 40))
                self.setDateTextFormat(self.highlighted_date, scheduled_format)
            
            # Restore original selection
            if hasattr(self, 'original_selection'):
                self.setSelectedDate(self.original_selection)
                delattr(self, 'original_selection')
            
            self.highlighted_date = None
            self.updateCells()
            self.update()


class TimeSelectionDialog(QDialog):
    """Dialog for selecting start and end times when scheduling a task"""
    
    def __init__(self, task_name, selected_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"⏰ Schedule: {task_name}")
        self.setModal(True)
        self.resize(300, 200)
        
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
        self.start_time.setTime(QTime(9, 0))
        self.start_time.setDisplayFormat("hh:mm")
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(10, 0))
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
    
    def get_times(self):
        """Return the selected start and end times as strings"""
        return (self.start_time.time().toString("hh:mm"),
                self.end_time.time().toString("hh:mm"))


class TaskSchedulerWidget(QWidget):
    """Widget responsible for calendar-based task scheduling"""
    
    # Signals
    task_scheduled = pyqtSignal(object)  # Emitted when a task is scheduled
    task_unscheduled = pyqtSignal(object)  # Emitted when a task is unscheduled
    date_selected = pyqtSignal(QDate)  # Emitted when calendar date changes
    
    def __init__(self, task_manager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the scheduler UI"""
        layout = QVBoxLayout()
        
        # Calendar header
        calendar_header = QLabel("📅 Task Scheduler")
        calendar_header.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(calendar_header)
        
        # Instructions
        instructions = QLabel("💡 Drag tasks directly to any day")
        instructions.setStyleSheet("color: #888888; font-size: 11px; padding: 0 10px 5px 10px; font-style: italic;")
        layout.addWidget(instructions)
        
        # Calendar widget
        self.calendar = ScheduleCalendarWidget(self.task_manager)
        self.setup_calendar_styling()
        layout.addWidget(self.calendar)
        
        # Selected date display
        self.selected_date_label = QLabel("📍 Selected: Today")
        self.selected_date_label.setStyleSheet("""
            color: #2a82da; 
            font-weight: bold; 
            font-size: 12px; 
            padding: 8px; 
            background-color: #404040; 
            border-radius: 4px; 
            margin: 5px;
        """)
        layout.addWidget(self.selected_date_label)
        
        # Time selection frame
        time_frame = self.create_time_selection_frame()
        layout.addWidget(time_frame)
        
        # Scheduled tasks frame
        scheduled_frame = self.create_scheduled_tasks_frame()
        layout.addWidget(scheduled_frame)
        
        # Connect signals
        self.calendar.selectionChanged.connect(self.on_date_selection_changed)
        self.calendar.currentPageChanged.connect(self.calendar.refresh_calendar_display)
        
        # Set up drag and drop
        self.setup_drag_drop()
        
        # Update initial display
        self.update_selected_date_display()
        
        self.setLayout(layout)
    
    def setup_calendar_styling(self):
        """Apply styling to the calendar widget"""
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #404040;
                color: white;
                selection-background-color: #2a82da;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #888888;
            }
            QCalendarWidget QWidget {
                background-color: #404040;
                color: white;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #555555;
                border: 1px solid #666666;
                border-radius: 2px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #2a82da;
            }
            QCalendarWidget QMenu {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
            }
            QCalendarWidget QSpinBox {
                background-color: #555555;
                color: white;
                border: 1px solid #666666;
                border-radius: 2px;
            }
        """)
    
    def create_time_selection_frame(self):
        """Create the time selection frame"""
        time_frame = QGroupBox("⏰ Time Schedule")
        time_frame.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        time_layout = QFormLayout()
        
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(9, 0))
        self.start_time.setStyleSheet("""
            QTimeEdit {
                background-color: #555555;
                color: white;
                border: 1px solid #666666;
                border-radius: 2px;
                padding: 4px;
            }
        """)
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(10, 0))
        self.end_time.setStyleSheet("""
            QTimeEdit {
                background-color: #555555;
                color: white;
                border: 1px solid #666666;
                border-radius: 2px;
                padding: 4px;
            }
        """)
        
        time_layout.addRow("Start:", self.start_time)
        time_layout.addRow("End:", self.end_time)
        time_frame.setLayout(time_layout)
        
        return time_frame
    
    def create_scheduled_tasks_frame(self):
        """Create the scheduled tasks list frame"""
        scheduled_frame = QGroupBox("📋 Scheduled Tasks")
        scheduled_frame.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        scheduled_layout = QVBoxLayout()
        
        self.scheduled_tasks_list = QListWidget()
        self.scheduled_tasks_list.setStyleSheet("""
            QListWidget {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #2a82da;
            }
            QListWidget::item:hover {
                background-color: #505050;
            }
        """)
        self.scheduled_tasks_list.setMaximumHeight(150)
        scheduled_layout.addWidget(self.scheduled_tasks_list)
        
        # Clear schedule button
        clear_button = QPushButton("🗑️ Clear Selected")
        clear_button.clicked.connect(self.clear_selected_schedule)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        scheduled_layout.addWidget(clear_button)
        
        # Add task button
        add_task_button = QPushButton("➕ Add Task")
        add_task_button.clicked.connect(self.add_task_from_calendar)
        add_task_button.setToolTip("Create a new task for the selected date")
        add_task_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        scheduled_layout.addWidget(add_task_button)
        
        scheduled_frame.setLayout(scheduled_layout)
        return scheduled_frame
    
    def setup_drag_drop(self):
        """Set up drag and drop functionality"""
        self.calendar.setAcceptDrops(True)
        self.calendar.dragEnterEvent = self.calendar_drag_enter_event
        self.calendar.dragMoveEvent = self.calendar_drag_move_event
        self.calendar.dragLeaveEvent = self.calendar_drag_leave_event
        self.calendar.dropEvent = self.calendar_drop_event
    
    def calendar_drag_enter_event(self, event):
        """Handle drag enter events for the calendar"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("task_"):
            self.calendar.drag_in_progress = True
            self.calendar.original_month = self.calendar.selectedDate()
            event.acceptProposedAction()
        else:
            event.ignore()

    def calendar_drag_move_event(self, event):
        """Handle drag move events for the calendar"""
        if event.mimeData().hasText() and event.mimeData().text().startswith("task_"):
            event.acceptProposedAction()
            
            drop_pos = event.position()
            hovered_date = self.get_date_at_position(drop_pos)
            
            if hovered_date:
                q_date = QDate(hovered_date.year, hovered_date.month, hovered_date.day)
                # Only update highlighting if we moved to a different date
                if not self.calendar.highlighted_date or self.calendar.highlighted_date != q_date:
                    self.calendar.highlight_date_for_drop(hovered_date)
                    
            # Prevent month navigation during drag
            if hasattr(self.calendar, 'original_month'):
                current_month = self.calendar.selectedDate()
                if (current_month.year() != self.calendar.original_month.year() or 
                    current_month.month() != self.calendar.original_month.month()):
                    corrected_date = QDate(self.calendar.original_month.year(), 
                                         self.calendar.original_month.month(), 
                                         self.calendar.original_month.day())
                    self.calendar.setSelectedDate(corrected_date)
        else:
            self.calendar.clear_drop_highlighting()
            event.ignore()

    def calendar_drag_leave_event(self, event):
        """Handle drag leave events for the calendar"""
        self.calendar.drag_in_progress = False
        self.calendar.clear_drop_highlighting()
        event.accept()

    def calendar_drop_event(self, event):
        """Handle drop events for the calendar"""
        self.calendar.drag_in_progress = False
        self.calendar.clear_drop_highlighting()
        
        if event.mimeData().hasText() and event.mimeData().text().startswith("task_"):
            task_index_str = event.mimeData().text().replace("task_", "")
            try:
                task_index = int(task_index_str)
                tasks = self.task_manager.get_tasks()
                
                if 0 <= task_index < len(tasks):
                    drop_pos = event.position()
                    calendar_date = self.get_date_at_position(drop_pos)
                    
                    if calendar_date:
                        task = tasks[task_index]
                        
                        # Show time selection dialog
                        dialog = TimeSelectionDialog(task.task, calendar_date, self)
                        self.set_smart_default_times(dialog, calendar_date)
                        
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            start_time, end_time = dialog.get_times()
                            
                            # Schedule the task
                            task.schedule_on_calendar(
                                datetime.combine(calendar_date, datetime.min.time()),
                                start_time,
                                end_time
                            )
                            
                            # Update calendar selection
                            q_date = QDate(calendar_date.year, calendar_date.month, calendar_date.day)
                            self.calendar.setSelectedDate(q_date)
                            
                            # Update displays and emit signal
                            self.update_scheduled_tasks_display()
                            self.calendar.refresh_calendar_display()
                            self.task_scheduled.emit(task)
                            
                            event.acceptProposedAction()
                        else:
                            event.ignore()
                    else:
                        event.ignore()
                else:
                    event.ignore()
            except ValueError:
                event.ignore()
        else:
            event.ignore()
    
    def get_date_at_position(self, pos):
        """Get the date at the given position in the calendar widget with improved accuracy"""
        try:
            calendar_rect = self.calendar.rect()
            current_date = self.calendar.selectedDate()
            
            # Use multiple header height possibilities for better accuracy
            possible_header_heights = [50, 60, 70, 80, 90, 100, 110, 120]
            
            for header_height in possible_header_heights:
                content_height = calendar_rect.height() - header_height
                if content_height <= 0:
                    continue
                    
                cell_width = calendar_rect.width() / 7.0
                cell_height = content_height / 6.0
                
                grid_x = pos.x() / cell_width
                grid_y = (pos.y() - header_height) / cell_height
                
                if 0 <= grid_x < 7 and 0 <= grid_y < 6:
                    col = int(grid_x)
                    row = int(grid_y)
                    
                    year = current_date.year()
                    month = current_date.month()
                    first_day = QDate(year, month, 1)
                    first_weekday = first_day.dayOfWeek() % 7
                    
                    day_number = row * 7 + col - first_weekday + 1
                    days_in_month = first_day.daysInMonth()
                    
                    if 1 <= day_number <= days_in_month:
                        target_date = QDate(year, month, day_number)
                        if target_date.isValid():
                            return datetime(target_date.year(), target_date.month(), target_date.day()).date()
            
        except Exception as e:
            print(f"❌ Error detecting date at position: {e}")
        
        # Fallback to current selected date
        current_selected = self.calendar.selectedDate()
        return datetime(current_selected.year(), current_selected.month(), current_selected.day()).date()
    
    def set_smart_default_times(self, dialog, date):
        """Set smart default times based on existing scheduled tasks for the date"""
        latest_end_time = QTime(9, 0)
        
        for task in self.task_manager.get_tasks():
            if (task.is_scheduled() and 
                task.scheduled_date.date() == date and 
                task.scheduled_end_time):
                try:
                    task_end_time = QTime.fromString(task.scheduled_end_time, "hh:mm")
                    if not task_end_time.isValid():
                        task_end_time = QTime.fromString(task.scheduled_end_time, "HH:mm")
                    
                    if task_end_time.isValid() and task_end_time > latest_end_time:
                        latest_end_time = task_end_time
                except:
                    pass
        
        if latest_end_time != QTime(9, 0):
            start_time = latest_end_time.addSecs(30 * 60)
        else:
            start_time = QTime(9, 0)
        
        end_time = start_time.addSecs(60 * 60)
        
        dialog.start_time.setTime(start_time)
        dialog.end_time.setTime(end_time)
    
    def on_date_selection_changed(self):
        """Handle calendar date selection changes"""
        self.update_selected_date_display()
        self.update_scheduled_tasks_display()
        self.date_selected.emit(self.calendar.selectedDate())
    
    def update_selected_date_display(self):
        """Update the selected date display label"""
        selected_date = self.calendar.selectedDate().toString("dddd, MMMM d, yyyy")
        self.selected_date_label.setText(f"📍 Selected: {selected_date}")
    
    def update_scheduled_tasks_display(self):
        """Update the scheduled tasks list based on selected calendar date"""
        self.scheduled_tasks_list.clear()
        
        tasks = self.task_manager.get_tasks()
        if not tasks:
            return
            
        q_date = self.calendar.selectedDate()
        selected_date = datetime(q_date.year(), q_date.month(), q_date.day()).date()
        
        for i, task in enumerate(tasks):
            if (task.is_scheduled() and 
                task.scheduled_date.date() == selected_date):
                
                time_info = ""
                if task.scheduled_start_time and task.scheduled_end_time:
                    time_info = f" ({task.scheduled_start_time} - {task.scheduled_end_time})"
                
                item_text = f"{task.task}{time_info}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, i)
                self.scheduled_tasks_list.addItem(list_item)
    
    def clear_selected_schedule(self):
        """Clear the schedule for the selected task"""
        current_item = self.scheduled_tasks_list.currentItem()
        if current_item:
            task_index = current_item.data(Qt.ItemDataRole.UserRole)
            tasks = self.task_manager.get_tasks()
            
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                task.clear_schedule()
                self.update_scheduled_tasks_display()
                self.calendar.refresh_calendar_display()
                self.task_unscheduled.emit(task)
    
    def add_task_from_calendar(self):
        """Add a new task directly from the calendar view"""
        selected_date = self.calendar.selectedDate()
        selected_datetime = datetime(selected_date.year(), selected_date.month(), selected_date.day())
        selected_date_str = selected_datetime.strftime('%A, %B %d, %Y')
        
        # Create dialog for task input
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📅 Add Task for {selected_date_str}")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        # Apply styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #353535;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #555555;
                color: white;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
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
        date_label = QLabel(f"📅 Creating task for: {selected_date_str}")
        date_label.setStyleSheet("font-weight: bold; margin-bottom: 15px; color: #2a82da;")
        layout.addWidget(date_label)
        
        # Task input form
        from PyQt6.QtWidgets import QLineEdit
        form_layout = QFormLayout()
        
        task_input = QLineEdit()
        task_input.setPlaceholderText("Enter task name...")
        form_layout.addRow("📋 Task Name:", task_input)
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("1.0-5.0 (importance/impact)")
        value_input.setText("3.0")
        form_layout.addRow("★ Value:", value_input)
        
        time_input = QLineEdit()
        time_input.setPlaceholderText("0.5-8.0 (hours needed)")
        time_input.setText("2.0")
        form_layout.addRow("⏰ Time (hrs):", time_input)
        
        start_time = QTimeEdit()
        start_time.setTime(QTime(9, 0))
        start_time.setDisplayFormat("hh:mm")
        form_layout.addRow("🕐 Start Time:", start_time)
        
        end_time = QTimeEdit()
        end_time.setTime(QTime(11, 0))
        end_time.setDisplayFormat("hh:mm")
        form_layout.addRow("🕐 End Time:", end_time)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        task_input.setFocus()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_name = task_input.text().strip()
            if not task_name:
                QMessageBox.warning(self, "❌ Invalid Input", "Please enter a task name!")
                return
                
            try:
                value = float(value_input.text())
                time = float(time_input.text())
                
                # Use TaskValidator for validation
                if not TaskValidator.validate_value(value):
                    raise ValueError(f"Value must be between {TaskValidator.get_default_values()[0]} and 6.0")
                if not TaskValidator.validate_time(time):
                    raise ValueError(f"Time must be between 0.1 and 8.0 hours")
                    
            except ValueError as e:
                QMessageBox.warning(self, "❌ Invalid Input", f"Please enter valid numbers:\n\n{str(e)}")
                return
            
            # Create and schedule new task using TaskValidator
            try:
                new_task = TaskValidator.create_validated_task(task_name, value, time)
                
                selected_datetime = datetime.combine(
                    datetime(selected_date.year(), selected_date.month(), selected_date.day()).date(),
                    datetime.min.time()
                )
                
                start_time_str = start_time.time().toString("hh:mm")
                end_time_str = end_time.time().toString("hh:mm")
                
                new_task.schedule_on_calendar(selected_datetime, start_time_str, end_time_str)
                
                # Add to task manager and update displays
                self.task_manager.add_task(new_task)
                self.update_scheduled_tasks_display()
                self.calendar.refresh_calendar_display()
                self.task_scheduled.emit(new_task)
                
                QMessageBox.information(
                    self, 
                    "✅ Task Created!", 
                    f"🎉 Created and scheduled '{task_name}' for {selected_date_str}\n\n"
                    f"⏰ Time: {start_time_str} - {end_time_str}\n"
                    f"★ Value: {value} | ⏰ Time: {time} hrs"
                )
                
            except ValueError as e:
                QMessageBox.warning(self, "❌ Task Creation Failed", f"Could not create task:\n\n{str(e)}")
    
    def highlight_task_in_calendar(self, task):
        """Highlight the scheduled date of a task in the calendar"""
        if not task.is_scheduled():
            return
            
        scheduled_date = task.scheduled_date.date()
        q_date = QDate(scheduled_date.year, scheduled_date.month, scheduled_date.day)
        
        self.calendar.setSelectedDate(q_date)
        self.calendar.highlight_date_for_drop(scheduled_date)
        
        # Apply selection highlighting
        selection_format = self.calendar.dateTextFormat(q_date)
        selection_format.setBackground(QColor(42, 130, 218, 255))
        selection_format.setForeground(QColor(255, 255, 255, 255))
        
        font = selection_format.font()
        font.setBold(True)
        font.setWeight(900)
        font.setPointSize(font.pointSize() + 2)
        selection_format.setFont(font)
        
        self.calendar.setDateTextFormat(q_date, selection_format)
        self.calendar.update()
        
        self.update_selected_date_display()
        self.update_scheduled_tasks_display()
    
    def clear_calendar_highlighting(self):
        """Clear any highlighting from the calendar"""
        self.calendar.clear_drop_highlighting()
    
    def refresh_calendar(self):
        """Force refresh of the calendar display"""
        self.calendar.refresh_calendar_display() 