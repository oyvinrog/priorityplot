import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPalette, QColor
from .plot_widget import PriorityPlotWidget

def main():
    app = QApplication(sys.argv)
    
    # Set modern color scheme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Set modern stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #353535;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #353535;
        }
        QTabBar::tab {
            background-color: #454545;
            color: #ffffff;
            padding: 8px 20px;
            border: 1px solid #555555;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #2a82da;
        }
        QTabBar::tab:hover:!selected {
            background-color: #505050;
        }
        QPushButton {
            background-color: #2a82da;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #3292ea;
        }
        QPushButton:pressed {
            background-color: #1a72ca;
        }
        QLineEdit {
            padding: 6px;
            border: 1px solid #555555;
            border-radius: 4px;
            background-color: #454545;
            color: white;
        }
        QTableWidget {
            background-color: #353535;
            alternate-background-color: #454545;
            color: white;
            gridline-color: #555555;
            border: 1px solid #555555;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #2a82da;
        }
        QHeaderView::section {
            background-color: #454545;
            color: white;
            padding: 5px;
            border: 1px solid #555555;
        }
    """)
    
    main_window = QMainWindow()
    widget = PriorityPlotWidget()
    main_window.setCentralWidget(widget)
    main_window.setWindowTitle('priplot')
    main_window.resize(900, 600)  # Slightly larger window for better visibility
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 