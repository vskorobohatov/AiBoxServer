from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path
import uuid
import io

from .transcriber import Transcriber
from .llm_service import LLMService
from .tts_service import TTSService

app = FastAPI(title="Voice2Text API")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

transcriber: Transcriber | None = None
llm_service = LLMService()
tts_service = TTSService()


@app.on_event("startup")
def load_model():
    global transcriber
    transcriber = Transcriber(model_size="base")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    file_extension = Path(file.filename).suffix
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / safe_filename

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # 1️⃣ Whisper
        transcription = transcriber.transcribe(str(file_path))

        # 2️⃣ Ollama
        llm_response = await llm_service.generate(transcription)

        # 3️⃣ Coqui TTS
        if not llm_response or not llm_response.strip():
            llm_response = "Sorry, I could not generate a response."

        audio_bytes = await tts_service.synthesize(llm_response)

        # 4️⃣ Return WAV file
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=response.wav"
            }
        )

    finally:
        if file_path.exists():
            file_path.unlink()