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
        # Custom paint event to draw text along a curved baseline
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self.font())
        
        # Optionally fill the background using the widget's base color
        painter.fillRect(self.viewport().rect(), self.palette().base())
        
        fm = painter.fontMetrics()
        
        # Iterate over each text block (each line)
        block = self.document().firstBlock()
        while block.isValid():
            block_text = block.text()
            # Get the block geometry relative to the viewport
            block_rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
            
            # Define the baseline: top of block plus the ascent of the font
            baseline = block_rect.y() + fm.ascent()
            
            # Calculate the total width of the text line and its horizontal center
            line_width = fm.horizontalAdvance(block_text)
            center = line_width / 2.0
            
            # Define sag factor based on the weight; adjust the divisor to control sag intensity
            sag_factor = self.weight / 300.0
            # Compute maximum sag offset at the center of the line
            max_offset = sag_factor * (center ** 2)
            
            x = block_rect.x()
            for ch in block_text:
                char_width = fm.horizontalAdvance(ch)
                # Compute the center x position for the character relative to the start of the line
                char_center = (x - block_rect.x()) + (char_width / 2.0)
                
                # Calculate the offset so that the ends have no sag and the center has maximum sag
                offset = max_offset - sag_factor * ((char_center - center) ** 2)
                
                # Draw the character at position (x, baseline + offset)
                painter.drawText(x, baseline + offset, ch)
                x += char_width
            
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
