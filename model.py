import math
from typing import List, Dict

class Task:
    def __init__(self, task: str, value: float, time: float):
        self.task = task
        self.value = value
        self.time = time
        self.score = 0.0

    def calculate_score(self):
        self.score = self.value / math.log(max(2.718, self.time))
        return self.score

def calculate_and_sort_tasks(tasks: List[Task]) -> List[Task]:
    for t in tasks:
        t.calculate_score()
    return sorted(tasks, key=lambda t: t.score, reverse=True) 