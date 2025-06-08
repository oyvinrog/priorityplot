#!/usr/bin/env python3
"""
Test script to demonstrate day-specific calendar drag and drop.

Shows how you can now drag tasks directly to specific days (like "20") 
and the system will automatically propose that date for scheduling.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from priorityplot.plot_widget import PriorityPlotWidget
from priorityplot.model import Task

def main():
    app = QApplication(sys.argv)
    
    # Create test tasks with different priorities
    test_tasks = [
        Task("Team Meeting", 3.5, 1.0),
        Task("Code Review", 4.0, 2.0),
        Task("Documentation", 2.5, 3.0),
        Task("Bug Fixes", 4.5, 1.5),
        Task("Planning Session", 3.0, 2.5),
    ]
    
    # Create the widget
    widget = PriorityPlotWidget(test_tasks)
    widget.show()
    
    print("🎯 Day-Specific Drag & Drop Test")
    print("=" * 40)
    print("✨ NEW FEATURE: Direct day targeting!")
    print()
    print("📋 Test Instructions:")
    print("1. The app will load with 5 test tasks")
    print("2. Look at the calendar on the right")
    print("3. Drag any task from the priority table")
    print("4. Drop it directly on day '20' (or any other day)")
    print("5. The time dialog will show the 20th as the selected date!")
    print()
    print("🚀 What's New:")
    print("• No need to click dates first")
    print("• Drop directly on the day number you want")
    print("• System detects which day you dropped on")
    print("• Time dialog shows the correct date automatically")
    print()
    print("Try dragging to different days like 15, 20, 25, etc!")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 