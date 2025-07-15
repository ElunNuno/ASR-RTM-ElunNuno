import difflib
from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QScrollArea, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSlot, QTimer

class SubtitleLabel(QLabel):
    """A self-contained label for displaying subtitles with custom styling."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_styles()
        self.setText("Vosk ASR is ready...")

    def _apply_styles(self):
        font = QFont("Arial", 24)
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                background-color: rgba(0, 0, 0, 150);
                padding: 15px;
                border-radius: 10px;
                qproperty-alignment: AlignLeft;
            }}
        """)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class VoskSubtitleWidget(QScrollArea):
    """A self-contained subtitle widget for the Vosk plugin."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.transcript_text = []
        self.full_transcript_history = []
        self.current_partial_paragraph = ""

        self._setup_ui()

    def _setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
            QScrollBar:vertical { background: rgba(50, 50, 50, 150); width: 12px; }
            QScrollBar::handle:vertical { background: rgba(100, 100, 100, 200); border-radius: 6px; }
        """)
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.subtitle_label = SubtitleLabel(container)
        container_layout.addWidget(self.subtitle_label)
        self.setWidget(container)

    @pyqtSlot(str)
    def update_text(self, text: str):
        is_partial = text.startswith("PARTIAL:")
        if is_partial:
            partial_text = text[8:]
            self.current_partial_paragraph = self._format_text(partial_text)
            display_list = self.transcript_text[-9:] + ([self.current_partial_paragraph] if self.current_partial_paragraph else [])
            self.subtitle_label.setText('\n'.join(display_list))
        else:
            formatted_text = self._format_text(text)
            if formatted_text and (not self.transcript_text or not self._is_similar(formatted_text, self.transcript_text[-1])):
                self.transcript_text.append(formatted_text)
                self.full_transcript_history.append(formatted_text)
                if len(self.transcript_text) > 10:
                    self.transcript_text.pop(0)
            self.subtitle_label.setText('\n'.join(self.transcript_text))
            self.current_partial_paragraph = ""
        
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _format_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        if text and text[-1] not in '.?!':
            text += '.'
        return text

    def _is_similar(self, text1: str, text2: str) -> bool:
        if not text1 or not text2:
            return False
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio() > 0.8

    def _scroll_to_bottom(self):
        scroll_bar = self.verticalScrollBar()
        if scroll_bar:
            scroll_bar.setValue(scroll_bar.maximum())

    def get_full_transcript(self) -> str:
        return '\n'.join(self.full_transcript_history)