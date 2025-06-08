#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced drag and drop visual feedback.

This script showcases the new visual feedback features:
1. Visual drag pixmap showing the task being dragged
2. Row highlighting when preparing to drag
3. Cursor changes to indicate drag state
4. Pulsing calendar date highlighting during drag
5. Clear instruction text for better UX
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from priorityplot import PriorityPlotWidget
from priorityplot.model import Task

def main():
    app = QApplication(sys.argv)
    
    # Create test tasks with variety for demonstration
    test_tasks = [
        Task("Team Standup Meeting", 4.2, 0.5),
        Task("Code Review - Feature Branch", 3.8, 1.2), 
        Task("Write API Documentation", 3.0, 2.5),
        Task("Bug Fix - Critical Issue", 4.8, 1.0),
        Task("Planning Session Q2", 3.5, 2.0),
        Task("Database Migration", 4.0, 3.0),
        Task("User Testing Session", 3.2, 1.5),
    ]
    
    # Create the widget with test tasks
    widget = PriorityPlotWidget(test_tasks)
    widget.show()
    
    print("🎯 Enhanced Drag & Drop Visual Feedback Demo")
    print("=" * 50)
    print()
    print("✨ NEW FEATURES TO TEST:")
    print("1. 📱 Hover over tasks in the table - see cursor change")
    print("2. 🎯 Click and hold on any task - row highlights in blue") 
    print("3. 🖱️  Start dragging - see visual drag preview with task info")
    print("4. 📅 Drag over calendar - dates pulse with red highlighting")
    print("5. 💫 Drop on any date - time selection dialog appears")
    print()
    print("🎨 VISUAL ENHANCEMENTS:")
    print("• Custom drag pixmap shows task name and rank")
    print("• Table rows highlight when clicked")
    print("• Calendar dates pulse during drag operations")
    print("• Improved cursor feedback (hand/pointer icons)")
    print("• Clear instruction text with golden border")
    print()
    print("🚀 Try dragging different tasks to see the visual feedback!")
    print("The drag preview will show the task name and priority rank.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 