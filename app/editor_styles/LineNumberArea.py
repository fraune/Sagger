from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import QSize, Qt


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def computeWidth(self):
        digits = 1
        max_lines = max(1, self.codeEditor.blockCount())
        while max_lines >= 10:
            max_lines //= 10
            digits += 1
        space = 6 + self.codeEditor.fontMetrics().horizontalAdvance("9") * digits
        return space

    def sizeHint(self):
        return QSize(self.computeWidth(), 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(0, 0, 0))
        block = self.codeEditor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = (
            self.codeEditor.blockBoundingGeometry(block)
            .translated(self.codeEditor.contentOffset())
            .top()
        )
        bottom = top + self.codeEditor.blockBoundingRect(block).height()
        height = self.codeEditor.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(
                    0, int(top), self.computeWidth() - 3, height, Qt.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + self.codeEditor.blockBoundingRect(block).height()
            blockNumber += 1
