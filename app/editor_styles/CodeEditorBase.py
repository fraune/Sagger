from PySide6.QtWidgets import QPlainTextEdit, QTextEdit
from PySide6.QtGui import QFont, QColor, QTextFormat, QPainter
from app.components.LineNumberArea import LineNumberArea
import math


class CodeEditorBase(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        monospace_font = QFont("Courier New")
        monospace_font.setStyleHint(QFont.Monospace)
        self.setFont(monospace_font)
        # Default weight parameter controlling "heaviness" of each line.
        self.weight = 1.0

        # Initialize the line number area.
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

        # Cache to store computed offsets for each block
        self.offsets_cache = {}

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberArea.computeWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
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

    # Shared utility: compute sag parameters for a given block of text.
    def compute_sag_parameters(self, fm, text):
        line_width = fm.horizontalAdvance(text)
        center = line_width / 2.0
        sag_factor = self.weight / 300.0
        max_offset = sag_factor * (center**2)
        return line_width, center, sag_factor, max_offset

    def _preparePainter(self):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipping(False)
        painter.setFont(self.font())
        painter.fillRect(self.viewport().rect(), self.palette().base())
        fm = painter.fontMetrics()
        return painter, fm

    def compute_offsets_for_block(self, fm, block_text):
        line_width, center, sag_factor, max_offset = self.compute_sag_parameters(
            fm, block_text
        )
        offsets = []
        cum_width = 0
        length = len(block_text)
        for i, ch in enumerate(block_text):
            char_width = fm.horizontalAdvance(ch)
            offset = self.calc_offset_for_char(
                i,
                cum_width,
                char_width,
                line_width,
                sag_factor,
                max_offset,
                center,
                length,
            )
            offsets.append(offset)
            cum_width += char_width
        return offsets

    def updateOffsets(self):
        fm = self.fontMetrics()
        self.offsets_cache = {}
        block = self.document().firstBlock()
        while block.isValid():
            block_text = block.text()
            self.offsets_cache[block.blockNumber()] = self.compute_offsets_for_block(
                fm, block_text
            )
            block = block.next()
        self.document().adjustSize()
        self.updateGeometry()
        self.viewport().update()

    def calc_offset_for_char(
        self,
        i,
        cum_width,
        char_width,
        line_width,
        sag_factor,
        max_offset,
        center,
        length,
    ):
        # Default: no sag effect; subclasses should override this method
        return 0

    def drawBlock(self, painter, fm, block):
        block_text = block.text()
        block_rect = self.blockBoundingGeometry(block).translated(self.contentOffset())
        baseline = block_rect.y() + fm.ascent()

        # Retrieve computed offsets for the block
        offsets = self.offsets_cache.get(block.blockNumber())
        if offsets is None or len(offsets) != len(block_text):
            offsets = self.compute_offsets_for_block(fm, block_text)

        # Compute x positions and character centers
        x = block_rect.x()
        x_centers = []
        char_widths = []
        for ch in block_text:
            cw = fm.horizontalAdvance(ch)
            char_widths.append(cw)
            x_centers.append(x + cw / 2)
            x += cw

        # Draw each character with rotation based on the tangent of the baseline curve
        for i, ch in enumerate(block_text):
            cw = char_widths[i]
            # Compute numerical derivative for tangent: use central difference if possible
            if len(x_centers) > 1:
                if i == 0:
                    dx = x_centers[1] - x_centers[0]
                    dy = offsets[1] - offsets[0]
                elif i == len(x_centers) - 1:
                    dx = x_centers[-1] - x_centers[-2]
                    dy = offsets[-1] - offsets[-2]
                else:
                    dx = x_centers[i + 1] - x_centers[i - 1]
                    dy = offsets[i + 1] - offsets[i - 1]
                slope = dy / dx if dx != 0 else 0
            else:
                slope = 0

            angle = math.degrees(math.atan(slope))

            # Draw character rotated about its center
            painter.save()
            painter.translate(x_centers[i], baseline + offsets[i])
            painter.rotate(angle)
            painter.drawText(-cw / 2, 0, ch)
            painter.restore()

    def paintEvent(self, event):
        painter, fm = self._preparePainter()
        block = self.document().firstBlock()
        while block.isValid():
            self.drawBlock(painter, fm, block)
            block = block.next()
