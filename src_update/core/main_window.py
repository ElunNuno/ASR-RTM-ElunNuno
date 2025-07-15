import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QComboBox, QApplication

# Adjust import paths for the new structure
from .plugin_manager import PluginManager
from .. import plugins # Import the plugins package

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ASR Plugin Host")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Instantiate the plugin manager
        self.plugin_manager = PluginManager(plugins)
        self.active_plugin = None

        # Create UI elements
        self.plugin_selector = QComboBox()
        self.plugin_ui_container = QWidget()

        # Add widgets to layout
        self.layout.addWidget(self.plugin_selector)
        self.layout.addWidget(self.plugin_ui_container)

        # Populate plugin selector and connect signals
        self.populate_plugins()
        self.plugin_selector.currentTextChanged.connect(self.activate_plugin)

        # Activate the first plugin by default
        if self.plugin_manager.get_all_plugins():
            self.activate_plugin(self.plugin_selector.currentText())

    def populate_plugins(self):
        """Fills the dropdown with discovered plugins."""
        for plugin in self.plugin_manager.get_all_plugins():
            self.plugin_selector.addItem(plugin.get_name())

    def activate_plugin(self, plugin_name: str):
        """Activates the selected plugin and displays its UI."""
        for plugin in self.plugin_manager.get_all_plugins():
            if plugin.get_name() == plugin_name:
                self.active_plugin = plugin
                break
        
        if self.active_plugin:
            # Clear previous plugin UI
            old_layout = self.plugin_ui_container.layout()
            if old_layout is not None:
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

            # Create and add new plugin UI
            plugin_ui = self.active_plugin.create_ui()
            new_layout = QVBoxLayout()
            new_layout.addWidget(plugin_ui)
            self.plugin_ui_container.setLayout(new_layout)
            print(f"Activated plugin: {plugin_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # To make imports work correctly when running this file directly for testing
    # we might need to adjust the python path.
    # This is a common issue in package development.
    # A better approach is to run it via the main.py entrypoint.
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())