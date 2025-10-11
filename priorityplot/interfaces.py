from abc import ABC, abstractmethod
from typing import List, Optional, Protocol, runtime_checkable
from PyQt6.QtCore import pyqtSignal
from .model import Task

@runtime_checkable
class ITaskInputWidget(Protocol):
    """Protocol for task input widgets following ISP"""
    
    def get_current_task_text(self) -> str:
        """Get the current task text from input"""
        ...
    
    def clear_input(self) -> None:
        """Clear the input field"""
        ...
    
    def set_placeholder_text(self, text: str) -> None:
        """Set placeholder text for user guidance"""
        ...

@runtime_checkable
class ITaskDisplayWidget(Protocol):
    """Protocol for widgets that display task lists"""
    
    def refresh_display(self, tasks: List[Task]) -> None:
        """Refresh the display with updated task list"""
        ...
    
    def highlight_task(self, task_index: int) -> None:
        """Highlight a specific task"""
        ...
    
    def clear_highlighting(self) -> None:
        """Clear all highlighting"""
        ...

@runtime_checkable
class IPlotWidget(Protocol):
    """Protocol for plot/visualization widgets"""
    
    def update_plot(self, tasks: List[Task]) -> None:
        """Update the plot with new task data"""
        ...
    
    def highlight_task_in_plot(self, task_index: int) -> None:
        """Highlight a specific task in the plot"""
        ...

@runtime_checkable
class IExportService(Protocol):
    """Protocol for export functionality following SRP - converted from ABC to avoid Qt metaclass conflict"""
    
    def export_tasks(self, tasks: List[Task], file_path: str) -> bool:
        """Export tasks to specified file path"""
        ...
    
    def get_default_export_path(self) -> str:
        """Get default export directory"""
        ...

class ITaskCoordinator(ABC):
    """Interface for coordinating task operations following SRP"""
    
    @abstractmethod
    def add_task(self, task_name: str) -> bool:
        """Add a new task"""
        pass
    
    @abstractmethod
    def get_tasks(self) -> List[Task]:
        """Get all tasks"""
        pass
    
    @abstractmethod
    def update_task_priority(self, task_index: int, value: float, time: float) -> None:
        """Update task priority values"""
        pass

@runtime_checkable
class IWidgetEventHandler(Protocol):
    """Protocol for handling inter-widget communication - converted from ABC to avoid Qt metaclass conflict"""
    
    def on_task_selected(self, task_index: int) -> None:
        """Handle task selection across widgets"""
        ...
    
    def on_task_modified(self, task_index: int) -> None:
        """Handle task modification events"""
        ...
    
    def on_view_changed(self, view_name: str) -> None:
        """Handle view state changes"""
        ... 