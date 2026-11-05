from pathlib import Path
from typing import Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env file relative to project root
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama / LLM Configuration
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"
    OLLAMA_NUM_CTX: int = 8192
    OLLAMA_NUM_THREAD: int = 0
    OLLAMA_NUM_PREDICT: int = 4096

    # Context / Tokenizer Budget Configuration
    MAX_MODEL_TOKENS: int = 32768


    def __getitem__(self, item: str) -> Any:
        """Support dictionary-style access: config['KEY']."""
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"Setting '{item}' not found in configuration.")

    def __contains__(self, item: str) -> bool:
        """Support 'in' operator: 'KEY' in config."""
        return hasattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        """Support dictionary-style get method: config.get('KEY', default)."""
        return getattr(self, item, default)


# Singleton instances
settings = Settings()
config = settings


def get_settings() -> Settings:
    """Return the global application settings instance."""
    return settings