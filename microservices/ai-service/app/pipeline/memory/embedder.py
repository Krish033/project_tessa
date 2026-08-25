import ollama
import asyncio


class Embedder:
    def __init__(self):
        self.client = ollama.Client()
        self.async_client = ollama.AsyncClient()
        self.model = "nomic-embed-text"



    def embed(self, text: str) -> list[float]:
        """Sync embed - runs the async version in event loop if available."""
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self._embed_sync, text)
                return future.result()

        except RuntimeError:
            return self._embed_sync(text)



    def _embed_sync(self, text: str) -> list[float]:
        response = self.client.embed(model=self.model, input=text)
        return response["embeddings"][0]


    async def aembed(self, text: str) -> list[float]:
        """Async embed - non-blocking."""
        response = await self.async_client.embed(model=self.model, input=text)
        return response["embeddings"][0]

