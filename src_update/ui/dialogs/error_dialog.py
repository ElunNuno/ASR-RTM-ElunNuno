from PyQt5.QtWidgets import QMessageBox
from src_update.core.common.event_bus_interface import EventBusInterface

class ErrorDialogManager:
    def __init__(self, event_bus: EventBusInterface, parent=None):
        self.event_bus = event_bus
        self.parent = parent
        self._subscribe_events()
        
    def _subscribe_events(self):
        self.event_bus.subscribe("show_error_dialog", self._show_error)
        self.event_bus.subscribe("show_warning_dialog", self._show_warning)
        
    def _show_error(self, title: str, message: str):
        QMessageBox.critical(self.parent, title, message)
        
    def _show_warning(self, title: str, message: str):
        QMessageBox.warning(self.parent, title, message)