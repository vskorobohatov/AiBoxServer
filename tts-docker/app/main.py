from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from TTS.api import TTS
import io
import soundfile as sf

app = FastAPI(title="Coqui TTS REST API")

tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

class SynthesizeRequest(BaseModel):
    text: str
    speaker: str = None

@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty text not allowed")

    kwargs = {}
    if hasattr(tts_model, "speakers") and tts_model.speakers:
        if request.speaker is None:
            kwargs["speaker"] = tts_model.speakers[0]
        else:
            if request.speaker not in tts_model.speakers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Speaker must be one of {tts_model.speakers}"
                )
            kwargs["speaker"] = request.speaker

    wav = tts_model.tts(request.text, **kwargs)
    sr = tts_model.synthesizer.output_sample_rate

    buffer = io.BytesIO()
    sf.write(buffer, wav, sr, format="WAV")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="audio/wav")