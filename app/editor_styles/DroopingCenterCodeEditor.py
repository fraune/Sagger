from app.editor_styles.CodeEditorBase import CodeEditorBase


class DroopingCenterCodeEditor(CodeEditorBase):
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
        char_center = cum_width + (char_width / 2.0)
        return max_offset - sag_factor * ((char_center - center) ** 2)
