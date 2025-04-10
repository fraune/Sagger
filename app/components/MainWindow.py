from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSlider,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import Qt, QEvent
from app.enum.SagStyle import SagStyle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sagger Code Editor")

        # Set default sag style
        self.currentSagStyle = SagStyle.NO_SAG
        # Create our custom text editor widget based on the sag style using the enum's factory method
        self.editor = self.currentSagStyle.create_editor()
        self.editor.setPlainText("def my_function():\n    print('Hello World')\n")
        self.editor.viewport().installEventFilter(self)

        # Create a slider to adjust the "weight" parameter interactively.
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(20)
        self.slider.setValue(10)
        self.slider.valueChanged.connect(self.updateWeight)
        self.slider_label = QLabel(f"Weight: {self.slider.value()/10:.1f}")

        # Create a combo box to select the sag style by iterating over all items in the SagStyle enum
        self.sag_combo = QComboBox()
        for style in SagStyle:
            self.sag_combo.addItem(style.value, style)
        # Set default combo index corresponding to currentSagStyle
        default_index = list(SagStyle).index(self.currentSagStyle)
        self.sag_combo.setCurrentIndex(default_index)
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

    def updateWeight(self, value):
        # Update the weight value in our text editor and refresh the view.
        weight_value = value / 10.0
        self.editor.weight = weight_value
        self.slider_label.setText(f"Weight: {weight_value:.1f}")
        self.editor.updateOffsets()
        self.editor.viewport().update()

    def updateSagStyle(self, index):
        # Use the actual enum value selected from the combo box
        new_style = self.sag_combo.itemData(index)
        if new_style != self.currentSagStyle:
            # Preserve current text and weight before recreating the editor.
            current_text = self.editor.toPlainText()
            current_weight = self.editor.weight
            # Remove the current editor widget.
            self.layout.removeWidget(self.editor)
            self.editor.deleteLater()
            # Create a new editor widget using the enum's factory method.
            self.editor = new_style.create_editor()
            self.editor.setPlainText(current_text)
            self.editor.weight = current_weight
            # Insert the new editor at the top of the layout.
            self.layout.insertWidget(0, self.editor)
            self.currentSagStyle = new_style

    def updateStatusBar(self):
        editor_rect = self.editor.viewport().rect()
        self.statusBar().showMessage(
            f"Window Size: {self.width()} x {self.height()} | Editor Size: {editor_rect.width()} x {editor_rect.height()}"
        )

    def resizeEvent(self, event):
        self.updateStatusBar()
        super().resizeEvent(event)

    def eventFilter(self, source, event):
        if source == self.editor.viewport() and event.type() == QEvent.Resize:
            self.updateStatusBar()
        return super().eventFilter(source, event)
