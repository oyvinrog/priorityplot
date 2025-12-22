# Backward compatibility module - delegates to new modular architecture
# This maintains the original API while using the new SOLID-compliant structure

from .main_plot_widget import PriorityPlotWidget
from .plot_widgets import DraggableTaskTable as DraggableTableWidget

# Re-export the main widget for backward compatibility
__all__ = [
    'PriorityPlotWidget',
    'DraggableTableWidget'
]

# The original large PriorityPlotWidget class has been refactored into:
#
# 1. interfaces.py - Abstract interfaces following ISP and DIP
# 2. input_widgets.py - Task input functionality (SRP)  
# 3. plot_widgets.py - Plot and visualization (SRP)
# 4. main_plot_widget.py - Main coordinator (SRP, DIP)
#
# SOLID Principles Applied:
# - SRP: Each module has a single, well-defined responsibility
# - OCP: Extensible through interfaces without modifying existing code
# - LSP: Consistent interfaces allow substitution
# - ISP: Specific interfaces avoid unnecessary dependencies  
# - DIP: High-level modules depend on abstractions, not concretions
#
# Benefits:
# - Easier testing (each module can be tested independently)
# - Better maintainability (changes are localized)
# - Improved reusability (widgets can be used independently)
# - Cleaner architecture (separation of concerns)
# - Type safety (interfaces define clear contracts)
