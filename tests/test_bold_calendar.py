#!/usr/bin/env python3
"""
Demo script to showcase the bold calendar formatting feature.

Pre-schedules some tasks on different dates to immediately show
how days with scheduled tasks appear in bold on the calendar.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from priorityplot.plot_widget import PriorityPlotWidget
from priorityplot.model import Task
from datetime import datetime, timedelta

def main():
    app = QApplication(sys.argv)
    
    # Create test tasks
    tasks = [
        Task("Morning standup", 4.0, 0.5),
        Task("Code review", 4.5, 2.0),
        Task("Team meeting", 3.5, 1.5),
        Task("Documentation", 3.0, 3.0),
        Task("Bug fixes", 4.0, 2.5),
    ]
    
    # Pre-schedule some tasks on different dates to show bold formatting
    today = datetime.now()
    
    # Schedule task 1 for today
    tasks[0].schedule_on_calendar(today, "09:00 AM", "09:30 AM")
    
    # Schedule task 2 for tomorrow  
    tomorrow = today + timedelta(days=1)
    tasks[1].schedule_on_calendar(tomorrow, "10:00 AM", "12:00 PM")
    
    # Schedule task 3 for day after tomorrow
    day_after = today + timedelta(days=2)
    tasks[2].schedule_on_calendar(day_after, "02:00 PM", "03:30 PM")
    
    # Create the widget with pre-scheduled tasks
    widget = PriorityPlotWidget(tasks)
    widget.show()
    
    print("📅 Bold Calendar Formatting Demo")
    print("=" * 40)
    print("✨ FEATURE: Days with tasks appear in BOLD!")
    print()
    print("🎯 What to Notice:")
    print(f"• {today.strftime('%d')}: Morning standup (bold)")
    print(f"• {tomorrow.strftime('%d')}: Code review (bold)")  
    print(f"• {day_after.strftime('%d')}: Team meeting (bold)")
    print("• Other days: Normal formatting")
    print()
    print("📋 Try This:")
    print("1. Look at the calendar - notice the bold dates!")
    print("2. Click on the bold dates to see scheduled tasks")
    print("3. Drag more tasks to other dates")
    print("4. Watch new dates become bold instantly")
    print("5. Clear schedules and see bold formatting disappear")
    print()
    print("🔄 Navigation:")
    print("• Change months - bold formatting persists")
    print("• Bold dates show which days have work scheduled")
    print("• Perfect for quick visual planning!")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 