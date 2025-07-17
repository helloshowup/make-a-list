import os
import subprocess
from pathlib import Path
from typing import Iterable


def run_cli(args: Iterable[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run the mdgpt CLI via poetry and return the completed process."""
    cmd = ["poetry", "run", "mdgpt", *args]
    env = os.environ.copy()
    env.update(
        {
            "OPENAI_API_KEY": "dummy",
            "PYTHONPATH": str(Path(__file__).parent / "stubs"),
        }
    )
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)
