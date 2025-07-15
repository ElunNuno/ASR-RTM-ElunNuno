from PyQt5.QtWidgets import QMenuBar, QAction

class MainMenu(QMenuBar):
    def __init__(self, event_bus, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self._init_menus()

    def _init_menus(self):
        # 文件菜单
        file_menu = self.addMenu("文件")
        save_action = QAction("保存转录", self)
        save_action.triggered.connect(lambda: self.event_bus.publish("save_transcript"))
        file_menu.addAction(save_action)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(lambda: self.event_bus.publish("exit_app"))
        file_menu.addAction(exit_action)

        # 模型菜单（可动态生成）
        model_menu = self.addMenu("模型")
        # 事件驱动模型切换
        for model in ["vosk_small", "sherpa_onnx_int8", "sherpa_onnx_std", "sherpa_0626_int8", "sherpa_0626_std", "opus", "argos"]:
            action = QAction(model, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, m=model: self.event_bus.publish("set_asr_model", model_name=m))
            model_menu.addAction(action)

        # 插件菜单
        plugin_menu = self.addMenu("插件")
        plugin_manager_action = QAction("插件管理", self)
        plugin_manager_action.triggered.connect(lambda: self.event_bus.publish("show_plugin_manager"))
        plugin_menu.addAction(plugin_manager_action)

        # 帮助菜单
        help_menu = self.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(lambda: self.event_bus.publish("show_about"))
        help_menu.addAction(about_action)
        usage_action = QAction("使用说明", self)
        usage_action.triggered.connect(lambda: self.event_bus.publish("show_usage"))
        help_menu.addAction(usage_action)
