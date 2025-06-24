"""
事件系统模块
提供基于发布-订阅模式的事件处理机制
"""
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """事件类"""
    name: str
    data: Any = None

class EventBus:
    """事件总线类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not EventBus._initialized:
            self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
            EventBus._initialized = True
    
    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        """订阅事件
        
        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
            
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)
            logger.debug(f"订阅事件: {event_name}")
    
    def unsubscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        """取消订阅事件
        
        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name in self._subscribers and handler in self._subscribers[event_name]:
            self._subscribers[event_name].remove(handler)
            logger.debug(f"取消订阅事件: {event_name}")
            
            if not self._subscribers[event_name]:
                del self._subscribers[event_name]
    
    def publish(self, event: Event) -> None:
        """发布事件
        
        Args:
            event: 事件实例
        """
        if event.name in self._subscribers:
            logger.debug(f"发布事件: {event.name}")
            for handler in self._subscribers[event.name]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"处理事件失败: {event.name}, 错误: {e}")
    
    def clear(self) -> None:
        """清除所有订阅"""
        self._subscribers.clear()
        logger.debug("清除所有事件订阅")

# 创建全局事件总线实例
event_bus = EventBus()
