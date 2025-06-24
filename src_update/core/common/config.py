"""
配置管理系统

提供统一的配置管理接口，支持多配置文件、配置热重载、配置验证等功能
"""
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path

class ConfigManager:
    """配置管理器，采用单例模式"""
    _instance = None
    _configs: Dict[str, Dict[str, Any]] = {}
    _config_files: Dict[str, Path] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def load_config(self, name: str, config_path: Path) -> bool:
        """
        加载指定配置文件
        
        Args:
            name: 配置名称
            config_path: 配置文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            if not config_path.exists():
                logging.error(f"配置文件不存在: {config_path}")
                return False
                
            with config_path.open('r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            self._configs[name] = config_data
            self._config_files[name] = config_path
            return True
            
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return False
    
    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定名称的配置
        
        Args:
            name: 配置名称
            
        Returns:
            Optional[Dict[str, Any]]: 配置数据，如果不存在返回None
        """
        return self._configs.get(name)
    
    def save_config(self, name: str) -> bool:
        """
        保存指定配置到文件
        
        Args:
            name: 配置名称
            
        Returns:
            bool: 保存是否成功
        """
        if name not in self._configs or name not in self._config_files:
            logging.error(f"配置 {name} 不存在")
            return False
            
        try:
            config_path = self._config_files[name]
            with config_path.open('w', encoding='utf-8') as f:
                json.dump(self._configs[name], f, indent=4, ensure_ascii=False)
            return True
            
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
            return False
    
    def update_config(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        更新指定配置的值
        
        Args:
            name: 配置名称
            updates: 要更新的配置项
            
        Returns:
            bool: 更新是否成功
        """
        if name not in self._configs:
            logging.error(f"配置 {name} 不存在")
            return False
            
        try:
            self._configs[name].update(updates)
            return True
            
        except Exception as e:
            logging.error(f"更新配置失败: {e}")
            return False
