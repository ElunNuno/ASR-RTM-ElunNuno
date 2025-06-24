"""
测试插件系统的基础功能
"""
import pytest
from pathlib import Path
from typing import Dict, Any

from src_update.core.plugin_framework.interface import PluginInterface
from src_update.core.plugin_framework.manager import PluginManager

# 测试用插件类
class TestPlugin(PluginInterface):
    def __init__(self, plugin_id: str, name: str):
        self.plugin_id = plugin_id
        self.plugin_name = name
        self.initialized = False
        self.config = {}
    
    def initialize(self) -> bool:
        self.initialized = True
        return True
    
    def cleanup(self) -> bool:
        self.initialized = False
        return True
    
    def configure(self, config: Dict[str, Any]) -> bool:
        self.config = config
        return True
    
    def get_id(self) -> str:
        return self.plugin_id
    
    def get_name(self) -> str:
        return self.plugin_name
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Test Plugin"
    
    def get_author(self) -> str:
        return "Test Author"
    
    def get_dependencies(self) -> Dict[str, str]:
        return {}
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test": {"type": "string"}
            }
        }
    
    def validate_files(self) -> bool:
        return True
    
    def get_resource_path(self) -> Path:
        return Path(__file__).parent

class TestPluginSystem:
    """插件系统测试类"""
    
    @pytest.fixture
    def plugin_manager(self):
        """创建插件管理器实例"""
        return PluginManager()
    
    @pytest.fixture
    def test_plugin(self):
        """创建测试插件实例"""
        return TestPlugin("test_plugin", "Test Plugin")
    
    def test_plugin_registration(self, plugin_manager, test_plugin):
        """测试插件注册"""
        # 注册插件
        assert plugin_manager.register_plugin(test_plugin.get_id(), test_plugin)
        
        # 验证插件是否已注册
        assert plugin_manager.get_plugin(test_plugin.get_id()) == test_plugin
        
        # 验证插件默认是禁用状态
        assert not plugin_manager.is_plugin_enabled(test_plugin.get_id())
    
    def test_plugin_enable_disable(self, plugin_manager, test_plugin):
        """测试插件启用和禁用"""
        # 注册插件
        plugin_manager.register_plugin(test_plugin.get_id(), test_plugin)
        
        # 启用插件
        assert plugin_manager.enable_plugin(test_plugin.get_id())
        assert plugin_manager.is_plugin_enabled(test_plugin.get_id())
        assert test_plugin.initialized
        
        # 禁用插件
        assert plugin_manager.disable_plugin(test_plugin.get_id())
        assert not plugin_manager.is_plugin_enabled(test_plugin.get_id())
        assert not test_plugin.initialized
    
    def test_plugin_configuration(self, plugin_manager, test_plugin):
        """测试插件配置"""
        # 注册插件
        plugin_manager.register_plugin(test_plugin.get_id(), test_plugin)
        
        # 配置插件
        config = {"test": "value"}
        assert plugin_manager.configure_plugin(test_plugin.get_id(), config)
        assert test_plugin.config == config
    
    def test_plugin_lifecycle(self, plugin_manager, test_plugin):
        """测试插件生命周期"""
        # 注册
        assert plugin_manager.register_plugin(test_plugin.get_id(), test_plugin)
        
        # 配置
        config = {"test": "value"}
        assert plugin_manager.configure_plugin(test_plugin.get_id(), config)
        
        # 启用
        assert plugin_manager.enable_plugin(test_plugin.get_id())
        assert test_plugin.initialized
        
        # 禁用
        assert plugin_manager.disable_plugin(test_plugin.get_id())
        assert not test_plugin.initialized
        
        # 注销
        assert plugin_manager.unregister_plugin(test_plugin.get_id())
        assert plugin_manager.get_plugin(test_plugin.get_id()) is None
    
    def test_multiple_plugins(self, plugin_manager):
        """测试多插件管理"""
        plugins = [
            TestPlugin("plugin1", "Plugin 1"),
            TestPlugin("plugin2", "Plugin 2"),
            TestPlugin("plugin3", "Plugin 3")
        ]
        
        # 注册多个插件
        for plugin in plugins:
            assert plugin_manager.register_plugin(plugin.get_id(), plugin)
        
        # 验证插件数量
        assert len(plugin_manager.get_all_plugins()) == len(plugins)
        
        # 启用所有插件
        for plugin in plugins:
            assert plugin_manager.enable_plugin(plugin.get_id())
        
        # 验证已启用插件数量
        assert len(plugin_manager.get_enabled_plugins()) == len(plugins)
        
        # 禁用所有插件
        for plugin in plugins:
            assert plugin_manager.disable_plugin(plugin.get_id())
        
        # 验证已启用插件数量为0
        assert len(plugin_manager.get_enabled_plugins()) == 0
