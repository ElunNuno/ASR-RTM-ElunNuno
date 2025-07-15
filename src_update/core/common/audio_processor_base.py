"""
音频处理器抽象基类，定义音频采集、预处理、流式推送等通用接口。
所有插件的音频处理器都应继承本类，实现自定义逻辑。
"""
from abc import ABC, abstractmethod
from typing import Any

class AudioProcessorBase(ABC):
    @abstractmethod
    def initialize(self) -> bool:
        """初始化音频设备和资源。"""
        pass

    @abstractmethod
    def start_stream(self) -> None:
        """开始音频流采集。"""
        pass

    @abstractmethod
    def stop_stream(self) -> None:
        """停止音频流采集。"""
        pass

    @abstractmethod
    def process_audio(self, data: bytes) -> Any:
        """处理音频数据。"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """资源释放。"""
        pass
