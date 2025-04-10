from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont


class CodeEditorBase(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.Monospace)
        self.setFont(monospace_font)
        # Default weight parameter controlling "heaviness" of each line
        self.weight = 1.0
