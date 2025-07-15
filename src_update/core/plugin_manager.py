import importlib
import pkgutil
import os

# We need to adjust the path to correctly import interfaces
# This assumes src_update is on the Python path.
from ..plugins.interfaces import ASRPluginInterface

class PluginManager:
    def __init__(self, plugin_package):
        self.plugin_package = plugin_package
        self.plugins = {}
        self._discover_plugins()

    def _discover_plugins(self):
        """Dynamically discovers and loads plugins."""
        # Ensure the package itself is a module
        package_module = importlib.import_module(self.plugin_package.__name__)

        for _, name, _ in pkgutil.iter_modules(package_module.__path__, package_module.__name__ + "."):
            try:
                module = importlib.import_module(name)
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    # Check if it's a class, a subclass of our interface, and not the interface itself
                    if isinstance(item, type) and issubclass(item, ASRPluginInterface) and item is not ASRPluginInterface:
                        # The key will be the plugin's module name (e.g., 'vosk_asr')
                        plugin_instance = item()
                        plugin_key = name.split('.')[-1]
                        self.plugins[plugin_key] = plugin_instance
                        print(f"Discovered and loaded plugin: {plugin_key}")
            except Exception as e:
                print(f"Failed to load plugin {name}: {e}")

    def get_plugin(self, name: str) -> ASRPluginInterface:
        return self.plugins.get(name)

    def get_all_plugins(self) -> list[ASRPluginInterface]:
        return list(self.plugins.values())