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
    
    # Set modern color scheme - Professional design system
    app.setStyle("Fusion")
    palette = QPalette()
    # Rich dark background with subtle depth
    palette.setColor(QPalette.ColorRole.Window, QColor(24, 26, 31))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.Base, QColor(17, 19, 23))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(31, 34, 40))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(17, 19, 23))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.Text, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.Button, QColor(31, 34, 40))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(229, 231, 235))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(248, 113, 113))
    palette.setColor(QPalette.ColorRole.Link, QColor(96, 165, 250))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(79, 70, 229))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Set modern stylesheet - Professional design system
    app.setStyleSheet("""
        /* Modern design system with refined aesthetics */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #181A1F, stop:1 #0F1117);
        }
        
        QTabWidget::pane {
            border: 1px solid #2D3139;
            background-color: #181A1F;
            border-radius: 8px;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1F2228, stop:1 #181A1F);
            color: #9CA3AF;
            padding: 10px 24px;
            border: 1px solid #2D3139;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4F46E5, stop:1 #4338CA);
            color: #FFFFFF;
            border-bottom: 2px solid #6366F1;
        }
        
        QTabBar::tab:hover:!selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #252830, stop:1 #1F2228);
            color: #E5E7EB;
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6366F1, stop:1 #4F46E5);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            min-width: 90px;
            font-weight: 600;
            font-size: 13px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #818CF8, stop:1 #6366F1);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4338CA, stop:1 #3730A3);
            padding: 11px 20px 9px 20px;
        }
        
        QLineEdit {
            padding: 11px 14px;
            border: 2px solid #2D3139;
            border-radius: 8px;
            background-color: #1F2228;
            color: #E5E7EB;
            font-size: 13px;
            selection-background-color: #4F46E5;
        }
        
        QLineEdit:focus {
            border: 2px solid #6366F1;
            background-color: #252830;
        }
        
        QLabel {
            color: #E5E7EB;
        }
        
        QTableWidget {
            background-color: #181A1F;
            alternate-background-color: #1F2228;
            color: #E5E7EB;
            gridline-color: #2D3139;
            border: 2px solid #2D3139;
            border-radius: 8px;
        }
        
        QTableWidget::item {
            padding: 10px;
            border-bottom: 1px solid #2D3139;
        }
        
        QTableWidget::item:selected {
            background-color: #4F46E5;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #252830, stop:1 #1F2228);
            color: #F3F4F6;
            padding: 10px;
            border: 1px solid #2D3139;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        QToolTip {
            background-color: #111317;
            color: #E5E7EB;
            border: 2px solid #4F46E5;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 12px;
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
            background-color: #2D3139;
        }
        
        QSplitter::handle:hover {
            background-color: #4F46E5;
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