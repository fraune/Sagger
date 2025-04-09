import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSlider,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Qt

from app.SagStyle import SagStyle
from app.EditorStyles import (
    HangingEndCodeEditor,
    DroopingCenterCodeEditor,
    PlainCodeEditor,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sagger Code Editor")

        # Set default sag style
        self.currentSagStyle = SagStyle.NO_SAG
        # Create our custom text editor widget based on the sag style
        self.editor = self.createEditor(self.currentSagStyle)
        self.editor.setPlainText("def my_function():\n    print('Hello World')\n")

        # Create a slider to adjust the "weight" parameter interactively.
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(20)
        self.slider.setValue(10)
        self.slider.valueChanged.connect(self.updateWeight)
        self.slider_label = QLabel(f"Weight: {self.slider.value()}")

        # Create a combo box to select the sag style
        self.sag_combo = QComboBox()
        self.sag_combo.addItem(SagStyle.NO_SAG.value)
        self.sag_combo.addItem(SagStyle.HANGING_END.value)
        self.sag_combo.addItem(SagStyle.DROOPING_CENTER.value)
        # Set default combo index corresponding to currentSagStyle
        self.sag_combo.setCurrentIndex(0)
        self.sag_combo.currentIndexChanged.connect(self.updateSagStyle)

        # Lay out the editor, slider, and sag style selector in the main window.
        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)
        self.layout.addWidget(self.editor)
        self.layout.addWidget(self.slider_label)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(QLabel("Sag Style:"))
        self.layout.addWidget(self.sag_combo)
        self.setCentralWidget(central_widget)

    def createEditor(self, style):
        # Create a new editor instance based on the selected SagStyle.
        if style == SagStyle.HANGING_END:
            return HangingEndCodeEditor()
        elif style == SagStyle.DROOPING_CENTER:
            return DroopingCenterCodeEditor()
        elif style == SagStyle.NO_SAG:
            return PlainCodeEditor()
        else:
            return PlainCodeEditor()

    def updateWeight(self, value):
        # Update the weight value in our text editor and refresh the view.
        self.editor.weight = float(value)
        self.slider_label.setText(f"Weight: {value}")
        if hasattr(self.editor, 'updateHangingOffsets'):
            self.editor.updateHangingOffsets()
        self.editor.viewport().update()

    def updateSagStyle(self, index):
        # Determine the new sag style based on the combo box index.
        if index == 0:
            new_style = SagStyle.NO_SAG
        elif index == 1:
            new_style = SagStyle.HANGING_END
        else:
            new_style = SagStyle.DROOPING_CENTER

        if new_style != self.currentSagStyle:
            # Preserve current text and weight before recreating the editor.
            current_text = self.editor.toPlainText()
            current_weight = self.editor.weight
            # Remove the current editor widget.
            self.layout.removeWidget(self.editor)
            self.editor.deleteLater()
            # Create a new editor widget.
            self.editor = self.createEditor(new_style)
            self.editor.setPlainText(current_text)
            self.editor.weight = current_weight
            # Insert the new editor at the top of the layout.
            self.layout.insertWidget(0, self.editor)
            self.currentSagStyle = new_style


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
