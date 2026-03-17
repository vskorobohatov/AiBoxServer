from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from TTS.api import TTS
import io
import soundfile as sf
import os

app = FastAPI(title="Coqui TTS REST API")

tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

VOICE_PATH = os.path.join(os.path.dirname(__file__), "voice.wav")

class SynthesizeRequest(BaseModel):
    text: str
    language: str = "ru"

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty text not allowed")

    # Проверим что файл есть
    if not os.path.exists(VOICE_PATH):
        raise HTTPException(status_code=500, detail="voice.wav not found")

    # ✅ Главная правка — используем speaker_wav
    wav = tts_model.tts(
        text=request.text,
        speaker_wav=VOICE_PATH,
        language=request.language
    )

    sr = tts_model.synthesizer.output_sample_rate

    buffer = io.BytesIO()
    sf.write(buffer, wav, sr, format="WAV")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="audio/wav")