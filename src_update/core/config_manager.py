import json
import os

class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_path=None):
        if not hasattr(self, 'initialized'):
            if config_path is None:
                # Build the path relative to this file's location
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up two levels from core/ to src_update/ and then to the project root
                project_root = os.path.dirname(os.path.dirname(base_dir))
                config_path = os.path.join(project_root, 'config', 'config.json')
            
            self.config_path = config_path
            self.config = self._load_config()
            self.initialized = True

    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Handle the case where the config file is not found
            # You might want to log this or raise an exception
            return {}
        except json.JSONDecodeError:
            # Handle JSON parsing errors
            return {}

    def get(self, key, default=None):
        """Gets a configuration value using a dot-separated key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

# Global instance
config_manager = ConfigManager()