"""
测试事件系统
"""
import pytest
from typing import List

from src_update.core.common.events import EventBus, Event

class TestEventSystem:
    """事件系统测试类"""
    
    @pytest.fixture
    def event_bus(self):
        """创建事件总线实例"""
        bus = EventBus()
        bus.clear()  # 清除单例可能保留的订阅
        return bus
    
    @pytest.fixture
    def event_log(self):
        """创建事件日志列表"""
        return []
    
    def test_subscribe_and_publish(self, event_bus, event_log):
        """测试订阅和发布事件"""
        def handler(event: Event):
            event_log.append(event)
        
        # 订阅事件
        event_bus.subscribe("test_event", handler)
        
        # 发布事件
        test_event = Event("test_event", "test_data")
        event_bus.publish(test_event)
        
        # 验证事件处理
        assert len(event_log) == 1
        assert event_log[0].name == "test_event"
        assert event_log[0].data == "test_data"
    
    def test_multiple_subscribers(self, event_bus):
        """测试多个订阅者"""
        received_events: List[str] = []
        
        def handler1(event: Event):
            received_events.append(f"handler1_{event.data}")
            
        def handler2(event: Event):
            received_events.append(f"handler2_{event.data}")
        
        # 订阅事件
        event_bus.subscribe("test_event", handler1)
        event_bus.subscribe("test_event", handler2)
        
        # 发布事件
        event_bus.publish(Event("test_event", "test_data"))
        
        # 验证所有处理器都收到事件
        assert len(received_events) == 2
        assert "handler1_test_data" in received_events
        assert "handler2_test_data" in received_events
    
    def test_unsubscribe(self, event_bus, event_log):
        """测试取消订阅"""
        def handler(event: Event):
            event_log.append(event)
        
        # 订阅事件
        event_bus.subscribe("test_event", handler)
        
        # 发布第一个事件
        event_bus.publish(Event("test_event", "data1"))
        assert len(event_log) == 1
        
        # 取消订阅
        event_bus.unsubscribe("test_event", handler)
        
        # 发布第二个事件
        event_bus.publish(Event("test_event", "data2"))
        assert len(event_log) == 1  # 日志不应增加
    
    def test_multiple_event_types(self, event_bus):
        """测试多个事件类型"""
        received_events: List[str] = []
        
        def handler1(event: Event):
            received_events.append(f"event1_{event.data}")
            
        def handler2(event: Event):
            received_events.append(f"event2_{event.data}")
        
        # 订阅不同事件
        event_bus.subscribe("event1", handler1)
        event_bus.subscribe("event2", handler2)
        
        # 发布事件
        event_bus.publish(Event("event1", "data1"))
        event_bus.publish(Event("event2", "data2"))
        
        # 验证事件处理
        assert len(received_events) == 2
        assert "event1_data1" in received_events
        assert "event2_data2" in received_events
    
    def test_error_handling(self, event_bus):
        """测试错误处理"""
        def failing_handler(event: Event):
            raise Exception("Test error")
            
        def normal_handler(event: Event):
            pass  # 这个处理器应该被正常调用
        
        # 订阅事件
        event_bus.subscribe("test_event", failing_handler)
        event_bus.subscribe("test_event", normal_handler)
        
        # 发布事件不应抛出异常
        event_bus.publish(Event("test_event", "data"))
    
    def test_singleton_behavior(self, event_bus, event_log):
        """测试单例行为"""
        def handler(event: Event):
            event_log.append(event)
        
        # 在第一个实例上订阅
        event_bus.subscribe("test_event", handler)
        
        # 创建新实例
        another_bus = EventBus()
        
        # 通过新实例发布事件
        another_bus.publish(Event("test_event", "test_data"))
        
        # 验证事件被处理
        assert len(event_log) == 1
