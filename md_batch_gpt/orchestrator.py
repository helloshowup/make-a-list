from __future__ import annotations

from pathlib import Path
from typing import List

from .file_io import iter_markdown_files, write_atomic
from .openai_client import send_prompt


def process_folder(folder: Path, prompt_paths: List[Path], model: str, temp: float) -> None:
    """Process Markdown files in *folder* using prompts from *prompt_paths*."""
    for md_file in iter_markdown_files(folder):
        text = md_file.read_text()
        for p in prompt_paths:
            prompt = Path(p).read_text()
            text = send_prompt(prompt, text, model, temp)
            write_atomic(md_file, text)
