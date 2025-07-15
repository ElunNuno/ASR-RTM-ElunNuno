"""
字幕控件抽象基类，定义字幕显示、更新、样式设置等通用接口。
所有插件的字幕控件都应继承本类，实现自定义UI逻辑。
"""
from abc import ABC, abstractmethod
from typing import Dict

class SubtitleWidgetBase(ABC):
    @abstractmethod
    def update_text(self, text: str) -> None:
        """更新字幕内容。"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空字幕。"""
        pass

    @abstractmethod
    def set_style(self, style: Dict) -> None:
        """设置字幕样式。"""
        pass

    @abstractmethod
    def get_current_text(self) -> str:
        """获取当前字幕内容。"""
        pass
