"""
COM处理模块
负责Windows COM组件的初始化和管理
"""
import os
import pythoncom
import threading
from typing import Optional

# 设置环境变量，防止COM初始化冲突
os.environ["PYTHONCOM_INITIALIZE"] = "0"

class ComHandler:
    """COM处理类"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized_threads = set()
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(ComHandler, cls).__new__(cls)
        return cls._instance
    
    def initialize_com(self, threading_model: Optional[int] = None) -> bool:
        """
        初始化COM
        
        Args:
            threading_model: 保留参数，已废弃，强制使用STA模式
                
        Returns:
            bool: 初始化是否成功
        """
        import pythoncom
        import threading
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id in self._initialized_threads:
                print(f"线程 {thread_id} 已初始化COM")
                return True
        try:
            # 强制所有线程都用STA（单线程单元）模式
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            print("COM初始化成功（单线程模式）")
            with self._lock:
                self._initialized_threads.add(thread_id)
            return True
        except Exception as e:
            error_msg = str(e)
            if "already initialized" in error_msg or "cannot change thread mode" in error_msg:
                print("COM已经初始化，继续执行")
                with self._lock:
                    self._initialized_threads.add(thread_id)
                return True
            else:
                print(f"COM初始化错误: {e}")
                return False
    
    def uninitialize_com(self) -> bool:
        """
        释放COM
        
        Returns:
            bool: 释放是否成功
        """
        # 获取当前线程ID
        thread_id = threading.get_ident()
        
        try:
            # 检查当前线程是否已初始化
            with self._lock:
                if thread_id not in self._initialized_threads:
                    print(f"线程 {thread_id} 未初始化COM，无需释放")
                    return True
            
            # 释放COM
            pythoncom.CoUninitialize()
            print("COM已释放")
            
            # 移除已初始化的线程记录
            with self._lock:
                self._initialized_threads.remove(thread_id)
            
            return True
            
        except Exception as e:
            print(f"COM释放错误: {e}")
            return False

# 创建全局实例
com_handler = ComHandler()
