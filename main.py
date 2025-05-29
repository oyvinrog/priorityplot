import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from plot_widget import PriorityPlotWidget

def main():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    widget = PriorityPlotWidget()
    main_window.setCentralWidget(widget)
    main_window.setWindowTitle('Priority Plot')
    main_window.resize(700, 500)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 