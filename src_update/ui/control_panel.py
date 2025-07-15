"""
事件驱动版控制面板（设备选择+进度条），适配插件架构
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt

class ControlPanel(QWidget):
    def __init__(self, event_bus, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self._create_widgets()
        self._create_layout()
        self._connect_events()

    def _create_widgets(self):
        self.start_button = QPushButton("开始转录", self)
        self.device_combo = QComboBox(self)
        self.device_combo.setPlaceholderText("选择音频设备")
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v/%m")

    def _create_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.device_combo)
        self.setLayout(layout)

    def _connect_events(self):
        self.start_button.clicked.connect(self._on_start_clicked)
        self.device_combo.currentTextChanged.connect(self._on_device_changed)
        # 订阅事件总线
        self.event_bus.subscribe("progress_update", self.update_progress)
        self.event_bus.subscribe("device_list", self.set_devices)

    def _on_start_clicked(self):
        self.event_bus.publish("start_transcription", device_id=self.get_selected_device())

    def _on_device_changed(self, device_name):
        self.event_bus.publish("set_audio_device", device_name=device_name)

    def set_devices(self, devices):
        self.device_combo.clear()
        for device in devices:
            # 设备对象应至少有 name 属性
            self.device_combo.addItem(device.name, device)

    def get_selected_device(self):
        idx = self.device_combo.currentIndex()
        return self.device_combo.itemData(idx)

    def update_progress(self, value, text=None, **kwargs):
        self.progress_bar.setValue(value)
        if text:
            self.progress_bar.setFormat(text)
