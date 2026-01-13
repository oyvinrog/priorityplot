import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase, QAction, QKeySequence
from PyQt6.QtCore import Qt
from .plot_widget import PriorityPlotWidget
from .file_manager import FileManager


class PriorityPlotMainWindow(QMainWindow):
    """Main window with File menu for save/load functionality."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize file manager
        self.file_manager = FileManager()
        
        # Create the main widget
        self.widget = PriorityPlotWidget()
        self.setCentralWidget(self.widget)
        
        # Setup menu bar
        self._setup_menu_bar()
        
        # Update window title
        self._update_window_title()
        
        # Connect to task changes to track modifications
        self._connect_modification_signals()
    
    def _setup_menu_bar(self):
        """Create the menu bar with File menu."""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #0F1115;
                color: #E5E7EB;
                border-bottom: 1px solid #262B32;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #1B2027;
            }
            QMenu {
                background-color: #171B22;
                color: #E5E7EB;
                border: 1px solid #262B32;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1FAE9B;
            }
            QMenu::separator {
                height: 1px;
                background-color: #262B32;
                margin: 4px 8px;
            }
        """)
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New action
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create a new priority plot")
        new_action.triggered.connect(self._on_new)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open a priority plot file")
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = QMenu("Open &Recent", self)
        self._update_recent_files_menu()
        file_menu.addMenu(self.recent_menu)
        
        file_menu.addSeparator()
        
        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save the current priority plot")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.setStatusTip("Save the priority plot to a new file")
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def _update_recent_files_menu(self):
        """Update the recent files submenu."""
        self.recent_menu.clear()
        
        recent_files = self.file_manager.get_recent_files()
        
        if not recent_files:
            no_recent_action = QAction("No Recent Files", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
        else:
            for i, rf in enumerate(recent_files):
                file_path = rf.get("path", "")
                file_name = rf.get("name", "Unknown")
                action = QAction(f"&{i + 1}. {file_name}", self)
                action.setStatusTip(file_path)
                action.setData(file_path)
                action.triggered.connect(lambda checked, path=file_path: self._open_file(path))
                self.recent_menu.addAction(action)
            
            self.recent_menu.addSeparator()
            
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_menu.addAction(clear_action)
    
    def _update_window_title(self):
        """Update the window title based on current file state."""
        title = "Priority Plot  •  Task Prioritization Made Simple"
        file_name = self.file_manager.current_file_name
        
        if self.file_manager.is_modified:
            title = f"• {file_name} - {title}"
        elif self.file_manager.current_file:
            title = f"{file_name} - {title}"
        
        self.setWindowTitle(title)
    
    def _connect_modification_signals(self):
        """Connect signals to track when tasks are modified."""
        # Connect to the input coordinator's tasks_updated signal
        self.widget.input_coordinator.tasks_updated.connect(self._on_tasks_modified)
        # Connect to the plot coordinator's task_updated signal
        self.widget.plot_coordinator.task_updated.connect(self._on_tasks_modified)
        self.widget.plot_coordinator.task_added.connect(self._on_tasks_modified)
        self.widget.plot_coordinator.task_deleted.connect(self._on_tasks_modified)
        self.widget.plot_coordinator.task_renamed.connect(self._on_tasks_modified)
    
    def _on_tasks_modified(self, *args):
        """Handle task modifications."""
        self.file_manager.set_modified(True)
        self._update_window_title()
    
    def _on_new(self):
        """Create a new priority plot."""
        if not self._check_save_changes():
            return
        
        # Reset the widget with empty task list using the public API
        self.widget.set_tasks([])
        self.widget.results_panel.hide()
        self.widget.input_coordinator.show()
        
        self.file_manager.new_file()
        self._update_window_title()
    
    def _on_open(self):
        """Open a priority plot file."""
        if not self._check_save_changes():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Priority Plot",
            self.file_manager.get_default_save_directory(),
            self.file_manager.FILE_FILTER
        )
        
        if file_path:
            self._open_file(file_path)
    
    def _open_file(self, file_path: str):
        """Open a specific file."""
        if not self._check_save_changes():
            return
        
        success, message, tasks = self.file_manager.load(file_path)
        
        if success:
            # Update the widget with loaded tasks using the public API
            self.widget.set_tasks(tasks)
            
            # Show results if there are tasks
            if tasks:
                self.widget._show_results()
            else:
                self.widget.results_panel.hide()
                self.widget.input_coordinator.show()
            
            self._update_recent_files_menu()
            self._update_window_title()
        else:
            QMessageBox.warning(self, "Open Failed", message)
    
    def _on_save(self):
        """Save the current priority plot."""
        if self.file_manager.current_file:
            self._save_to_file(self.file_manager.current_file)
        else:
            self._on_save_as()
    
    def _on_save_as(self):
        """Save the priority plot to a new file."""
        default_name = self.file_manager.current_file_name
        if default_name == "Untitled":
            default_name = "my_priorities.priplot"
        elif not default_name.endswith(".priplot"):
            default_name += ".priplot"
        
        default_path = os.path.join(
            self.file_manager.get_default_save_directory(),
            default_name
        )
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Priority Plot",
            default_path,
            self.file_manager.FILE_FILTER
        )
        
        if file_path:
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str):
        """Save to a specific file."""
        tasks = self.widget.get_tasks()
        success, message = self.file_manager.save(tasks, file_path)
        
        if success:
            self._update_recent_files_menu()
            self._update_window_title()
        else:
            QMessageBox.warning(self, "Save Failed", message)
    
    def _clear_recent_files(self):
        """Clear the recent files list."""
        self.file_manager.clear_recent_files()
        self._update_recent_files_menu()
    
    def _check_save_changes(self) -> bool:
        """
        Check if there are unsaved changes and prompt to save.
        Returns True if the operation should continue, False if cancelled.
        """
        if not self.file_manager.is_modified:
            return True
        
        # Check if there are any tasks
        tasks = self.widget.get_tasks()
        if not tasks:
            return True
        
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Do you want to save your changes before continuing?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard | 
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            self._on_save()
            return not self.file_manager.is_modified  # True if save succeeded
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:  # Cancel
            return False
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self._check_save_changes():
            event.accept()
        else:
            event.ignore()


