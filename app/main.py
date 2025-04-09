import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
    QSlider,
    QLabel,
    QComboBox
)
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt

from app.SagStyle import SagStyle


class SaggingTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.weight = 1.0  # Default weight parameter controlling "heaviness" of each line
        self.sag_style = SagStyle.HANGING_END
        
        # Set a bottom margin to reduce clipping of sagging text
        self.setViewportMargins(0, 0, 0, 100)
        
        # Dictionary to cache precalculated hanging offsets per block
        self.hanging_offsets = {}
        
        # Recalculate offsets whenever the text changes
        self.textChanged.connect(self.updateHangingOffsets)

    def updateHangingOffsets(self):
        """Precalculate hanging style offsets for each text block."""
        fm = self.fontMetrics()
        self.hanging_offsets.clear()
        block = self.document().firstBlock()
        while block.isValid():
            block_text = block.text()
            offsets = []
            line_width = fm.horizontalAdvance(block_text)
            center = line_width / 2.0
            sag_factor = self.weight / 300.0
            max_offset = sag_factor * (center ** 2)
            cum_width = 0
            for i, ch in enumerate(block_text):
                char_width = fm.horizontalAdvance(ch)
                if i == 0 or i == len(block_text) - 1:
                    offsets.append(0)
                else:
                    # Compute the center x position of the character relative to the start of the line
                    relative_center = cum_width + (char_width / 2.0)
                    # Quadratic sag: grows with the square of the relative position
                    offset = ((relative_center / line_width) ** 2) * max_offset
                    offsets.append(offset)
                cum_width += char_width
            self.hanging_offsets[block.blockNumber()] = offsets
            block = block.next()

    def paintEvent(self, event):
        # Custom paint event to draw text along a curved baseline
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipping(False)
        painter.setFont(self.font())
        
        # Fill the background using the widget's base color
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
            
            x = block_rect.x()
            
            # For hanging style, use precomputed offsets if available
            if self.sag_style == SagStyle.HANGING_END:
                offsets = self.hanging_offsets.get(block.blockNumber())
                # If offsets are not available or outdated, compute them on the fly
                if offsets is None or len(offsets) != len(block_text):
                    offsets = []
                    line_width = fm.horizontalAdvance(block_text)
                    center = line_width / 2.0
                    sag_factor = self.weight / 300.0
                    max_offset = sag_factor * (center ** 2)
                    cum_width = 0
                    for i, ch in enumerate(block_text):
                        char_width = fm.horizontalAdvance(ch)
                        if i == 0 or i == len(block_text) - 1:
                            offsets.append(0)
                        else:
                            relative_center = cum_width + (char_width / 2.0)
                            offset = ((relative_center / line_width) ** 2) * max_offset
                            offsets.append(offset)
                        cum_width += char_width
                
                for i, ch in enumerate(block_text):
                    char_width = fm.horizontalAdvance(ch)
                    # Use precalculated offset
                    offset = offsets[i] if i < len(offsets) else 0
                    painter.drawText(x, baseline + offset, ch)
                    x += char_width
            else:
                # (For completeness, if other sag styles were to be added, they can be handled here.)
                for i, ch in enumerate(block_text):
                    char_width = fm.horizontalAdvance(ch)
                    # Default behavior: no sag
                    painter.drawText(x, baseline, ch)
                    x += char_width
            
            block = block.next()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sagger Code Editor")

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

        # Create a combo box to select the sag style
        self.sag_combo = QComboBox()
        self.sag_combo.addItem(SagStyle.HANGING_END.value)
        self.sag_combo.addItem(SagStyle.DROOPING_CENTER.value)
        self.sag_combo.setCurrentIndex(0)  # Default to "Full Curve"
        self.sag_combo.currentIndexChanged.connect(self.updateSagStyle)

        # Lay out the editor, slider, and sag style selector in the main window.
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.editor)
        layout.addWidget(self.slider_label)
        layout.addWidget(self.slider)
        layout.addWidget(QLabel("Sag Style:"))
        layout.addWidget(self.sag_combo)
        self.setCentralWidget(central_widget)

    def updateWeight(self, value):
        # Update the weight value in our text editor and refresh the view.
        self.editor.weight = float(value)
        self.slider_label.setText(f"Weight: {value}")
        self.editor.viewport().update()

    def updateSagStyle(self, index):
        if index == 0:
            self.editor.sag_style = SagStyle.HANGING_END
        else:
            self.editor.sag_style = SagStyle.DROOPING_CENTER
        self.editor.viewport().update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
