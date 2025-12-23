from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QMessageBox, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from typing import List

from .interfaces import ITaskCoordinator, IWidgetEventHandler
from .model import Task, TaskValidator, SampleDataGenerator
from .input_widgets import TaskInputCoordinator
from .plot_widgets import PlotResultsCoordinator
from .goal_memory import GoalMemory

class TaskCoordinatorImpl(ITaskCoordinator):
    """Implementation of task coordination following DIP - depends on abstractions"""
    
    def __init__(self, task_list: List[Task], goal_memory: GoalMemory = None):
        self._task_list = task_list
        self._goal_memory = goal_memory
    
    def add_task(self, task_name: str) -> bool:
        """Add a new task"""
        try:
            new_task = self.create_task_with_memory(task_name)
            self._task_list.append(new_task)
            return True
        except ValueError:
            return False

    def create_task_with_memory(self, task_name: str) -> Task:
        if self._goal_memory is None:
            return TaskValidator.create_validated_task(task_name)
        match = self._goal_memory.find_match(task_name)
        if match:
            return TaskValidator.create_validated_task(task_name, match.value, match.time)
        return TaskValidator.create_validated_task(task_name)
    
    
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
        self._goal_memory = GoalMemory()
        self._task_coordinator = TaskCoordinatorImpl(self._task_list, self._goal_memory)
        
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
        self.input_coordinator = TaskInputCoordinator(goal_memory=self._goal_memory)
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
        
        # Add Ctrl+V shortcut for pasting tasks from clipboard
        self._setup_paste_shortcut()
    
    def _setup_paste_shortcut(self):
        """Setup Ctrl+V shortcut to paste tasks when not in a text field"""
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.paste_shortcut.activated.connect(self._handle_paste_shortcut)
    
    def _handle_paste_shortcut(self):
        """Handle Ctrl+V - import tasks if not focused on a text input"""
        from PyQt6.QtWidgets import QApplication
        focused_widget = QApplication.focusWidget()
        # Only import tasks if not typing in a text field
        if not isinstance(focused_widget, QLineEdit):
            self.input_coordinator._import_from_clipboard()
    
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
        self.plot_coordinator.task_renamed.connect(self._on_task_renamed_from_results)
        self.plot_coordinator.task_move_finished.connect(self._on_task_move_finished)
    
    def _on_tasks_updated(self, tasks: List[Task]):
        """Handle task list updates from input coordinator"""
        self._task_list = tasks
        self._update_all_displays()
    
    def _on_task_updated(self, task_index: int, value: float, time: float):
        """Handle task priority updates from plot"""
        self._task_coordinator.update_task_priority(task_index, value, time)
        self._update_all_displays()
    
    def _on_task_deleted_from_results(self, task_index: int):
        """Handle task deletion from results view"""
        if 0 <= task_index < len(self._task_list):
            del self._task_list[task_index]
            self._update_all_displays()

    def _on_task_added_from_results(self, task_name: str):
        """Handle task addition from results view"""
        try:
            new_task = self._task_coordinator.create_task_with_memory(task_name)
            self._task_list.append(new_task)
            self._update_all_displays()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Task", f"Could not add task:\n{str(e)}")

    def _on_task_renamed_from_results(self, task_index: int, task_name: str):
        """Handle task rename from results view"""
        if 0 <= task_index < len(self._task_list):
            self._task_list[task_index].task = task_name
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
        save_memory = True
        if hasattr(self, "plot_coordinator") and hasattr(self.plot_coordinator, "plot_widget"):
            save_memory = not self.plot_coordinator.plot_widget.dragging
        self._goal_memory.update_from_tasks(self._task_list, save=save_memory)
        self.plot_coordinator.set_tasks(self._task_list)

    def _on_task_move_finished(self, task_index: int, value: float, time: float):
        """Persist goal memory after a drag finishes."""
        self._goal_memory.update_from_tasks(self._task_list, save=True)
    
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
