"""
Simple task manager interface to provide abstraction between UI components and task data.
This supports the modular architecture and separation of concerns.
"""

class TaskManager:
    """Manages task data and provides interface for UI components"""
    
    def __init__(self, task_list=None):
        self._tasks = task_list if task_list is not None else []
    
    def get_tasks(self):
        """Get all tasks"""
        return self._tasks
    
    def add_task(self, task):
        """Add a new task"""
        self._tasks.append(task)
    
    def remove_task(self, task):
        """Remove a task"""
        if task in self._tasks:
            self._tasks.remove(task)
    
    def get_task_count(self):
        """Get number of tasks"""
        return len(self._tasks)
    
    def clear_all_tasks(self):
        """Clear all tasks"""
        self._tasks.clear() 