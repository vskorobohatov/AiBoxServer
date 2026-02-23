from faster_whisper import WhisperModel

class Transcriber:
    def __init__(self, model_size: str = "base"):
        self.model = WhisperModel(model_size, compute_type="int8")

    def transcribe(self, file_path: str) -> str:
        segments, _ = self.model.transcribe(file_path)
        return " ".join(segment.text for segment in segments)