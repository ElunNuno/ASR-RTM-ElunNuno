"""
测试日志系统
"""
import pytest
import tempfile
from pathlib import Path
import logging
import os

from src_update.core.common.logger import LoggerFactory

class TestLoggerSystem:
    """日志系统测试类"""
    
    @pytest.fixture
    def logger_factory(self):
        """创建日志工厂实例"""
        factory = LoggerFactory()
        return factory
    
    @pytest.fixture
    def temp_log_dir(self):
        """创建临时日志目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_logger_initialization(self, logger_factory, temp_log_dir):
        """测试日志初始化"""
        # 初始化日志系统
        logger_factory.initialize(temp_log_dir, 'DEBUG')
        
        # 验证系统日志文件是否创建
        log_files = list(temp_log_dir.glob('*.log'))
        assert len(log_files) == 1
        
        # 获取并测试日志记录器
        logger = logger_factory.get_logger('test_logger')
        assert logger.getEffectiveLevel() == logging.DEBUG
        
        # 写入一条日志
        test_message = "Test log message"
        logger.info(test_message)
        
        # 验证日志内容
        with open(log_files[0], 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert test_message in log_content
    
    def test_multiple_loggers(self, logger_factory, temp_log_dir):
        """测试多个日志记录器"""
        logger_factory.initialize(temp_log_dir)
        
        # 创建两个不同的日志记录器
        logger1 = logger_factory.get_logger('logger1')
        logger2 = logger_factory.get_logger('logger2')
        
        # 写入不同的日志消息
        logger1.info("Message from logger1")
        logger2.info("Message from logger2")
        
        # 验证日志文件
        log_files = list(temp_log_dir.glob('*.log'))
        assert len(log_files) == 1
        
        # 验证日志内容
        with open(log_files[0], 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert "Message from logger1" in log_content
            assert "Message from logger2" in log_content
    
    def test_custom_log_file(self, logger_factory, temp_log_dir):
        """测试自定义日志文件"""
        logger_factory.initialize(temp_log_dir)
        
        # 创建带自定义日志文件的记录器
        custom_log_file = temp_log_dir / 'custom.log'
        logger = logger_factory.get_logger('custom_logger', str(custom_log_file))
        
        # 写入日志
        logger.info("Custom log message")
        
        # 验证自定义日志文件
        assert custom_log_file.exists()
        with open(custom_log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert "Custom log message" in log_content
    
    def test_log_levels(self, logger_factory, temp_log_dir):
        """测试日志级别"""
        logger_factory.initialize(temp_log_dir, 'INFO')
        logger = logger_factory.get_logger('test_logger')
        
        # 写入不同级别的日志
        logger.debug("Debug message")  # 不应该被记录
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # 验证日志内容
        log_files = list(temp_log_dir.glob('*.log'))
        with open(log_files[0], 'r', encoding='utf-8') as f:
            log_content = f.read()
            assert "Debug message" not in log_content
            assert "Info message" in log_content
            assert "Warning message" in log_content
            assert "Error message" in log_content
    
    def test_singleton_behavior(self, logger_factory, temp_log_dir):
        """测试单例行为"""
        logger_factory.initialize(temp_log_dir)
        
        # 通过第一个实例创建日志记录器
        logger1 = logger_factory.get_logger('test_logger')
        
        # 创建新的工厂实例
        another_factory = LoggerFactory()
        logger2 = another_factory.get_logger('test_logger')
        
        # 验证是同一个日志记录器
        assert logger1 is logger2
    
    def teardown_method(self, method):
        """测试清理"""
        # 移除所有处理器
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