# Need os for file paths
import os

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
            background: #1B2027;
            color: #E5E7EB;
            border: 1px solid #2A2F36;
            padding: 6px 12px;
            border-radius: 6px;
            min-height: 30px;
            font-weight: 600;
            font-size: 12px;
        }
        
        QPushButton:hover {
            background: #212833;
            border-color: #3A4452;
        }
        
        QPushButton:pressed {
            background: #161B22;
        }
        
        QPushButton[variant="primary"] {
            background: #1FAE9B;
            color: #FFFFFF;
            border-color: #1FAE9B;
        }
        
        QPushButton[variant="primary"]:hover {
            background: #23C3AE;
            border-color: #23C3AE;
        }
        
        QPushButton[variant="primary"]:pressed {
            background: #189686;
            border-color: #189686;
        }
        
        QPushButton[variant="secondary"] {
            background: transparent;
            color: #C9D2DD;
            border-color: #2A2F36;
        }
        
        QPushButton[variant="secondary"]:hover {
            background: #1A2028;
            border-color: #3A4452;
            color: #E5E7EB;
        }
        
        QPushButton[variant="danger"] {
            background: transparent;
            color: #FCA5A5;
            border-color: #4B2328;
        }
        
        QPushButton[variant="danger"]:hover {
            background: #B91C1C;
            color: #FFFFFF;
            border-color: #B91C1C;
        }
        
        QPushButton[variant="danger"]:pressed {
            background: #991B1B;
            border-color: #991B1B;
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
            min-width: 90px;
            padding: 6px 12px;
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
    
    main_window = PriorityPlotMainWindow()
    
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
