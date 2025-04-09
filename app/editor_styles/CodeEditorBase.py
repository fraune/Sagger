from PySide6.QtWidgets import QPlainTextEdit


class CodeEditorBase(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Default weight parameter controlling "heaviness" of each line
        self.weight = 1.0
