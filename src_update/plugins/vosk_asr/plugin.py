from PyQt5.QtWidgets import QWidget
from ..interfaces import ASRPluginInterface
from src_update.core.config_manager import config_manager
from .engine import VoskASR
from .ui.subtitle_widget import VoskSubtitleWidget

class VoskASRPlugin(ASRPluginInterface):
    def __init__(self):
        self._engine = None
        self._ui = None

    def get_name(self) -> str:
        return "Vosk Small ASR"

    def initialize(self) -> None:
        model_path = config_manager.get('asr.models.vosk_small.path')
        if not model_path:
            raise ValueError("Vosk model path not found in config.json. Please check config/config.json")
        self.engine = VoskASR(model_path)

    def transcribe(self, audio_chunk: bytes) -> str:
        return self._engine.transcribe(audio_chunk)

    def transcribe_file(self, file_path: str) -> str:
        return self._engine.transcribe_file(file_path)

    def create_ui(self) -> QWidget:
        if not self._ui:
            self._ui = VoskSubtitleWidget()
        return self._ui