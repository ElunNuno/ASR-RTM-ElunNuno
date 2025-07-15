"""
文件转录器抽象基类，定义文件转录的启动、停止、进度、结果等通用接口。
所有插件的文件转录器都应继承本类，实现自定义逻辑。
"""
from abc import ABC, abstractmethod
from typing import Any

class FileTranscriberBase(ABC):
    @abstractmethod
    def start_transcription(self, file_path: str, recognizer: Any) -> bool:
        """启动文件转录。"""
        pass

    @abstractmethod
    def stop_transcription(self) -> None:
        """停止转录。"""
        pass

    @abstractmethod
    def get_progress(self) -> float:
        """获取转录进度。"""
        pass

    @abstractmethod
    def get_result(self) -> str:
        """获取转录结果。"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """资源释放。"""
        pass
