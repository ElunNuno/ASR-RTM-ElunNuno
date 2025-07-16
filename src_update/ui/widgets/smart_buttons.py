from PyQt5.QtWidgets import QPushButton
from src_update.core.common.event_bus_interface import EventBusInterface

class SmartToggleButton(QPushButton):
    """智能切换按钮基类"""
    def __init__(self, initial_text: str, active_text: str, event_bus: EventBusInterface, parent=None):
        super().__init__(initial_text, parent)
        self.initial_text = initial_text
        self.active_text = active_text
        self.event_bus = event_bus
        self.is_active = False
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        """点击时切换状态并发布对应事件"""
        self.set_active_state(not self.is_active)

    def set_active_state(self, is_active: bool):
        """设置按钮状态"""
        self.is_active = is_active
        self.setText(self.active_text if is_active else self.initial_text)

class TranscribeButton(SmartToggleButton):
    """智能转录按钮"""
    def __init__(self, event_bus: EventBusInterface, parent=None):
        super().__init__("开始转录", "停止转录", event_bus, parent)
        self._subscribe_events()

    def _subscribe_events(self):
        self.event_bus.subscribe("transcription_started", lambda: self.set_active_state(True))
        self.event_bus.subscribe("transcription_stopped", lambda: self.set_active_state(False))

    def _on_clicked(self):
        if not self.is_active:
            self.event_bus.publish("start_transcription")
        else:
            self.event_bus.publish("stop_transcription")

class RecordButton(SmartToggleButton):
    """智能录音按钮"""
    def __init__(self, event_bus: EventBusInterface, parent=None):
        super().__init__("开始录音", "停止录音", event_bus, parent)
        self._subscribe_events()
        
    def _subscribe_events(self):
        self.event_bus.subscribe("recording_started", lambda: self.set_active_state(True))
        self.event_bus.subscribe("recording_stopped", lambda: self.set_active_state(False))

    def _on_clicked(self):
        if not self.is_active:
            self.event_bus.publish("start_recording")
        else:
            self.event_bus.publish("stop_recording")