from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QPushButton, QSpinBox, QCheckBox, QComboBox, QLabel)
from PyQt5.QtCore import Qt
from src_update.core.common.event_bus_interface import EventBusInterface

class ASRConfigDialog(QDialog):
    """事件驱动的 ASR 配置对话框"""
    
    def __init__(self, event_bus: EventBusInterface, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setWindowTitle("ASR 配置")
        self.resize(400, 300)
        self.setup_ui()
        self._subscribe_events()
        self._load_current_config()

    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 配置表单
        form_layout = QFormLayout()
        
        # 采样率设置
        self.sample_rate = QComboBox(self)
        self.sample_rate.addItems(['16000', '44100', '48000'])
        form_layout.addRow("采样率:", self.sample_rate)
        
        # 静音检测
        self.vad_enabled = QCheckBox("启用静音检测", self)
        self.vad_threshold = QSpinBox(self)
        self.vad_threshold.setRange(0, 100)
        form_layout.addRow(self.vad_enabled)
        form_layout.addRow("静音阈值:", self.vad_threshold)
        
        # 识别参数
        self.max_alternatives = QSpinBox(self)
        self.max_alternatives.setRange(1, 10)
        form_layout.addRow("最大候选数:", self.max_alternatives)
        
        layout.addLayout(form_layout)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("应用", self)
        self.cancel_btn = QPushButton("取消", self)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        # 连接按钮事件
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        self.cancel_btn.clicked.connect(self.reject)

    def _subscribe_events(self):
        """订阅事件总线事件"""
        self.event_bus.subscribe("asr_config_updated", self._on_config_updated)

    def _load_current_config(self):
        """加载当前配置"""
        self.event_bus.publish("request_asr_config")

    def _on_apply_clicked(self):
        """应用按钮点击处理"""
        config = {
            'sample_rate': int(self.sample_rate.currentText()),
            'vad_enabled': self.vad_enabled.isChecked(),
            'vad_threshold': self.vad_threshold.value(),
            'max_alternatives': self.max_alternatives.value()
        }
        self.event_bus.publish("apply_asr_config", config=config)
        self.accept()

    def _on_config_updated(self, config: dict):
        """处理配置更新事件"""
        self.sample_rate.setCurrentText(str(config.get('sample_rate', 16000)))
        self.vad_enabled.setChecked(config.get('vad_enabled', True))
        self.vad_threshold.setValue(config.get('vad_threshold', 30))
        self.max_alternatives.setValue(config.get('max_alternatives', 1))