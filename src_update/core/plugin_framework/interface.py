"""
插件系统接口定义
定义了所有插件必须实现的基本接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class PluginInterface(ABC):
    """插件基础接口"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理插件资源
        
        Returns:
            bool: 清理是否成功
        """
        pass
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> bool:
        """配置插件
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 配置是否成功
        """
        pass
    
    @abstractmethod
    def get_id(self) -> str:
        """获取插件ID
        
        Returns:
            str: 插件的唯一标识符
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称
        
        Returns:
            str: 插件的显示名称
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """获取插件版本
        
        Returns:
            str: 插件的版本号
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取插件描述
        
        Returns:
            str: 插件的详细描述
        """
        pass
    
    @abstractmethod
    def get_author(self) -> str:
        """获取插件作者
        
        Returns:
            str: 插件的作者信息
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> Dict[str, str]:
        """获取插件依赖
        
        Returns:
            Dict[str, str]: 依赖的插件ID和所需版本的映射
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """获取插件配置模式
        
        Returns:
            Dict[str, Any]: JSON Schema格式的配置定义
        """
        pass
    
    @abstractmethod
    def validate_files(self) -> bool:
        """验证插件文件完整性
        
        Returns:
            bool: 文件是否完整有效
        """
        pass
    
    @abstractmethod
    def get_resource_path(self) -> Optional[Path]:
        """获取插件资源目录
        
        Returns:
            Optional[Path]: 插件资源目录的路径，如果没有则返回None
        """
        pass
