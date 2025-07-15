import importlib
from pathlib import Path

import pytest


def import_config():
    if "md_batch_gpt.config" in importlib.sys.modules:
        del importlib.sys.modules["md_batch_gpt.config"]
    return importlib.import_module("md_batch_gpt.config")


def test_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    config = import_config()
    assert config.OPENAI_API_KEY == "from-env"


def test_api_key_from_dotenv(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = Path(".env")
    env_file.write_text("OPENAI_API_KEY=from-file")
    try:
        config = import_config()
        assert config.OPENAI_API_KEY == "from-file"
    finally:
        env_file.unlink()


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = Path(".env")
    if env_file.exists():
        env_file.unlink()
    with pytest.raises(RuntimeError):
        import_config()
