import os
from pathlib import Path
import tomllib
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment or .env file")


def _load_defaults() -> tuple[str, float]:
    """Return (model, temperature) defaults from pyproject.toml."""
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    if not pyproject.exists():
        return "o3", 0.2
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        tool_cfg = data.get("tool", {}).get("md_batch_gpt", {})
        model = tool_cfg.get("model", "o3")
        temperature = float(tool_cfg.get("temperature", 0.2))
        return model, temperature
    except Exception:
        return "o3", 0.2


DEFAULT_MODEL, DEFAULT_TEMPERATURE = _load_defaults()
