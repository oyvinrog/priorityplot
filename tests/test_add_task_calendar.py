#!/usr/bin/env python3
"""
Test script to demonstrate the new "Add Task" button in the calendar view.

This script shows how the new feature works:
1. Click on any date in the calendar to select it
2. Click the green "➕ Add Task" button in the calendar panel
3. Fill out the task creation dialog with name, value, time, and schedule
4. The task is automatically created and scheduled on the selected date
5. Tasks appear in both the priority chart and calendar (bold dates)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from priorityplot.plot_widget import PriorityPlotWidget

def main():
    app = QApplication(sys.argv)
    
    # Create the widget without any initial tasks
    widget = PriorityPlotWidget()
    widget.show()
    
    print("📅 Add Task from Calendar Demo")
    print("=" * 40)
    print("✨ NEW FEATURE: Create tasks directly from the calendar!")
    print()
    print("🎯 How to Test:")
    print("1. Look at the calendar panel on the right side")
    print("2. Click on any date to select it")
    print("3. Click the green '➕ Add Task' button below the scheduled tasks")
    print("4. Fill out the dialog:")
    print("   • Task Name: Enter a descriptive name")
    print("   • Value: 1.0-5.0 (importance/impact)")
    print("   • Time: 0.5-8.0 (hours needed)")
    print("   • Start/End Times: When you want to do it")
    print("5. Click OK to create and schedule the task")
    print()
    print("🎉 Results:")
    print("• Task appears in the priority chart")
    print("• Task is automatically scheduled on selected date")
    print("• Calendar date becomes bold (shows scheduled tasks)")
    print("• Task appears in priority ranking table")
    print("• Export to Excel includes both priorities and schedule")
    print()
    print("💡 Tips:")
    print("• Try creating multiple tasks on different dates")
    print("• Use 'Try Sample Tasks' first to see the full interface")
    print("• Green dots on chart = scheduled tasks")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 