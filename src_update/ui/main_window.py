"""
新主窗口模块（事件驱动解耦版）
"""


from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import Qt, QTimer
from src_update.core.common.event_bus_interface import EventBusInterface
from src_update.plugins.vosk_small.ui.subtitle import SubtitleWidget
from .control_panel import ControlPanel
from .menu import MainMenu


class MainWindow(QMainWindow):
    """
    事件驱动解耦主窗口，完整集成字幕控件、控制面板、菜单栏，预留全部原版功能接口。
    """
    def __init__(self, event_bus: EventBusInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_bus = event_bus
        self.setWindowTitle("实时字幕")
        self.resize(800, 400)

        # 事件驱动菜单栏
        self.menu_bar = MainMenu(self.event_bus, self)
        self.setMenuBar(self.menu_bar)

        # 主体布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 字幕控件（顶部）
        self.subtitle_widget = SubtitleWidget(self.event_bus)
        layout.addWidget(self.subtitle_widget.label, 1)

        # 控制面板（底部，含设备选择、进度条、开始按钮等）
        self.control_panel = ControlPanel(self.event_bus)
        layout.addWidget(self.control_panel)

        # 订阅事件
        self._subscribe_events()

        # 窗口样式/状态恢复（可扩展）
        self._apply_window_style()
        self._load_window_state()

    # 菜单初始化已由MainMenu实现

    def _subscribe_events(self):
        # 状态栏/窗口标题等
        self.event_bus.subscribe("status_update", self._on_status_update)
        self.event_bus.subscribe("show_message", self._on_show_message)
        # 事件驱动对话框/管理器弹出
        self.event_bus.subscribe("show_model_manager", self._on_show_model_manager)
        self.event_bus.subscribe("show_plugin_manager", self._on_show_plugin_manager)
        self.event_bus.subscribe("show_asr_config", self._on_show_asr_config)
        self.event_bus.subscribe("select_file", self._on_select_file)
        # 预留更多事件...

    def _on_show_model_manager(self, *args, **kwargs):
        from .dialogs.model_manager_dialog import ModelManagerDialog
        dlg = ModelManagerDialog(self.event_bus, self)
        dlg.exec_()

    def _on_show_plugin_manager(self, *args, **kwargs):
        # TODO: 事件驱动弹出插件管理对话框（后续可集成新版UI/逻辑）
        QMessageBox.information(self, "插件管理", "弹出插件管理对话框（待实现）")

    def _on_show_asr_config(self, *args, **kwargs):
        # TODO: 事件驱动弹出ASR配置对话框（后续可集成新版UI/逻辑）
        QMessageBox.information(self, "ASR配置", "弹出ASR配置对话框（待实现）")

    def _on_select_file(self, *args, **kwargs):
        # TODO: 事件驱动弹出文件选择对话框（后续可集成新版UI/逻辑）
        QMessageBox.information(self, "选择文件", "弹出文件选择对话框（待实现）")

    def _on_status_update(self, msg, **kwargs):
        self.setWindowTitle(f"实时字幕 - {msg}")

    def _on_show_message(self, msg, title="提示", **kwargs):
        QMessageBox.information(self, title, msg)

    def _apply_window_style(self):
        # 预留：可通过事件/配置设置窗口样式、透明度、置顶等
        self.setWindowOpacity(0.9)
        # 兼容 PyQt5/6 的置顶写法
        try:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        except AttributeError:
            self.setWindowFlags(self.windowFlags())

    def _load_window_state(self):
        # 事件驱动+配置管理恢复窗口状态
        try:
            from src_update.core.common.config import ConfigManager
            config = ConfigManager().get_config("window")
            if config:
                x = config.get("pos_x", 100)
                y = config.get("pos_y", 100)
                w = config.get("width", 800)
                h = config.get("height", 400)
                opacity = config.get("opacity", 0.9)
                self.setGeometry(x, y, w, h)
                self.setWindowOpacity(opacity)
        except Exception:
            pass

    def closeEvent(self, event):
        # 保存窗口状态到配置
        try:
            from src_update.core.common.config import ConfigManager
            geometry = self.geometry()
            state = {
                "pos_x": geometry.x(),
                "pos_y": geometry.y(),
                "width": geometry.width(),
                "height": geometry.height(),
                "opacity": self.windowOpacity()
            }
            cm = ConfigManager()
            cm.update_config("window", state)
            cm.save_config("window")
        except Exception:
            pass
        super().closeEvent(event)

    def _update_menu_states(self):
        """更新菜单项状态"""
        # 文件菜单
        self.menu_bar.file_menu.actions()[0].setEnabled(self.has_transcription)
        
        # 转录控制菜单
        self.menu_bar.plugin_menu.actions()[0].setEnabled(not self.is_transcribing)
        self.menu_bar.plugin_menu.actions()[1].setEnabled(self.is_transcribing)
        self.menu_bar.plugin_menu.actions()[2].setEnabled(self.is_transcribing)
        
        # 设备菜单
        self.menu_bar.model_menu.setEnabled(self.has_available_devices)

    # 预留：全部原版业务方法、对话框、配置、模型/插件管理等，均通过事件驱动集成
    # 如 self.event_bus.publish("open_model_manager")、self.event_bus.subscribe("model_list", ...)
