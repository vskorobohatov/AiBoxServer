import os
import httpx

class TTSService:
    def __init__(self):
        base_url = os.getenv("TTS_URL", "http://coqui-tts:5002")
        self.tts_url = f"{base_url.rstrip('/')}/synthesize"

    async def synthesize(self, text: str) -> bytes:
        if not text.strip():
            raise ValueError("Cannot synthesize empty text.")

        payload = {"text": text}
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.tts_url, json=payload, headers=headers)

            if not response.headers.get("Content-Type", "").startswith("audio/"):
                print("TTS server error:", response.text)
                response.raise_for_status()

            return response.content