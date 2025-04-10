from app.editor_styles.CodeEditorBase import CodeEditorBase
import math


class HangingEndCodeEditor(CodeEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offsets_cache = {}
        # Recalculate offsets whenever the text changes.
        self.textChanged.connect(self.updateOffsets)

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
        if i == 0:
            return 0
        else:
            relative_center = cum_width + (char_width / 2.0)
            return (
                ((relative_center / line_width) ** 2 * max_offset)
                if line_width > 0
                else 0
            )

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
