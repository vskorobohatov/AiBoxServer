FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 git curl build-essential \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir \
    torch==2.4.0+cpu torchaudio==2.4.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir \
    transformers==4.38.2 \
    TTS==0.22.0 \
    fastapi uvicorn

COPY app/ /app/

COPY app/voice.wav /app/voice.wav

EXPOSE 5002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5002"]