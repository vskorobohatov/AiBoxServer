FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 git curl build-essential \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch==2.1.0+cpu torchaudio==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir TTS[all] fastapi uvicorn

COPY app ./app

EXPOSE 5002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]