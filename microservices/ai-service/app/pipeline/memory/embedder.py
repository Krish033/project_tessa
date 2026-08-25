import ollama


class Embedder:
    """Async text embedder using Ollama."""

    def __init__(self, model: str = "nomic-embed-text"):
        self.client = ollama.AsyncClient()
        self.model = model

    async def embed(self, text: str) -> list[float]:
        """Generate text embedding vector asynchronously."""
        response = await self.client.embed(model=self.model, input=text)
        return response["embeddings"][0]
