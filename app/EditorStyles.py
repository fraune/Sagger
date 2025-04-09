# File: app/EditorStyles.py

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt


class CodeEditorBase(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.weight = (
            1.0  # Default weight parameter controlling "heaviness" of each line
        )
        # Set a bottom margin to reduce clipping of sagging text
        self.setViewportMargins(0, 0, 0, 100)


class PlainCodeEditor(CodeEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        # Use default painting from QPlainTextEdit for plain (NO_SAG) rendering.
        super().paintEvent(event)


class HangingEndCodeEditor(CodeEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent)
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
            max_offset = sag_factor * (center**2)
            cum_width = 0
            for i, ch in enumerate(block_text):
                char_width = fm.horizontalAdvance(ch)
                # Force the first and last character to use normal baseline.
                if i == 0 or i == len(block_text) - 1:
                    offsets.append(0)
                else:
                    relative_center = cum_width + (char_width / 2.0)
                    offset = ((relative_center / line_width) ** 2) * max_offset
                    offsets.append(offset)
                cum_width += char_width
            self.hanging_offsets[block.blockNumber()] = offsets
            block = block.next()

    def paintEvent(self, event):
        # Custom paint event that uses the precomputed hanging offsets.
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
            x = block_rect.x()
            offsets = self.hanging_offsets.get(block.blockNumber())
            if offsets is None or len(offsets) != len(block_text):
                # Recalculate offsets on the fly if not available.
                offsets = []
                line_width = fm.horizontalAdvance(block_text)
                center = line_width / 2.0
                sag_factor = self.weight / 300.0
                max_offset = sag_factor * (center**2)
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
                offset = offsets[i] if i < len(offsets) else 0
                painter.drawText(x, baseline + offset, ch)
                x += char_width
            block = block.next()


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
