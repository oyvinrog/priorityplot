import math
from typing import List, Dict, Optional
from datetime import datetime

class Task:
    def __init__(self, task: str, value: float, time: float):
        self.task = task
        self.value = value
        self.time = time
        self.score = 0.0
        # Calendar scheduling info
        self.scheduled_date: Optional[datetime] = None
        self.scheduled_start_time: Optional[str] = None
        self.scheduled_end_time: Optional[str] = None

    def calculate_score(self):
        self.score = self.value / math.log(max(2.718, self.time))
        return self.score
    
    def schedule_on_calendar(self, date: datetime, start_time: str = None, end_time: str = None):
        """Schedule this task on a specific date with optional time range"""
        self.scheduled_date = date
        self.scheduled_start_time = start_time
        self.scheduled_end_time = end_time
    
    def clear_schedule(self):
        """Remove task from calendar scheduling"""
        self.scheduled_date = None
        self.scheduled_start_time = None
        self.scheduled_end_time = None
    
    def is_scheduled(self) -> bool:
        """Check if task is scheduled on calendar"""
        return self.scheduled_date is not None

def calculate_and_sort_tasks(tasks: List[Task]) -> List[Task]:
    for t in tasks:
        t.calculate_score()
    return sorted(tasks, key=lambda t: t.score, reverse=True) 