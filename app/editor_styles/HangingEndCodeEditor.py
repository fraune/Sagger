from PySide6.QtGui import QPainter
from app.editor_styles.CodeEditorBase import CodeEditorBase
import math


class HangingEndCodeEditor(CodeEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Dictionary to cache precalculated hanging offsets per block
        self.hanging_offsets = {}
        # Recalculate offsets whenever the text changes
        self.textChanged.connect(self.updateHangingOffsets)

    def updateHangingOffsets(self):
        """Precalculate hanging style offsets for each text block and adjust bottom margin accordingly."""
        fm = self.fontMetrics()
        self.hanging_offsets.clear()
        block = self.document().firstBlock()
        overall_max_sag = 0  # Track maximum sag offset among all blocks
        while block.isValid():
            block_text = block.text()
            offsets = []
            line_width = fm.horizontalAdvance(block_text)
            center = line_width / 2.0
            sag_factor = self.weight / 300.0
            max_offset = sag_factor * (center**2)
            cum_width = 0
            line_max = 0  # Maximum offset for this line
            for i, ch in enumerate(block_text):
                char_width = fm.horizontalAdvance(ch)
                if i == 0:
                    offset = 0
                else:
                    relative_center = cum_width + (char_width / 2.0)
                    offset = ((relative_center / line_width) ** 2) * max_offset
                offsets.append(offset)
                if offset > line_max:
                    line_max = offset
                cum_width += char_width
            self.hanging_offsets[block.blockNumber()] = offsets
            if line_max > overall_max_sag:
                overall_max_sag = line_max
            block = block.next()

        # Instead of adjusting the viewport margins, force a recalculation of the document layout
        # to include any extra vertical space required by the sag offsets.
        # !IMPORTANT! KEEP THESE LINES
        self.document().adjustSize()
        self.updateGeometry()
        self.viewport().update()

    def paintEvent(self, event):
        # Custom paint event that uses the precomputed hanging offsets and applies per-letter rotation
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setClipping(False)
        painter.setFont(self.font())
        painter.fillRect(self.viewport().rect(), self.palette().base())
        fm = painter.fontMetrics()
        block = self.document().firstBlock()
        active_block_number = self.textCursor().block().blockNumber()
        while block.isValid():
            block_text = block.text()
            block_rect = self.blockBoundingGeometry(block).translated(
                self.contentOffset()
            )
            baseline = block_rect.y() + fm.ascent()
            # Compute line parameters used for both sag offset and rotation
            line_width = fm.horizontalAdvance(block_text)
            center = line_width / 2.0
            sag_factor = self.weight / 300.0
            max_offset = sag_factor * (center**2)
            x = block_rect.x()
            offsets = self.hanging_offsets.get(block.blockNumber())
            if offsets is None or len(offsets) != len(block_text):
                # Recalculate offsets on the fly if not available
                offsets = []
                cum_width = 0
                for i, ch in enumerate(block_text):
                    char_width = fm.horizontalAdvance(ch)
                    if i == 0:
                        offsets.append(0)
                    else:
                        offset = (
                            (((cum_width + (char_width / 2.0)) / line_width) ** 2)
                            * max_offset
                            if line_width > 0
                            else 0
                        )
                        offsets.append(offset)
                    cum_width += char_width
            # Reset cumulative width for rotation computation
            cum_width = 0
            for i, ch in enumerate(block_text):
                char_width = fm.horizontalAdvance(ch)
                offset = offsets[i] if i < len(offsets) else 0
                # Calculate the letter's relative center position in the line
                relative_x_mid = cum_width + (char_width / 2.0)
                # Compute the slope of the quadratic sag curve: f(x) = (x/line_width)^2 * max_offset
                # f'(x) = 2 * max_offset * (x) / (line_width^2)
                slope = (
                    (2 * max_offset * relative_x_mid) / (line_width**2)
                    if line_width > 0
                    else 0
                )
                # Compute rotation angle in degrees from the tangent (negative for clockwise rotation)
                angle = math.degrees(math.atan(slope))
                painter.save()
                # Translate to the letter's base position
                painter.translate(x, baseline + offset)
                # Apply rotation based on the tangent of the sag curve
                painter.rotate(angle)
                # Draw the letter at the origin; drawing at (0, 0) positions the text with its baseline at 0
                painter.drawText(0, 0, ch)
                painter.restore()
                cum_width += char_width
                x += char_width
            block = block.next()
