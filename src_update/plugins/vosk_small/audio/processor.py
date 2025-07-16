"""
AudioProcessor for vosk_small plugin.
Implements audio processing logic specific to vosk_small, inheriting from AudioProcessorBase.
"""

from src_update.core.common.audio_processor_base import AudioProcessorBase
from src_update.core.common.events import EventBus, Event


class AudioProcessor(AudioProcessorBase):
    """Audio processor for vosk_small plugin (event-driven)."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._running = False
        # 订阅事件
        self.event_bus.subscribe("start_transcription", self.on_start_transcription)
        self.event_bus.subscribe("stop_transcription", self.on_stop_transcription)

    def on_start_transcription(self, event: Event):
        """Event-driven audio stream transcription logic."""
        import numpy as np
        import soundcard as sc
        import json

        data = event.data or {}
        device_id = data.get("device_id")
        recognizer = data.get("recognizer")
        sample_rate = data.get("sample_rate", 16000)
        buffer_size = data.get("buffer_size", 4000)

        self.event_bus.publish(Event("status_update", {"message": "Audio stream transcription started"}))

        try:
            if not device_id:
                self.event_bus.publish(Event("error_occurred", {"message": "Audio device not specified"}))
                return

            mic = sc.get_microphone(id=str(device_id), include_loopback=True)
            with mic.recorder(samplerate=sample_rate) as recorder:
                self._running = True
                while self._running:
                    data = recorder.record(numframes=buffer_size)
                    if isinstance(data, np.ndarray) and data.ndim > 1 and data.shape[1] > 1:
                        data = np.mean(data, axis=1)
                    if np.max(np.abs(data)) < 0.01:
                        continue
                    if recognizer:
                        data_bytes = (data * 32767).astype(np.int16).tobytes()
                        if recognizer.AcceptWaveform(data_bytes):
                            result = recognizer.Result()
                            try:
                                result_json = json.loads(result)
                                text = result_json.get("text", "").strip()
                            except Exception:
                                text = result
                            if text:
                                self.event_bus.publish(Event("asr_result", {"text": text}))
                        else:
                            partial = recognizer.PartialResult()
                            try:
                                partial_json = json.loads(partial)
                                partial_text = partial_json.get("partial", "").strip()
                            except Exception:
                                partial_text = partial
                            if partial_text:
                                self.event_bus.publish(Event("asr_result", {"text": partial_text}))
        except Exception as e:
            self.event_bus.publish(Event("error_occurred", {"message": f"Audio stream transcription error: {e}"}))

    def on_stop_transcription(self, event: Event):
        """Stop audio stream transcription."""
        self._running = False
        self.event_bus.publish(Event("status_update", {"message": "Audio stream transcription stopped"}))

    def initialize(self) -> bool:
        """初始化音频处理器"""
        return True

    def start_stream(self):
        """开始音频流处理"""
        self.event_bus.publish(Event("status_update", {"message": "Audio stream started"}))

    def stop_stream(self):
        """停止音频流处理"""
        self.event_bus.publish(Event("status_update", {"message": "Audio stream stopped"}))

    def process_audio(self, data):
        """处理音频数据并更新进度"""
        import numpy as np
        if isinstance(data, np.ndarray) and data.ndim > 1 and data.shape[1] > 1:
            data = np.mean(data, axis=1)
        if np.max(np.abs(data)) < 0.01:
            return None
        return data

    def cleanup(self):
        """清理资源"""
        self.event_bus.publish(Event("status_update", {"message": "Audio processor cleaned up"}))

    def debug_audio_stream(self):
        """调试音频流采集和处理逻辑"""
        import numpy as np
        import soundcard as sc

        self.event_bus.publish(Event("status_update", {"message": "开始调试音频流采集"}))
        try:
            sample_rate = 16000
            buffer_size = 4000
            mic = sc.default_microphone()
            with mic.recorder(samplerate=sample_rate) as recorder:
                for _ in range(10):
                    data = recorder.record(numframes=buffer_size)
                    if isinstance(data, np.ndarray) and data.ndim > 1 and data.shape[1] > 1:
                        data = np.mean(data, axis=1)
                    self.event_bus.publish(Event("debug_audio_data", {"data": data.tolist()}))
        except Exception as e:
            self.event_bus.publish(Event("error_occurred", {"message": f"音频流调试异常: {e}"}))


if __name__ == "__main__":
    import vosk
    import soundcard as sc

    def print_asr_result(event: Event):
        """打印转录结果"""
        text = event.data.get("text", "")
        print(f"转录结果: {text}")

    # 初始化事件总线
    event_bus = EventBus()
    event_bus.subscribe("asr_result", print_asr_result)  # 订阅转录结果事件

    # 初始化识别器
    model_path = "path/to/vosk/model"  # 替换为实际模型路径
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)

    # 获取默认麦克风设备
    microphones = sc.all_microphones(include_loopback=True)
    if not microphones:
        print("未找到支持环回录音的麦克风设备")
        exit(1)
    default_mic = microphones[0]  # 使用第一个麦克风设备
    device_id = default_mic.name

    # 初始化音频处理器并开始转录
    processor = AudioProcessor(event_bus)
    processor.on_start_transcription(Event("start_transcription", {
        "device_id": device_id,
        "recognizer": recognizer
    }))
