from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt

class TranscriptionProgressBar(QProgressBar):
    def __init__(self, event_bus, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setup_ui()
        self._subscribe_events()
    
    def setup_ui(self):
        """初始化UI"""
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat("%p%")
        
    def _subscribe_events(self):
        """订阅进度更新事件"""
        self.event_bus.subscribe("transcription_progress", self._on_progress_update)
        self.event_bus.subscribe("transcription_started", self._on_transcription_start)
        self.event_bus.subscribe("transcription_stopped", self._on_transcription_stop)
    
    def _on_progress_update(self, progress: float):
        """处理进度更新事件"""
        self.setValue(int(progress * 100))
    
    def _on_transcription_start(self):
        """处理转录开始事件"""
        self.setValue(0)
        self.setEnabled(True)
    
    def _on_transcription_stop(self):
        """处理转录停止事件"""
        self.setValue(100)
        self.setEnabled(False)