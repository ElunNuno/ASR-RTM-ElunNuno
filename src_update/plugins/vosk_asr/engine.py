import os
import json
import numpy as np
from typing import Optional, Union
from vosk import Model, KaldiRecognizer

class VoskASR:
    """VOSK ASR 引擎封装类, 专为插件化设计"""

    def __init__(self, model_path: str):
        """初始化 VOSK ASR 引擎

        Args:
            model_path: VOSK 模型路径
        """
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.sample_rate = 16000
        self.setup()

    def setup(self):
        """Loads the Vosk model."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Vosk model path does not exist: {self.model_path}")
        try:
            self.model = Model(self.model_path)
        except Exception as e:
            print(f"Failed to load Vosk model from {self.model_path}: {e}")
            # Optionally, re-raise the exception or handle it as needed
            raise

    def transcribe(self, audio_data: Union[bytes, np.ndarray]) -> Optional[str]:
        """转录音频数据"""
        if not self.recognizer:
            return None

        try:
            if isinstance(audio_data, np.ndarray):
                audio_data = (audio_data * 32767).astype(np.int16).tobytes()

            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                return result.get("text", "")
            else:
                partial_result = json.loads(self.recognizer.PartialResult())
                return partial_result.get("partial", "")

        except Exception as e:
            print(f"Error in VOSK transcription: {str(e)}")
            return None

    def reset(self) -> None:
        """重置识别器状态"""
        if self.recognizer:
            self.recognizer.Reset()

    def get_final_result(self) -> Optional[str]:
        """获取最终识别结果"""
        try:
            if self.recognizer:
                final_result = self.recognizer.FinalResult()
                result = json.loads(final_result)
                text = result.get("text", "").strip()
                if text:
                    return text[0].upper() + text[1:] + '.' if text[-1] not in '.?!' else ''
            return None
        except Exception as e:
            print(f"Error getting VOSK final result: {str(e)}")
            return None

    def transcribe_file(self, file_path: str) -> Optional[str]:
        """转录音频文件"""
        import wave

        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None

            if not file_path.lower().endswith('.wav'):
                print(f"File is not a WAV file: {file_path}")
                # Here you could add conversion logic if needed
                return None

            with wave.open(file_path, 'rb') as wf:
                if wf.getframerate() != self.sample_rate:
                    print(f"Sample rate mismatch: {wf.getframerate()} != {self.sample_rate}")
                    # Here you could add resampling logic if needed
                    return None

                recognizer = KaldiRecognizer(self.model, self.sample_rate)
                recognizer.SetWords(True)

                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        results.append(result['text'])
                
                final_result = json.loads(recognizer.FinalResult())
                results.append(final_result['text'])

                full_text = ' '.join(filter(None, results)).strip()
                return full_text.capitalize() + '.' if full_text else ''

        except Exception as e:
            print(f"Error transcribing file with VOSK: {str(e)}")
            return None