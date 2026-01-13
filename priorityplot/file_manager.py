"""
File Manager for Priority Plot - handles save, load, and recent files functionality.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path


@dataclass
class PriorityPlotFile:
    """Represents a priority plot file with metadata."""
    version: str = "1.0"
    created_at: str = ""
    modified_at: str = ""
    tasks: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []


class RecentFilesManager:
    """Manages the list of recently opened files."""
    
    MAX_RECENT_FILES = 10
    
    def __init__(self, storage_path: Optional[str] = None):
        self._storage_path = storage_path or self._default_storage_path()
        self._recent_files: List[Dict[str, str]] = []
        self._load()
    
    def _default_storage_path(self) -> str:
        base_dir = os.path.join(os.path.expanduser("~"), ".priorityplot")
        return os.path.join(base_dir, "recent_files.json")
    
    def _load(self) -> None:
        """Load recent files list from storage."""
        if not os.path.exists(self._storage_path):
            return
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._recent_files = data.get("recent_files", [])
                # Filter out files that no longer exist
                self._recent_files = [
                    rf for rf in self._recent_files 
                    if os.path.exists(rf.get("path", ""))
                ]
        except Exception:
            self._recent_files = []
    
    def _save(self) -> None:
        """Save recent files list to storage."""
        storage_dir = os.path.dirname(self._storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)
        
        payload = {"recent_files": self._recent_files}
        tmp_path = f"{self._storage_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp_path, self._storage_path)
    
    def add_file(self, file_path: str) -> None:
        """Add a file to the recent files list."""
        file_path = os.path.abspath(file_path)
        
        # Remove if already exists
        self._recent_files = [
            rf for rf in self._recent_files 
            if rf.get("path") != file_path
        ]
        
        # Add to the beginning
        self._recent_files.insert(0, {
            "path": file_path,
            "name": os.path.basename(file_path),
            "accessed_at": datetime.utcnow().isoformat()
        })
        
        # Keep only the most recent
        self._recent_files = self._recent_files[:self.MAX_RECENT_FILES]
        self._save()
    
    def get_recent_files(self) -> List[Dict[str, str]]:
        """Get the list of recent files."""
        # Filter out files that no longer exist
        valid_files = [
            rf for rf in self._recent_files 
            if os.path.exists(rf.get("path", ""))
        ]
        if len(valid_files) != len(self._recent_files):
            self._recent_files = valid_files
            self._save()
        return self._recent_files.copy()
    
    def clear(self) -> None:
        """Clear the recent files list."""
        self._recent_files = []
        self._save()


class FileManager:
    """Handles file operations for Priority Plot files (.priplot)."""
    
    FILE_EXTENSION = ".priplot"
    FILE_FILTER = "Priority Plot Files (*.priplot);;All Files (*)"
    
    def __init__(self):
        self._current_file: Optional[str] = None
        self._is_modified: bool = False
        self._recent_files_manager = RecentFilesManager()
    
    @property
    def current_file(self) -> Optional[str]:
        """Get the current file path."""
        return self._current_file
    
    @property
    def current_file_name(self) -> str:
        """Get the current file name or 'Untitled'."""
        if self._current_file:
            return os.path.basename(self._current_file)
        return "Untitled"
    
    @property
    def is_modified(self) -> bool:
        """Check if the current document has been modified."""
        return self._is_modified
    
    def set_modified(self, modified: bool = True) -> None:
        """Set the modified state."""
        self._is_modified = modified
    
    def get_recent_files(self) -> List[Dict[str, str]]:
        """Get the list of recent files."""
        return self._recent_files_manager.get_recent_files()
    
    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        self._recent_files_manager.clear()
    
    @staticmethod
    def tasks_to_dict(tasks: List) -> List[Dict[str, Any]]:
        """Convert task list to serializable dictionaries."""
        from .model import Task
        result = []
        for task in tasks:
            if isinstance(task, Task):
                result.append({
                    "task": task.task,
                    "value": task.value,
                    "time": task.time,
                })
        return result
    
    @staticmethod
    def dict_to_tasks(task_dicts: List[Dict[str, Any]]) -> List:
        """Convert dictionaries back to Task objects."""
        from .model import Task
        tasks = []
        for td in task_dicts:
            task = Task(
                task=td.get("task", ""),
                value=float(td.get("value", 3.0)),
                time=float(td.get("time", 4.0))
            )
            tasks.append(task)
        return tasks
    
    def save(self, tasks: List, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Save tasks to a file.
        
        Args:
            tasks: List of Task objects to save
            file_path: Path to save to. If None, uses current file.
        
        Returns:
            Tuple of (success, message)
        """
        if file_path is None:
            file_path = self._current_file
        
        if file_path is None:
            return False, "No file path specified"
        
        # Ensure correct extension
        if not file_path.endswith(self.FILE_EXTENSION):
            file_path += self.FILE_EXTENSION
        
        try:
            now = datetime.utcnow().isoformat()
            
            # Create file data
            file_data = PriorityPlotFile(
                version="1.0",
                created_at=now if self._current_file != file_path else self._get_created_at(file_path) or now,
                modified_at=now,
                tasks=self.tasks_to_dict(tasks)
            )
            
            # Write to file
            tmp_path = f"{file_path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(asdict(file_data), f, indent=2)
            os.replace(tmp_path, file_path)
            
            # Update state
            self._current_file = file_path
            self._is_modified = False
            self._recent_files_manager.add_file(file_path)
            
            return True, f"Saved to {os.path.basename(file_path)}"
            
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    def _get_created_at(self, file_path: str) -> Optional[str]:
        """Get the created_at timestamp from an existing file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("created_at")
        except Exception:
            return None
    
    def load(self, file_path: str) -> Tuple[bool, str, List]:
        """
        Load tasks from a file.
        
        Args:
            file_path: Path to load from
        
        Returns:
            Tuple of (success, message, tasks)
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}", []
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Parse the file data
            task_dicts = data.get("tasks", [])
            tasks = self.dict_to_tasks(task_dicts)
            
            # Update state
            self._current_file = file_path
            self._is_modified = False
            self._recent_files_manager.add_file(file_path)
            
            return True, f"Loaded {os.path.basename(file_path)}", tasks
            
        except json.JSONDecodeError as e:
            return False, f"Invalid file format: {str(e)}", []
        except Exception as e:
            return False, f"Error loading file: {str(e)}", []
    
    def new_file(self) -> None:
        """Reset to a new untitled file."""
        self._current_file = None
        self._is_modified = False
    
    @staticmethod
    def get_default_save_directory() -> str:
        """Get the default directory for saving files."""
        save_locations = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~"),
            os.getcwd()
        ]
        
        for location in save_locations:
            if os.path.exists(location) and os.access(location, os.W_OK):
                return location
        
        return os.getcwd()
