from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List

from .interfaces import ITaskCoordinator, IWidgetEventHandler
from .model import Task, TaskValidator, SampleDataGenerator
from .input_widgets import TaskInputCoordinator
from .plot_widgets import PlotResultsCoordinator

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
        """Setup the results panel with plot"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Plot results coordinator
        self.plot_coordinator = PlotResultsCoordinator()
        
        layout.addWidget(self.plot_coordinator)
        self.results_panel.setLayout(layout)
    
    def _connect_signals(self):
        """Connect signals between components following LSP"""
        # Input coordinator signals
        self.input_coordinator.tasks_updated.connect(self._on_tasks_updated)
        self.input_coordinator.show_results_requested.connect(self._show_results)
        
        # Plot coordinator signals  
        self.plot_coordinator.task_selected.connect(self.on_task_selected)
        self.plot_coordinator.task_updated.connect(self._on_task_updated)
        self.plot_coordinator.task_added.connect(self._on_task_added_from_results)
        self.plot_coordinator.task_deleted.connect(self._on_task_deleted_from_results)
    
    def _on_tasks_updated(self, tasks: List[Task]):
        """Handle task list updates from input coordinator"""
        self._task_list = tasks
        self._update_all_displays()
    
    def _on_task_updated(self, task_index: int, value: float, time: float):
        """Handle task priority updates from plot"""
        self._task_coordinator.update_task_priority(task_index, value, time)
        self._update_all_displays()
    
    def _on_task_added_from_results(self, task_name: str):
        """Handle task addition from results view"""
        try:
            # Create task with is_new=True flag
            from .model import TaskValidator
            new_task = TaskValidator.create_validated_task(task_name)
            new_task.is_new = True  # Mark as new for visual indication
            self._task_list.append(new_task)
            
            # Mark in state manager for plot highlighting
            new_task_index = len(self._task_list) - 1
            self.plot_coordinator.plot_widget._state_manager.mark_task_new(new_task_index)
            
            self._update_all_displays()
        except ValueError as e:
            QMessageBox.warning(self, "❌ Invalid Task", f"Could not add task: {str(e)}")
    
    def _on_task_deleted_from_results(self, task_index: int):
        """Handle task deletion from results view"""
        if 0 <= task_index < len(self._task_list):
            del self._task_list[task_index]
            self._update_all_displays()
    
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
    
    def _show_welcome_message(self):
        """Show welcome message for new users"""
        main_text = "🎉 <b>Welcome to PriPlot!</b>"
        
        detailed_text = """Transform your task management with smart priority visualization!<br><br>
<b>🚀 New User-Controlled Experience:</b><br>
• Choose "🧪 Try Sample Tasks" for instant exploration<br>
• Or "📋 Import List" to paste your own tasks<br>
• Add tasks manually with the input field<br>
• <b>Click "Show Results" when you're ready to prioritize!</b><br><br>
<b>💡 You're in control!</b><br>
Add as many tasks as you want, then click the green "Show Results" button when you're ready to see your priority chart.<br><br>
Ready to boost your productivity? 🎯"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("🎯 Welcome to PriPlot!")
        msg.setText(main_text)
        msg.setInformativeText(detailed_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
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
                max-width: 600px;
            }
            QMessageBox QPushButton {
                min-width: 100px;
                padding: 10px 16px;
            }
        """)
        msg.exec()
    
    # Implementation of IWidgetEventHandler interface
    def on_task_selected(self, task_index: int) -> None:
        """Handle task selection across widgets"""
        # Coordinate highlighting across all widgets
        self.plot_coordinator.highlight_task(task_index)
    
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