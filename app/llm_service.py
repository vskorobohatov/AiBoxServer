import httpx
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/generate")
MODEL_NAME = "llama3.2:1b"

class LLMService:
    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                }
            )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")