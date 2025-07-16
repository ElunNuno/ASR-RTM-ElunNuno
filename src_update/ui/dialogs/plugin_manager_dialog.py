from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                           QPushButton, QMessageBox, QListWidgetItem)
from PyQt5.QtCore import Qt
from src_update.core.common.event_bus_interface import EventBusInterface

class PluginManagerDialog(QDialog):
    """事件驱动的插件管理对话框"""
    
    def __init__(self, event_bus: EventBusInterface, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setWindowTitle("插件管理")
        self.resize(400, 300)
        self.setup_ui()
        self._subscribe_events()
        self._load_plugins()

    def setup_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 插件列表
        self.plugin_list = QListWidget(self)
        layout.addWidget(self.plugin_list)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新", self)
        self.enable_btn = QPushButton("启用", self)
        self.disable_btn = QPushButton("禁用", self)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.enable_btn)
        button_layout.addWidget(self.disable_btn)
        layout.addLayout(button_layout)
        
        # 底部确认/取消按钮
        bottom_layout = QHBoxLayout()
        self.apply_btn = QPushButton("应用", self)
        self.cancel_btn = QPushButton("取消", self)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.cancel_btn)
        layout.addLayout(bottom_layout)

        # 连接按钮事件
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        self.enable_btn.clicked.connect(self._on_enable_clicked)
        self.disable_btn.clicked.connect(self._on_disable_clicked)
        self.apply_btn.clicked.connect(self._on_apply_clicked)
        self.cancel_btn.clicked.connect(self.reject)

    def _subscribe_events(self):
        """订阅事件总线事件"""
        self.event_bus.subscribe("plugins_list_updated", self._on_plugins_updated)
        self.event_bus.subscribe("plugin_status_changed", self._on_plugin_status_changed)

    def _load_plugins(self):
        """加载插件列表"""
        self.event_bus.publish("request_plugins_refresh")

    def _on_refresh_clicked(self):
        """刷新插件列表"""
        self._load_plugins()
    
    def _on_enable_clicked(self):
        """启用选中插件"""
        if selected := self.plugin_list.currentItem():
            plugin_name = selected.text()
            self.event_bus.publish("enable_plugin", plugin_name=plugin_name)

    def _on_disable_clicked(self):
        """禁用选中插件"""
        if selected := self.plugin_list.currentItem():
            plugin_name = selected.text()
            self.event_bus.publish("disable_plugin", plugin_name=plugin_name)

    def _on_apply_clicked(self):
        """应用按钮点击处理"""
        self.event_bus.publish("plugins_config_applied")
        self.accept()

    def _on_plugins_updated(self, plugins_list: list):
        """处理插件列表更新事件"""
        self.plugin_list.clear()
        if plugins_list:
            self.plugin_list.addItems(plugins_list)
        else:
            self.plugin_list.addItem("无可用插件")

    def _on_plugin_status_changed(self, plugin_name: str, enabled: bool):
        """处理插件状态变更事件"""
        for i in range(self.plugin_list.count()):
            item = self.plugin_list.item(i)
            if item.text() == plugin_name:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled if not enabled 
                            else item.flags() | Qt.ItemIsEnabled)
                break