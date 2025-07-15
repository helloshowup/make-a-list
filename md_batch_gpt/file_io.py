from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
import os
from typing import Iterator


def read_text(path: Path) -> str:
    """Return the contents of *path* as UTF-8 text."""
    path = Path(path)
    return path.read_text(encoding="utf-8")


def iter_markdown_files(folder: Path) -> Iterator[Path]:
    """Yield paths to Markdown files under *folder* skipping dotfiles."""
    folder = Path(folder)
    for path in folder.rglob("*.md"):
        # Skip any file or directory that starts with a dot
        relative_parts = path.relative_to(folder).parts
        if any(part.startswith(".") for part in relative_parts):
            continue
        yield path


def write_atomic(path: Path, data: str) -> None:
    """Atomically write *data* to *path* using a temporary file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, path)
