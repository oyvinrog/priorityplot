from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List

from .interfaces import ITaskCoordinator, IWidgetEventHandler
from .model import Task, TaskValidator, SampleDataGenerator
from .input_widgets import TaskInputCoordinator
from .plot_widgets import PlotResultsCoordinator
from .calendar_widgets import CalendarSchedulingWidget

class TaskCoordinatorImpl(ITaskCoordinator):
    """Implementation of task coordination following DIP - depends on abstractions"""
    
    def __init__(self, task_list: List[Task]):
        self._task_list = task_list
    
    def add_task(self, task_name: str) -> bool:
        """Add a new task"""
        try:
            new_task = TaskValidator.create_validated_task(task_name)
            self._task_list.append(new_task)
            return True
        except ValueError:
            return False
    
    def schedule_task(self, task_index: int, date, start_time: str, end_time: str) -> bool:
        """Schedule a task"""
        if 0 <= task_index < len(self._task_list):
            task = self._task_list[task_index]
            task.schedule_on_calendar(date, start_time, end_time)
            return True
        return False
    
    def get_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self._task_list.copy()
    
    def update_task_priority(self, task_index: int, value: float, time: float) -> None:
        """Update task priority values"""
        if 0 <= task_index < len(self._task_list):
            self._task_list[task_index].value = value
            self._task_list[task_index].time = time

