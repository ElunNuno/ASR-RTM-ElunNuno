"""
测试配置管理系统
"""
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

from src_update.core.common.config import ConfigManager

class TestConfigManager:
    """配置管理器测试类"""
    
    @pytest.fixture
    def config_manager(self):
        """创建配置管理器实例"""
        manager = ConfigManager()
        manager._configs.clear()  # 清除单例可能保留的配置
        return manager
    
    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            temp.write(b'{"test": "value"}')
            return Path(temp.name)
    
    def test_load_config(self, config_manager, temp_config_file):
        """测试加载配置"""
        # 加载配置文件
        config = config_manager.load_config(temp_config_file)
        
        # 验证配置内容
        assert config is not None
        assert config["test"] == "value"
        
        # 验证配置已缓存
        assert config_manager.get_config(temp_config_file) == config
    
    def test_save_config(self, config_manager, temp_config_file):
        """测试保存配置"""
        # 准备新配置
        new_config = {
            "test": "new_value",
            "number": 42
        }
        
        # 保存配置
        assert config_manager.save_config(temp_config_file, new_config)
        
        # 重新加载并验证
        loaded_config = config_manager.load_config(temp_config_file)
        assert loaded_config == new_config
    
    def test_update_config(self, config_manager, temp_config_file):
        """测试更新配置"""
        # 加载初始配置
        config_manager.load_config(temp_config_file)
        
        # 更新配置
        updates = {
            "test": "updated_value",
            "new_key": "new_value"
        }
        assert config_manager.update_config(temp_config_file, updates)
        
        # 验证更新结果
        config = config_manager.get_config(temp_config_file)
        assert config["test"] == "updated_value"
        assert config["new_key"] == "new_value"
    
    def test_nonexistent_config(self, config_manager):
        """测试不存在的配置文件"""
        nonexistent_file = Path("nonexistent.json")
        
        # 尝试加载不存在的文件
        assert config_manager.load_config(nonexistent_file) is None
        
        # 尝试获取不存在的配置
        assert config_manager.get_config(nonexistent_file) is None
    
    def test_singleton_behavior(self, config_manager, temp_config_file):
        """测试单例行为"""
        # 加载配置到第一个实例
        config_manager.load_config(temp_config_file)
        
        # 创建新实例
        another_manager = ConfigManager()
        
        # 验证两个实例共享配置
        assert another_manager.get_config(temp_config_file) == \
               config_manager.get_config(temp_config_file)
    
    def teardown_method(self, method):
        """测试清理"""
        # 清理临时文件
        for config_file in Path(tempfile.gettempdir()).glob("*.json"):
            try:
                config_file.unlink()
            except Exception:
                pass
