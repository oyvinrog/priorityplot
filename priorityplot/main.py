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
    
    # Set simple, modern color scheme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 17, 21))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.Base, QColor(20, 24, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(26, 31, 38))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(20, 24, 30))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.Text, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.Button, QColor(34, 39, 46))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(248, 113, 113))
    palette.setColor(QPalette.ColorRole.Link, QColor(34, 197, 181))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(34, 197, 181))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Set simplified stylesheet for a cleaner UI
    app.setStyleSheet("""
        QMainWindow {
            background-color: #0F1115;
        }
        
        QTabWidget::pane {
            border: 1px solid #262B32;
            background-color: #0F1115;
            border-radius: 6px;
        }
        
        QTabBar::tab {
            background: #171B22;
            color: #B5BDC9;
            padding: 7px 16px;
            border: 1px solid #262B32;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-weight: 600;
            font-size: 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #1D232B;
            color: #FFFFFF;
        }
        
        QTabBar::tab:hover:!selected {
            background: #1B2027;
            color: #DCE1E8;
        }
        
        QPushButton {
            background: #1FAE9B;
            color: #FFFFFF;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            min-width: 84px;
            font-weight: 600;
            font-size: 12px;
        }
        
        QPushButton:hover {
            background: #23C3AE;
        }
        
        QPushButton:pressed {
            background: #189686;
        }
        
        QLineEdit {
            padding: 8px 10px;
            border: 1px solid #2A2F36;
            border-radius: 6px;
            background-color: #171B22;
            color: #E5E7EB;
            font-size: 12px;
            selection-background-color: #23C3AE;
        }
        
        QLineEdit:focus {
            border: 1px solid #23C3AE;
            background-color: #1B2027;
        }
        
        QLabel {
            color: #E5E7EB;
        }
        
        QTableWidget {
            background-color: #12161C;
            alternate-background-color: #171B22;
            color: #E5E7EB;
            gridline-color: #2A2F36;
            border: 1px solid #2A2F36;
            border-radius: 6px;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2A2F36;
        }
        
        QTableWidget::item:selected {
            background-color: #1FAE9B;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background: #171B22;
            color: #CCD3DD;
            padding: 7px;
            border: 1px solid #2A2F36;
            font-weight: 600;
            font-size: 11px;
        }
        
        QToolTip {
            background-color: #171B22;
            color: #E5E7EB;
            border: 1px solid #2A2F36;
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 11px;
        }
        
        QMessageBox {
            background-color: #181A1F;
            color: #E5E7EB;
        }
        
        QMessageBox QPushButton {
            min-width: 110px;
            padding: 8px 16px;
        }
        
        QSplitter::handle {
            background-color: #262B32;
        }
        
        QSplitter::handle:hover {
            background-color: #23C3AE;
        }

        QScrollBar:vertical {
            background: #101318;
            width: 10px;
            margin: 2px;
        }

        QScrollBar::handle:vertical {
            background: #2A313A;
            border-radius: 5px;
            min-height: 24px;
        }

        QScrollBar::handle:vertical:hover {
            background: #37404A;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    
    main_window = QMainWindow()
    widget = PriorityPlotWidget()
    main_window.setCentralWidget(widget)
    main_window.setWindowTitle('Priority Plot  •  Task Prioritization Made Simple')
    
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
