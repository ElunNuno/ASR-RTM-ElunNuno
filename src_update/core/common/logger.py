"""
日志系统模块
提供统一的日志记录功能
"""
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

class LoggerFactory:
    """日志工厂类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LoggerFactory._initialized:
            self._loggers = {}
            LoggerFactory._initialized = True
    
    def initialize(self, log_dir: Path, level: str = 'INFO') -> None:
        """初始化日志系统
        
        Args:
            log_dir: 日志目录
            level: 日志级别
        """
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
        )
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 创建默认的文件处理器
        default_log_file = log_dir / f'system_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(default_log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """获取日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 指定的日志文件名，可选
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name in self._loggers:
            return self._loggers[name]
            
        logger = logging.getLogger(name)
        
        if log_file:
            # 为特定模块创建单独的文件处理器
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s'
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        self._loggers[name] = logger
        return logger

# 创建全局日志工厂实例
logger_factory = LoggerFactory()
