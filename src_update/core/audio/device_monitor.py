from PyQt5.QtCore import QObject
from src_update.core.common.event_bus_interface import EventBusInterface

class AudioDeviceMonitor(QObject):
    def __init__(self, event_bus: EventBusInterface):
        super().__init__()
        self.event_bus = event_bus
        self._subscribe_events()
        
    def _subscribe_events(self):
        self.event_bus.subscribe("audio_device_error", self._handle_device_error)
        self.event_bus.subscribe("device_disconnected", self._handle_device_disconnect)
        
    def _handle_device_error(self, error_code: int, device_name: str):
        error_msg = self._get_error_message(error_code)
        self.event_bus.publish("show_error_dialog", 
                             title="音频设备错误",
                             message=f"设备 {device_name} 发生错误: {error_msg}")
        self.event_bus.publish("stop_transcription")
        
    def _handle_device_disconnect(self, device_name: str):
        self.event_bus.publish("show_warning_dialog",
                             title="设备断开",
                             message=f"音频设备 {device_name} 已断开连接")
        self.event_bus.publish("refresh_device_list")