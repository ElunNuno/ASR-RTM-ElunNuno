"""
AudioProcessor for vosk_small plugin.
Implements audio processing logic specific to vosk_small, inheriting from AudioProcessorBase.
"""
from src_update.core.common.audio_processor_base import AudioProcessorBase


class AudioProcessor(AudioProcessorBase):
    """Audio processor for vosk_small plugin (event-driven)."""
    def __init__(self, event_bus):
        self.event_bus = event_bus
        # 订阅事件
        self.event_bus.subscribe("start_transcription", self.on_start_transcription)
        self.event_bus.subscribe("stop_transcription", self.on_stop_transcription)

    def on_start_transcription(self, file_path=None, recognizer=None, **kwargs):
        """
        事件驱动的音频流采集与识别主流程（移植自 src/core/audio/audio_processor.py，已用事件总线解耦）
        """
        import numpy as np
        import soundcard as sc
        import time
        self.event_bus.publish("status_update", msg="音频流转录已开始")
        try:
            # 假设已通过事件或配置选定设备
            device_id = kwargs.get('device_id')
            sample_rate = kwargs.get('sample_rate', 16000)
            buffer_size = kwargs.get('buffer_size', 4000)
            if not device_id:
                self.event_bus.publish("error_occurred", msg="未指定音频设备")
                return
            mic = sc.get_microphone(id=str(device_id), include_loopback=True)
            with mic.recorder(samplerate=sample_rate) as recorder:
                self._running = True
                while self._running:
                    data = recorder.record(numframes=buffer_size)
                    # 转为单声道
                    if data.shape[1] > 1:
                        data = np.mean(data, axis=1)
                    # 静音检测
                    if np.max(np.abs(data)) < 0.01:
                        continue
                    # 送入 vosk 识别器
                    if recognizer is not None:
                        data_bytes = (data * 32767).astype(np.int16).tobytes()
                        accept_result = recognizer.AcceptWaveform(data_bytes)
                        if accept_result:
                            result = recognizer.Result()
                            # 解析 JSON，提取 text 字段
                            import json
                            try:
                                result_json = json.loads(result)
                                text = result_json.get('text', '').strip()
                            except Exception:
                                text = result
                            if text:
                                self.event_bus.publish("asr_result", text=text)
                        else:
                            partial = recognizer.PartialResult()
                            try:
                                partial_json = json.loads(partial)
                                partial_text = partial_json.get('partial', '').strip()
                            except Exception:
                                partial_text = partial
                            if partial_text:
                                self.event_bus.publish("asr_result", text=partial_text)
        except Exception as e:
            self.event_bus.publish("error_occurred", msg=f"音频流转录异常: {e}")



    def on_stop_transcription(self, **kwargs):
        # 停止音频流采集，释放资源
        self._running = False
        self.event_bus.publish("status_update", msg="音频流转录已停止")

    def initialize(self) -> bool:
        pass

    def start_stream(self):
        pass

    def stop_stream(self):
        pass

    def process_audio(self, data: bytes):
        pass

    def cleanup(self):
        pass
