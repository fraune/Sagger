from PySide6.QtGui import QPainter

from app.editor_styles.CodeEditorBase import CodeEditorBase


class DroopingCenterCodeEditor(CodeEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        # Custom paint event that draws a curved baseline with drooping at the center.
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipping(False)
        painter.setFont(self.font())
        painter.fillRect(self.viewport().rect(), self.palette().base())
        fm = painter.fontMetrics()
        block = self.document().firstBlock()
        while block.isValid():
            block_text = block.text()
            block_rect = self.blockBoundingGeometry(block).translated(
                self.contentOffset()
            )
            baseline = block_rect.y() + fm.ascent()
            line_width = fm.horizontalAdvance(block_text)
            center = line_width / 2.0
            sag_factor = self.weight / 300.0
            max_offset = sag_factor * (center**2)
            x = block_rect.x()
            for i, ch in enumerate(block_text):
                char_width = fm.horizontalAdvance(ch)
                # The first and last characters remain at the baseline.
                if i == 0 or i == len(block_text) - 1:
                    offset = 0
                else:
                    char_center = (x - block_rect.x()) + (char_width / 2.0)
                    offset = max_offset - sag_factor * ((char_center - center) ** 2)
                painter.drawText(x, baseline + offset, ch)
                x += char_width
            block = block.next()
