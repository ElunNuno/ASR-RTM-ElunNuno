from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from src_update.core.common.event_bus_interface import EventBusInterface

class ModelManagerDialog(QDialog):
    """事件驱动的模型管理对话框"""
    
    def __init__(self, event_bus: EventBusInterface, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setWindowTitle("模型管理")
        self.setup_ui()
        self._subscribe_events()

    def setup_ui(self):
        """初始化UI"""
        # 主布局
        layout = QVBoxLayout(self)
        
        # 模型列表
        self.model_list = QListWidget(self)
        layout.addWidget(self.model_list)
        
        # 操作按钮区域 - 水平布局
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新", self)
        self.enable_btn = QPushButton("启用", self)
        self.disable_btn = QPushButton("禁用", self)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.enable_btn)
        button_layout.addWidget(self.disable_btn)
        layout.addLayout(button_layout)
        
        # 底部确认/取消按钮 - 水平布局
        bottom_layout = QHBoxLayout()
        self.apply_btn = QPushButton("应用", self)
        self.cancel_btn = QPushButton("取消", self)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.cancel_btn)
        layout.addLayout(bottom_layout)

        # 连接事件处理
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        self.enable_btn.clicked.connect(self._on_enable_clicked)
        self.disable_btn.clicked.connect(self._on_disable_clicked)
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        self.cancel_btn.clicked.connect(self.reject)

    def _subscribe_events(self):
        """订阅事件总线事件"""
        self.event_bus.subscribe("models_list_updated", self._on_models_updated)
        self.event_bus.subscribe("model_status_changed", self._on_model_status_changed)

    def _on_refresh_clicked(self):
        """刷新模型列表"""
        self.event_bus.publish("request_models_refresh")
    
    def _on_enable_clicked(self):
        """启用选中模型"""
        if selected := self.model_list.currentItem():
            model_name = selected.text()
            self.event_bus.publish("enable_model", model_name=model_name)

    def _on_disable_clicked(self):
        """禁用选中模型"""
        if selected := self.model_list.currentItem():
            model_name = selected.text()
            self.event_bus.publish("disable_model", model_name=model_name)

    def _on_apply_clicked(self):
        """应用按钮点击处理"""
        self.event_bus.publish("models_config_applied")
        self.accept()

    def _on_models_updated(self, models_list: list):
        """处理模型列表更新事件"""
        self.model_list.clear()
        self.model_list.addItems(models_list)

    def _on_model_status_changed(self, model_name: str, enabled: bool):
        """处理模型状态变更事件"""
        for i in range(self.model_list.count()):
            item = self.model_list.item(i)
            if item.text() == model_name:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled if not enabled 
                            else item.flags() | Qt.ItemIsEnabled)
                break
