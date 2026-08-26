import ollama
from app.core.config import config

OPTIONS = {
    "temperature": 0.0,
    "num_ctx": config.OLLAMA_NUM_CTX,
    "num_thread": config.OLLAMA_NUM_THREAD,
    "num_predict": config.OLLAMA_NUM_PREDICT,
}


class QwenLLM:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or config.OLLAMA_MODEL
        self.client = ollama.Client(host=config.OLLAMA_URL)

    def run(self, messages: list) -> str:
        """Run LLM response synchronously."""
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            options=OPTIONS,
            think=False,
            keep_alive=-1,
        )
        return response["message"]["content"].strip()
