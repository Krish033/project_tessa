import ollama
from typing import Optional, List
from app.core.config import config


class Embedder:
    """Async text embedder using Ollama."""

    def __init__(self, model: str = "nomic-embed-text"):
        self.client = ollama.AsyncClient(host=config.OLLAMA_URL)
        self.model = model

    async def embed(self, text: str) -> Optional[List[float]]:
        """Generate text embedding vector asynchronously."""
        if not text or not str(text).strip():
            return None
        try:
            response = await self.client.embed(model=self.model, input=str(text).strip())
            return response["embeddings"][0]
        except Exception:
            return None
