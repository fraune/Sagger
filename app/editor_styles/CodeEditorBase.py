from PySide6.QtWidgets import QPlainTextEdit, QTextEdit
from PySide6.QtGui import QFont, QColor, QTextFormat

from app.components.LineNumberArea import LineNumberArea


class CodeEditorBase(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.Monospace)
        self.setFont(monospace_font)
        # Default weight parameter controlling "heaviness" of each line
        self.weight = 1.0

        # Initialize the line number area
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberArea.computeWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        # Simply update the entire line number area
        self.lineNumberArea.update()
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            cr.left(), cr.top(), self.lineNumberArea.computeWidth(), cr.height()
        )

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(50, 50, 50)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
