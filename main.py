import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
    QSlider,
    QLabel,
)
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt


class SaggingTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.weight = (
            1.0  # Default weight parameter controlling "heaviness" of each line
        )

    def paintEvent(self, event):
        # First, call the default painting behavior to draw text, cursor, etc.
        super().paintEvent(event)

        # Set up a painter to add our custom "sag" drawing on top of the text
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)

        # Iterate over each text block (i.e., line)
        block = self.document().firstBlock()
        while block.isValid():
            block_text = block.text()
            # Calculate the sag offset; here we use the number of characters and weight
            # For demonstration: the offset increases as the text gets longer,
            # then is wrapped with modulo so the offset stays within a visible range.
            sag_offset = (len(block_text) * self.weight) % 10

            # Determine the position of the block relative to the viewport
            block_rect = self.blockBoundingGeometry(block).translated(
                self.contentOffset()
            )

            # If there's text, draw a red line below the block that "sags"
            if block_text:
                start_x = block_rect.x()
                end_x = block_rect.x() + block_rect.width()
                # The sag is added to the y-coordinate of the block's bottom
                mid_y = block_rect.y() + block_rect.height() + sag_offset
                painter.setPen(Qt.red)
                painter.drawLine(start_x, mid_y, end_x, mid_y)
            block = block.next()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Saggy Code Editor")

        # Create our custom text editor widget
        self.editor = SaggingTextEdit()
        self.editor.setPlainText("def my_function():\n    print('Hello World')\n")

        # Create a slider to adjust the "weight" parameter interactively.
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(20)
        self.slider.setValue(10)
        self.slider.valueChanged.connect(self.updateWeight)
        self.slider_label = QLabel("Weight: 10")

        # Lay out the editor and slider in the main window.
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.editor)
        layout.addWidget(self.slider_label)
        layout.addWidget(self.slider)
        self.setCentralWidget(central_widget)

    def updateWeight(self, value):
        # Update the weight value in our text editor and refresh the view.
        self.editor.weight = float(value)
        self.slider_label.setText(f"Weight: {value}")
        self.editor.viewport().update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
