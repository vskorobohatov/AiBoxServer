from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

from .transcriber import Transcriber
from .llm_service import LLMService

app = FastAPI(title="Voice2Text API")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

transcriber: Transcriber | None = None
llm_service = LLMService()


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

        return {
            "transcription": transcription,
            "llm_response": llm_response
        }

    finally:
        if file_path.exists():
            file_path.unlink()