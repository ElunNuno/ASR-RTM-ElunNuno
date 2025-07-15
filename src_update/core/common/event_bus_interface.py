"""
统一事件总线接口，定义事件的发布、订阅、取消订阅等通用方法。
所有跨模块、跨线程事件通信均应通过本接口实现。
"""
from abc import ABC, abstractmethod
from typing import Callable, Any

class EventBusInterface(ABC):
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[..., Any]) -> None:
        """订阅事件。"""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable[..., Any]) -> None:
        """取消订阅事件。"""
        pass

    @abstractmethod
    def publish(self, event_type: str, *args, **kwargs) -> None:
        """发布事件。"""
        pass
