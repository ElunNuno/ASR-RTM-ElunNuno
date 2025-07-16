from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QComboBox, QProgressBar, QLabel)
from PyQt5.QtCore import Qt
from src_update.core.common.event_bus_interface import EventBusInterface

class ControlPanel(QWidget):
    """控制面板，包含设备选择、进度条、智能按钮等"""
    def __init__(self, event_bus: EventBusInterface, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setup_ui()
        self._subscribe_events()

    def setup_ui(self):
        """初始化UI布局"""
        main_layout = QVBoxLayout(self)

        # 设备选择区域
        device_layout = QHBoxLayout()
        self.device_label = QLabel("音频设备:", self)
        self.device_combo = QComboBox(self)
        self.refresh_devices_btn = QPushButton("刷新设备", self)
        device_layout.addWidget(self.device_label)
        device_layout.addWidget(self.device_combo, 1)  # 1表示可伸缩
        device_layout.addWidget(self.refresh_devices_btn)
        main_layout.addLayout(device_layout)

        # 转录控制区域
        control_layout = QHBoxLayout()
        self.transcribe_btn = SmartToggleButton("开始转录", "停止转录", self.event_bus, self)
        self.record_btn = SmartToggleButton("开始录音", "停止录音", self.event_bus, self)
        control_layout.addWidget(self.transcribe_btn)
        control_layout.addWidget(self.record_btn)
        main_layout.addLayout(control_layout)

        # 进度显示区域
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.time_label = QLabel("00:00", self)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.time_label)
        main_layout.addLayout(progress_layout)

        # 状态显示区域
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪", self)
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

        # 设置初始状态
        self.transcribe_btn.set_active_state(False)
        self.record_btn.set_active_state(False)

        # 连接按钮事件
        self._connect_buttons()

    def _connect_buttons(self):
        """连接按钮事件"""
        self.refresh_devices_btn.clicked.connect(self._on_refresh_devices)

    def _subscribe_events(self):
        """订阅事件总线事件"""
        self.event_bus.subscribe("devices_list_updated", self._on_devices_updated)
        self.event_bus.subscribe("progress_updated", self._on_progress_updated)
        self.event_bus.subscribe("status_updated", self._on_status_updated)

    def _on_refresh_devices(self):
        """刷新设备列表"""
        self.event_bus.publish("refresh_devices")

    def _on_devices_updated(self, devices):
        """处理设备列表更新事件"""
        self.device_combo.clear()
        for device_id, device_name in devices:
            self.device_combo.addItem(device_name, device_id)

    def _on_progress_updated(self, progress, time_str):
        """处理进度更新事件"""
        self.progress_bar.setValue(int(progress * 100))
        self.time_label.setText(time_str)

    def _on_status_updated(self, status):
        """处理状态更新事件"""
        self.status_label.setText(status)


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
        event_type = "start_transcription" if self.is_active else "stop_transcription"
        self.event_bus.publish(event_type)