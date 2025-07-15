from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget

class ASRPluginInterface(ABC):
    """ASR 插件接口"""

    @abstractmethod
    def get_name(self) -> str:
        """返回插件的显示名称"""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """初始化 ASR 引擎"""
        pass

    @abstractmethod
    def transcribe(self, audio_chunk: bytes) -> str:
        """实时转录音频块"""
        pass

    @abstractmethod
    def transcribe_file(self, file_path: str) -> str:
        """转录完整的音频文件"""
        pass

    @abstractmethod
    def create_ui(self) -> QWidget:
        """创建并返回此插件的专属UI组件（如字幕部件）"""
        pass