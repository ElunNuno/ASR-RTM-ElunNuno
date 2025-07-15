from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox

class ModelManagerDialog(QDialog):
    """
    事件驱动模型管理对话框骨架：展示模型列表，支持启用/禁用、刷新、变更事件。
    """
    def __init__(self, event_bus, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.setWindowTitle("模型管理")
        self.resize(400, 300)
        self._init_ui()
        self._connect_events()
        self._load_models()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.model_list = QListWidget(self)
        layout.addWidget(self.model_list)
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新", self)
        self.enable_btn = QPushButton("启用/禁用", self)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.enable_btn)
        layout.addLayout(btn_layout)

    def _connect_events(self):
        self.refresh_btn.clicked.connect(self._on_refresh)
        self.enable_btn.clicked.connect(self._on_toggle_enable)
        self.model_list.itemDoubleClicked.connect(self._on_toggle_enable)
        # 订阅模型变更事件
        self.event_bus.subscribe("model_list_updated", self._on_model_list_updated)

    def _load_models(self):
        # 事件驱动请求模型列表
        self.event_bus.publish("request_model_list")

    def _on_refresh(self):
        self._load_models()

    def _on_toggle_enable(self):
        item = self.model_list.currentItem()
        if item:
            model_name = item.text()
            self.event_bus.publish("toggle_model_enable", model_name=model_name)

    def _on_model_list_updated(self, models=None, **kwargs):
        self.model_list.clear()
        if models:
            for m in models:
                self.model_list.addItem(m)
        else:
            self.model_list.addItem("无可用模型")
