"""
插件管理器模块
负责插件的加载、管理和生命周期控制
"""
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .interface import PluginInterface

logger = logging.getLogger(__name__)

class PluginManager:
    """插件管理器类"""
    
    def __init__(self):
        """初始化插件管理器"""
        self._plugins: Dict[str, PluginInterface] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._enabled: Dict[str, bool] = {}
        
    def register_plugin(self, plugin_id: str, plugin: PluginInterface) -> bool:
        """注册插件
        
        Args:
            plugin_id: 插件ID
            plugin: 插件实例
            
        Returns:
            bool: 注册是否成功
        """
        try:
            if plugin_id in self._plugins:
                logger.warning(f"插件已存在: {plugin_id}")
                return False
                
            if not isinstance(plugin, PluginInterface):
                logger.error(f"无效的插件类型: {type(plugin)}")
                return False
                
            self._plugins[plugin_id] = plugin
            self._enabled[plugin_id] = False
            logger.info(f"注册插件成功: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"注册插件失败: {plugin_id}, 错误: {e}")
            return False
            
    def unregister_plugin(self, plugin_id: str) -> bool:
        """注销插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            bool: 注销是否成功
        """
        try:
            if plugin_id not in self._plugins:
                logger.warning(f"插件不存在: {plugin_id}")
                return False
                
            plugin = self._plugins[plugin_id]
            if self._enabled[plugin_id]:
                if not plugin.cleanup():
                    logger.error(f"插件清理失败: {plugin_id}")
                    return False
                    
            del self._plugins[plugin_id]
            del self._enabled[plugin_id]
            if plugin_id in self._configs:
                del self._configs[plugin_id]
                
            logger.info(f"注销插件成功: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"注销插件失败: {plugin_id}, 错误: {e}")
            return False
            
    def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            bool: 启用是否成功
        """
        try:
            if plugin_id not in self._plugins:
                logger.warning(f"插件不存在: {plugin_id}")
                return False
                
            if self._enabled[plugin_id]:
                logger.warning(f"插件已启用: {plugin_id}")
                return True
                
            plugin = self._plugins[plugin_id]
            if not plugin.initialize():
                logger.error(f"插件初始化失败: {plugin_id}")
                return False
                
            if plugin_id in self._configs:
                if not plugin.configure(self._configs[plugin_id]):
                    logger.error(f"插件配置失败: {plugin_id}")
                    return False
                    
            self._enabled[plugin_id] = True
            logger.info(f"启用插件成功: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"启用插件失败: {plugin_id}, 错误: {e}")
            return False
            
    def disable_plugin(self, plugin_id: str) -> bool:
        """禁用插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            bool: 禁用是否成功
        """
        try:
            if plugin_id not in self._plugins:
                logger.warning(f"插件不存在: {plugin_id}")
                return False
                
            if not self._enabled[plugin_id]:
                logger.warning(f"插件已禁用: {plugin_id}")
                return True
                
            plugin = self._plugins[plugin_id]
            if not plugin.cleanup():
                logger.error(f"插件清理失败: {plugin_id}")
                return False
                
            self._enabled[plugin_id] = False
            logger.info(f"禁用插件成功: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"禁用插件失败: {plugin_id}, 错误: {e}")
            return False
            
    def configure_plugin(self, plugin_id: str, config: Dict[str, Any]) -> bool:
        """配置插件
        
        Args:
            plugin_id: 插件ID
            config: 配置字典
            
        Returns:
            bool: 配置是否成功
        """
        try:
            if plugin_id not in self._plugins:
                logger.warning(f"插件不存在: {plugin_id}")
                return False
                
            plugin = self._plugins[plugin_id]
            if not plugin.configure(config):
                logger.error(f"插件配置失败: {plugin_id}")
                return False
                
            self._configs[plugin_id] = config
            logger.info(f"配置插件成功: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"配置插件失败: {plugin_id}, 错误: {e}")
            return False
            
    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """获取插件实例
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            Optional[PluginInterface]: 插件实例，不存在则返回None
        """
        return self._plugins.get(plugin_id)
        
    def get_all_plugins(self) -> List[PluginInterface]:
        """获取所有插件
        
        Returns:
            List[PluginInterface]: 插件实例列表
        """
        return list(self._plugins.values())
        
    def get_enabled_plugins(self) -> List[PluginInterface]:
        """获取所有启用的插件
        
        Returns:
            List[PluginInterface]: 启用的插件实例列表
        """
        return [plugin for plugin_id, plugin in self._plugins.items() 
                if self._enabled[plugin_id]]
                
    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """检查插件是否启用
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            bool: 插件是否启用
        """
        return self._enabled.get(plugin_id, False)
