import pytest
from app.core.config import Settings, settings, config, get_settings


def test_config_attributes():
    assert hasattr(config, "DATABASE_URL")
    assert hasattr(config, "POSTGRES_USER")
    assert hasattr(config, "POSTGRES_PASSWORD")
    assert hasattr(config, "POSTGRES_HOST")
    assert hasattr(config, "POSTGRES_PORT")
    assert hasattr(config, "POSTGRES_DB")
    assert hasattr(config, "OLLAMA_URL")
    assert hasattr(config, "OLLAMA_MODEL")
    assert hasattr(config, "OLLAMA_NUM_CTX")
    assert hasattr(config, "OLLAMA_NUM_THREAD")
    assert hasattr(config, "OLLAMA_NUM_PREDICT")
    assert hasattr(config, "MAX_MODEL_TOKENS")


def test_config_dict_access():
    assert config["OLLAMA_URL"] == config.OLLAMA_URL
    assert config["OLLAMA_MODEL"] == config.OLLAMA_MODEL
    assert config.get("OLLAMA_URL") == config.OLLAMA_URL
    assert config.get("NON_EXISTENT_KEY", "fallback") == "fallback"
    assert "OLLAMA_URL" in config

    with pytest.raises(KeyError):
        _ = config["NON_EXISTENT_KEY_12345"]


def test_database_url_property():
    assert config.database_url.startswith("postgresql://")
    assert f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}" in config.database_url


def test_settings_singleton_and_factory():
    assert settings is config
    assert get_settings() is settings


def test_settings_custom_values():
    custom = Settings(
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_HOST="127.0.0.1",
        POSTGRES_PORT=5433,
        POSTGRES_DB="test_db",
        OLLAMA_URL="http://127.0.0.1:11435",
        OLLAMA_MODEL="qwen2.5:3b",
        OLLAMA_NUM_CTX=4096,
        OLLAMA_NUM_THREAD=4,
        OLLAMA_NUM_PREDICT=2048,
        MAX_MODEL_TOKENS=16384,
    )
    assert custom.POSTGRES_USER == "test_user"
    assert custom.POSTGRES_PORT == 5433
    assert custom.database_url == "postgresql://test_user:test_password@127.0.0.1:5433/test_db"
    assert custom["OLLAMA_MODEL"] == "qwen2.5:3b"
    assert custom.MAX_MODEL_TOKENS == 16384
