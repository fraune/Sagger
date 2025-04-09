from app.editor_styles.CodeEditorBase import CodeEditorBase


class PlainCodeEditor(CodeEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        # Use default painting from QPlainTextEdit for plain (NO_SAG) rendering.
        super().paintEvent(event)
