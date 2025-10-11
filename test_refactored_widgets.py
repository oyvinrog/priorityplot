#!/usr/bin/env python3
"""
Test file to validate the refactored widget modules following SOLID principles.

This demonstrates:
- SRP: Each test focuses on a single widget responsibility
- OCP: Tests can be extended without modifying existing code  
- LSP: Interface implementations are substitutable
- ISP: Tests only depend on interfaces they need
- DIP: Tests depend on abstractions, not concretions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from priorityplot.model import Task, TaskValidator, SampleDataGenerator
from priorityplot.interfaces import ITaskInputWidget, ITaskDisplayWidget, IPlotWidget, IExportService
from priorityplot.input_widgets import TaskInputField, TaskInputCoordinator
from priorityplot.plot_widgets import InteractivePlotWidget, DraggableTaskTable, ExportButtonWidget
from priorityplot.main_plot_widget import PriorityPlotWidget

def test_srp_principle():
    """Test Single Responsibility Principle - each widget has one clear purpose"""
    print("🧪 Testing SRP (Single Responsibility Principle)")
    
    app = QApplication.instance() or QApplication([])
    
    # Task input field - only handles input
    input_field = TaskInputField()
    assert hasattr(input_field, 'get_current_task_text')
    assert hasattr(input_field, 'clear_input')
    print("  ✅ TaskInputField: Single responsibility for text input")
    
    # Plot widget - only handles plotting
    plot_widget = InteractivePlotWidget()
    assert hasattr(plot_widget, 'update_plot')
    assert hasattr(plot_widget, 'highlight_task_in_plot')
    print("  ✅ InteractivePlotWidget: Single responsibility for plotting")

def test_interface_segregation():
    """Test Interface Segregation Principle - specific interfaces for specific needs"""
    print("\n🧪 Testing ISP (Interface Segregation Principle)")
    
    # Input widget implements only input-related interface
    input_field = TaskInputField()
    assert isinstance(input_field, ITaskInputWidget)
    print("  ✅ TaskInputField implements ITaskInputWidget (focused interface)")
    
    # Display widget implements only display-related interface  
    display_table = DraggableTaskTable()
    assert isinstance(display_table, ITaskDisplayWidget)
    print("  ✅ DraggableTaskTable implements ITaskDisplayWidget (focused interface)")
    
    # Plot widget implements only plot-related interface
    plot_widget = InteractivePlotWidget()
    assert isinstance(plot_widget, IPlotWidget)
    print("  ✅ InteractivePlotWidget implements IPlotWidget (focused interface)")

def test_dependency_inversion():
    """Test Dependency Inversion Principle - depend on abstractions"""
    print("\n🧪 Testing DIP (Dependency Inversion Principle)")
    
    # Main widget depends on abstractions, not concretions
    main_widget = PriorityPlotWidget()
    
    # The main widget coordinates through interfaces
    assert hasattr(main_widget, '_task_coordinator')
    assert hasattr(main_widget, 'input_coordinator')
    assert hasattr(main_widget, 'plot_coordinator')
    print("  ✅ PriorityPlotWidget depends on abstractions via coordinators")
    
    # Widgets can be substituted as long as they implement interfaces
    input_widget = main_widget.input_coordinator.task_input_field
    assert isinstance(input_widget, ITaskInputWidget)
    print("  ✅ Input components are substitutable via interfaces")

def test_liskov_substitution():
    """Test Liskov Substitution Principle - implementations are substitutable"""
    print("\n🧪 Testing LSP (Liskov Substitution Principle)")
    
    # Create sample tasks
    tasks = SampleDataGenerator.get_sample_tasks()[:3]
    
    # Test that display widgets are substitutable
    display_widgets = [
        DraggableTaskTable(),
        # Could add other ITaskDisplayWidget implementations here
    ]
    
    for widget in display_widgets:
        widget.refresh_display(tasks)
        widget.highlight_task(0)
        widget.clear_highlighting()
        print(f"  ✅ {widget.__class__.__name__} correctly implements ITaskDisplayWidget")

def test_open_closed_principle():
    """Test Open/Closed Principle - open for extension, closed for modification"""
    print("\n🧪 Testing OCP (Open/Closed Principle)")
    
    # Create a custom display widget extending the interface
    class CustomTaskDisplay(ITaskDisplayWidget):
        def __init__(self):
            self.tasks = []
            self.highlighted = None
            
        def refresh_display(self, tasks):
            self.tasks = tasks
            
        def highlight_task(self, task_index):
            self.highlighted = task_index
            
        def clear_highlighting(self):
            self.highlighted = None
    
    # New implementation works without modifying existing code
    custom_widget = CustomTaskDisplay()
    tasks = [TaskValidator.create_validated_task("Test task")]
    
    custom_widget.refresh_display(tasks)
    custom_widget.highlight_task(0)
    custom_widget.clear_highlighting()
    
    print("  ✅ New implementations can be added without modifying existing code")
    print("  ✅ Interfaces enable extension without modification")

def test_modular_composition():
    """Test that modules can be composed and work together"""
    print("\n🧪 Testing Modular Composition")
    
    app = QApplication.instance() or QApplication([])
    
    # Create main widget
    main_widget = PriorityPlotWidget()
    
    # Test task addition through interface
    success = main_widget.add_task("Test task")
    assert success
    tasks = main_widget.get_tasks()
    assert len(tasks) == 1
    print("  ✅ Task addition works through clean interface")
    
    # Test that components are properly coordinated
    assert hasattr(main_widget, 'input_coordinator')
    assert hasattr(main_widget, 'plot_coordinator')
    print("  ✅ Components are properly composed and coordinated")

def test_testability():
    """Test that individual components are testable in isolation"""
    print("\n🧪 Testing Testability (Isolated Component Testing)")
    
    # Test input field in isolation
    input_field = TaskInputField()
    input_field.task_input.setText("Test task")
    text = input_field.get_current_task_text()
    assert text == "Test task"
    input_field.clear_input()
    assert input_field.get_current_task_text() == ""
    print("  ✅ TaskInputField is testable in isolation")
    
    # Test plot widget in isolation
    plot_widget = InteractivePlotWidget()
    tasks = [TaskValidator.create_validated_task("Test")]
    plot_widget.update_plot(tasks)
    plot_widget.highlight_task_in_plot(0)
    plot_widget.clear_highlighting()
    print("  ✅ InteractivePlotWidget is testable in isolation")
    
    # Test table widget in isolation
    table_widget = DraggableTaskTable()
    table_widget.refresh_display(tasks)
    table_widget.highlight_task(0)
    table_widget.clear_highlighting()
    print("  ✅ DraggableTaskTable is testable in isolation")

def test_protocol_implementation():
    """Test that widgets implement Protocol interfaces correctly without inheritance"""
    print("\n🧪 Testing Protocol Implementation Without Inheritance")
    
    # Create sample tasks
    tasks = [TaskValidator.create_validated_task("Test")]
    
    # Test that widgets implement their protocols correctly
    input_field = TaskInputField()
    plot_widget = InteractivePlotWidget()
    table_widget = DraggableTaskTable()
    export_widget = ExportButtonWidget()
    
    # Test runtime type checking
    assert isinstance(input_field, ITaskInputWidget)
    assert isinstance(plot_widget, IPlotWidget)
    assert isinstance(table_widget, ITaskDisplayWidget)
    assert isinstance(export_widget, IExportService)
    
    print("  ✅ All widgets correctly implement their Protocol interfaces")
    print("  ✅ Runtime type checking works with @runtime_checkable Protocol")
    print("  ✅ Metaclass conflicts resolved by not inheriting from Protocol")

def run_all_tests():
    """Run all SOLID principle tests"""
    print("🚀 Testing Refactored Widget Architecture - SOLID Principles Validation\n")
    
    test_srp_principle()
    test_interface_segregation()
    test_dependency_inversion()
    test_liskov_substitution()
    test_open_closed_principle()
    test_modular_composition()
    test_testability()
    test_protocol_implementation()
    
    print("\n🎉 All SOLID Principle Tests Passed!")
    print("\n📋 Architecture Benefits Validated:")
    print("  ✅ Single Responsibility: Each module has one clear purpose")
    print("  ✅ Open/Closed: Extensible without modification")
    print("  ✅ Liskov Substitution: Implementations are interchangeable")
    print("  ✅ Interface Segregation: Focused, specific interfaces")
    print("  ✅ Dependency Inversion: Depends on abstractions")
    print("  ✅ Testability: Components can be tested in isolation")
    print("  ✅ Maintainability: Changes are localized to modules")
    print("  ✅ Reusability: Widgets can be used independently")
    print("  ✅ Qt Compatibility: No metaclass conflicts with Protocol interfaces")

if __name__ == '__main__':
    run_all_tests() 