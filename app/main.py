import sys
from PySide6.QtWidgets import QApplication
import signal
from app.MainWindow import MainWindow


if __name__ == "__main__":
    # Accept SIGINT to exit app (helpful for quick edits when debugging)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Launch the app
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
