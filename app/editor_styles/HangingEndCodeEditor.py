from app.editor_styles.CodeEditorBase import CodeEditorBase


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