class PriorityPlotWidget(QWidget):
    """
    Main coordinator widget following SOLID principles:
    - SRP: Single responsibility is to coordinate between modules
    - OCP: Open for extension through interfaces
    - LSP: Uses consistent interfaces
    - ISP: Clients only depend on interfaces they need
    - DIP: Depends on abstractions, not concretions
    
    Implements IWidgetEventHandler protocol methods
    """
    
    def __init__(self, task_list: List[Task] = None):
        super().__init__()
        
        # Initialize task coordination (DIP - depend on abstraction)
        self._task_list = task_list if task_list is not None else []
        self._task_coordinator = TaskCoordinatorImpl(self._task_list)
        
        # Initialize UI components
        self._setup_ui()
        self._connect_signals()
        
        # Show welcome if no tasks
        if not self._task_list:
            self._show_welcome_message()
    
    def _setup_ui(self):
        """Setup the main UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main splitter for adaptive layout
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Input panel (left side) - following SRP
        self.input_coordinator = TaskInputCoordinator()
        self.input_coordinator.set_tasks(self._task_list)
        
        # Results panel (right side) - following SRP  
        self.results_panel = QWidget()
        self._setup_results_panel()
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.input_coordinator)
        self.main_splitter.addWidget(self.results_panel)
        
        # Initially show only input panel
        self.results_panel.hide()
        
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)
    
    def _setup_results_panel(self):
        """Setup the results panel with plot and calendar"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter for plot and calendar
        results_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Plot results coordinator (left)
        self.plot_coordinator = PlotResultsCoordinator()
        
        # Calendar scheduling widget (right)
        self.calendar_widget = CalendarSchedulingWidget(self._task_list)
        
        # Add to splitter with proper proportions
        results_splitter.addWidget(self.plot_coordinator)
        results_splitter.addWidget(self.calendar_widget)
        results_splitter.setSizes([2, 1])  # 2:1 ratio
        results_splitter.setStretchFactor(0, 2)
        results_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(results_splitter)
        self.results_panel.setLayout(layout)
    
    def _connect_signals(self):
        """Connect signals between components following LSP"""
        # Input coordinator signals
        self.input_coordinator.tasks_updated.connect(self._on_tasks_updated)
        self.input_coordinator.show_results_requested.connect(self._show_results)
        
        # Plot coordinator signals  
        self.plot_coordinator.task_selected.connect(self.on_task_selected)
        self.plot_coordinator.task_updated.connect(self._on_task_updated)
        self.plot_coordinator.task_drag_started.connect(self._on_task_drag_started)
        
        # Calendar widget signals
        self.calendar_widget.task_scheduled.connect(self._on_task_scheduled)
        self.calendar_widget.task_unscheduled.connect(self._on_task_unscheduled)
        self.calendar_widget.date_selected.connect(self.on_view_changed)
    
    def _on_tasks_updated(self, tasks: List[Task]):
        """Handle task list updates from input coordinator"""
        self._task_list = tasks
        self._update_all_displays()
    
    def _on_task_updated(self, task_index: int, value: float, time: float):
        """Handle task priority updates from plot"""
        self._task_coordinator.update_task_priority(task_index, value, time)
        self._update_displays_except_plot()
    
    def _on_task_drag_started(self, task_index: int, task_data: str):
        """Handle task drag started from plot coordinator (graph or table)"""
        print(f"🎯 Main widget: Task {task_index} drag started - enabling calendar drop zones")
        # The drag is now in progress, calendar widgets should be ready to receive drops
        # No additional action needed here as Qt's drag and drop system handles the rest
    
    def _on_task_scheduled(self, task: Task):
        """Handle task scheduling from calendar"""
        self._update_displays_except_calendar()
        self.on_task_modified(self._task_list.index(task))
    
    def _on_task_unscheduled(self, task: Task):
        """Handle task unscheduling from calendar"""
        self._update_displays_except_calendar()
        self.on_task_modified(self._task_list.index(task))
    
    def _show_results(self):
        """Transition to results view"""
        if not self._task_list:
            return
        
        # Show results panel
        self.results_panel.show()
        
        # Hide input panel to give full space to results
        self.input_coordinator.hide()
        self.main_splitter.setSizes([0, 1000])
        
        # Update all displays
        self._update_all_displays()
    
    def _update_all_displays(self):
        """Update all display components"""
        self.plot_coordinator.set_tasks(self._task_list)
        self.calendar_widget.update_task_list(self._task_list)
    
    def _update_displays_except_plot(self):
        """Update displays except the plot (to avoid recursion)"""
        self.calendar_widget.update_task_list(self._task_list)
    
    def _update_displays_except_calendar(self):
        """Update displays except the calendar (to avoid recursion)"""
        self.plot_coordinator.set_tasks(self._task_list)
    
    def _show_welcome_message(self):
        """Show welcome message for new users"""
        welcome_text = """
🎉 <b>Welcome to PriPlot!</b>

Transform your task management with smart priority visualization!

<b>🚀 New User-Controlled Experience:</b>
• Choose "🧪 Try Sample Tasks" for instant exploration
• Or "📋 Import List" to paste your own tasks
• Add tasks manually with the input field
• <b>Click "Show Results" when you're ready to prioritize!</b>

<b>💡 You're in control!</b>
Add as many tasks as you want, then click the green "Show Results" button when you're ready to see your priority chart and calendar.

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
    
    # Implementation of IWidgetEventHandler interface
    def on_task_selected(self, task_index: int) -> None:
        """Handle task selection across widgets"""
        # Coordinate highlighting across all widgets
        self.plot_coordinator.highlight_task(task_index)
        
        # If task is scheduled, highlight in calendar
        if task_index < len(self._task_list):
            task = self._task_list[task_index]
            if task.is_scheduled():
                self.calendar_widget.highlight_task_date(task)
    
    def on_task_modified(self, task_index: int) -> None:
        """Handle task modification events"""
        # Update displays when task is modified
        self._update_all_displays()
    
    def on_view_changed(self, view_name) -> None:
        """Handle view state changes"""
        # Could be used for additional coordination if needed
        pass
    
    # Public API for external access (following ISP)
    def get_tasks(self) -> List[Task]:
        """Get current task list"""
        return self._task_coordinator.get_tasks()
    
    def add_task(self, task_name: str) -> bool:
        """Add a new task"""
        success = self._task_coordinator.add_task(task_name)
        if success:
            self._update_all_displays()
        return success
    
    def clear_highlighting(self):
        """Clear all highlighting across widgets"""
        self.plot_coordinator.clear_highlighting()
        self.calendar_widget.clear_calendar_highlighting() 