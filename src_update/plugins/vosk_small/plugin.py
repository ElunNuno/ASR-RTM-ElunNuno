"""
Plugin entry for vosk_small ASR plugin.
Responsible for initializing and registering core components (structure only).
"""
from .audio.processor import AudioProcessor
from .audio.transcriber import FileTranscriber
from .ui.subtitle import SubtitleWidget

class VoskSmallPlugin:
    """Main plugin class for vosk_small (structure only)."""
    def __init__(self, event_bus):
        """Initialize plugin with event bus."""
        self.audio_processor = AudioProcessor()
        self.file_transcriber = FileTranscriber()
        self.subtitle_widget = SubtitleWidget()
        self.event_bus = event_bus

    def register(self):
        """Register plugin components and events."""
        # Register event handlers, components, etc.
        pass
