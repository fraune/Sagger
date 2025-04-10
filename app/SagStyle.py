from enum import Enum
from app.editor_styles.PlainCodeEditor import PlainCodeEditor
from app.editor_styles.HangingEndCodeEditor import HangingEndCodeEditor
from app.editor_styles.DroopingCenterCodeEditor import DroopingCenterCodeEditor

class SagStyle(Enum):
    NO_SAG = "No Sag"
    HANGING_END = "Hanging End"
    DROOPING_CENTER = "Drooping Center"

    def create_editor(self):
        match self:
            case SagStyle.HANGING_END:
                return HangingEndCodeEditor()
            case SagStyle.DROOPING_CENTER:
                return DroopingCenterCodeEditor()
            case _:
                return PlainCodeEditor()