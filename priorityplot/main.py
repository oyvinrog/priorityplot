import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase
from .plot_widget import PriorityPlotWidget

def main():
    app = QApplication(sys.argv)
    
    # Configure font fallback for emoji support
    try:
        emoji_font_id = QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
        if emoji_font_id != -1:
            emoji_families = QFontDatabase.applicationFontFamilies(emoji_font_id)
            if emoji_families:
                emoji_family = emoji_families[0]
                # Set up font substitution for emoji support
                QFont.insertSubstitution("DejaVu Sans", emoji_family)
    except Exception as e:
        # If emoji font setup fails, continue without it
        pass
    
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
            font-weight: bold;
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
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #3292ea;
        }
        QPushButton:pressed {
            background-color: #1a72ca;
        }
        QLineEdit {
            padding: 8px 12px;
            border: 1px solid #555555;
            border-radius: 4px;
            background-color: #454545;
            color: white;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 2px solid #2a82da;
            background-color: #505050;
        }
        QLabel {
            color: #ffffff;
        }
        QTableWidget {
            background-color: #353535;
            alternate-background-color: #454545;
            color: white;
            gridline-color: #555555;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #555555;
        }
        QTableWidget::item:selected {
            background-color: #2a82da;
        }
        QHeaderView::section {
            background-color: #454545;
            color: white;
            padding: 8px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        QToolTip {
            background-color: #2a2a2a;
            color: white;
            border: 2px solid #555555;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            font-weight: normal;
        }
        QMessageBox {
            background-color: #353535;
            color: white;
        }
        QMessageBox QPushButton {
            min-width: 100px;
            padding: 6px 12px;
        }
    """)
    
    main_window = QMainWindow()
    widget = PriorityPlotWidget()
    main_window.setCentralWidget(widget)
    main_window.setWindowTitle('priplot')
    
    # Make window scalable and responsive to different screen sizes
    # Get screen geometry to set appropriate default size
    screen = app.primaryScreen().geometry()
    screen_width = screen.width()
    screen_height = screen.height()
    
    # Set window to 80% of screen size, but with reasonable min/max bounds
    default_width = min(max(1000, int(screen_width * 0.8)), 1600)
    default_height = min(max(700, int(screen_height * 0.8)), 1200)
    
    main_window.resize(default_width, default_height)
    
    # Set minimum size to ensure usability on smaller screens
    main_window.setMinimumSize(800, 600)
    
    # Center the window on screen
    main_window.move(
        (screen_width - default_width) // 2,
        (screen_height - default_height) // 2
    )
    
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 