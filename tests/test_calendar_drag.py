#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced calendar drag and drop functionality.

This script shows how the new features work:
1. Click on any date in the calendar to select it
2. Drag tasks from the priority ranking table to the calendar
3. A time selection dialog appears with smart defaults
4. Tasks are scheduled with your chosen times
5. Green indicators show scheduled tasks
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from priorityplot import PriorityPlotWidget
from priorityplot.model import Task

def main():
    app = QApplication(sys.argv)
    
    # Create some test tasks
    test_tasks = [
        Task("Morning standup", 4.0, 0.5),
        Task("Code review", 3.5, 1.5), 
        Task("Write documentation", 3.0, 2.0),
        Task("Team meeting", 2.5, 1.0),
        Task("Bug fixes", 4.5, 3.0),
    ]
    
    # Create the widget with test tasks
    widget = PriorityPlotWidget(test_tasks)
    widget.show()
    
    print("🎯 Calendar Drag & Drop Demo")
    print("=" * 40)
    print("1. Click 'Try Sample Tasks' or use the provided test tasks")
    print("2. Click on any date in the calendar to select it")
    print("3. Drag any task from the priority table to the calendar")
    print("4. Choose your preferred start and end times")
    print("5. See tasks scheduled with smart time defaults!")
    print("6. Green dots = scheduled tasks")
    print("7. Export to Excel to see the full schedule")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 