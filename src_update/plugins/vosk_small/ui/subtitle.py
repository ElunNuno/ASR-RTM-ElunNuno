"""
SubtitleWidget for vosk_small plugin.
Implements subtitle display logic specific to vosk_small, inheriting from SubtitleWidgetBase.
"""
from src_update.core.common.subtitle_widget_base import SubtitleWidgetBase


from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class SubtitleWidget(SubtitleWidgetBase):
    """Subtitle widget for vosk_small plugin (event-driven, basic implementation)."""
    def __init__(self, event_bus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus = event_bus
        self.label = QLabel("", *args, **kwargs)
        self.label.setAlignment(Qt.Alignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop))
        self.label.setWordWrap(True)
        self._current_text = ""
        # 订阅事件
        self.event_bus.subscribe("asr_result", self.update_text)
        self.event_bus.subscribe("subtitle_update", self.update_text)

    def update_text(self, text: str, **kwargs):
        self._current_text = text
        self.label.setText(text)

    def clear(self):
        self._current_text = ""
        self.label.clear()

    def set_style(self, style: dict):
        # 简单实现：支持字体大小、颜色等
        if 'font-size' in style:
            self.label.setStyleSheet(f"font-size: {style['font-size']}pt;")
        if 'color' in style:
            self.label.setStyleSheet(self.label.styleSheet() + f"color: {style['color']};")

    def get_current_text(self) -> str:
        return self._current_text
