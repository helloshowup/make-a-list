from __future__ import annotations

from pathlib import Path
from typing import List

import typer

from .orchestrator import process_folder

app = typer.Typer()


@app.command()
def run(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    prompts: List[Path] = typer.Option(
        ..., "--prompts", help="Space-separated list of prompt files", exists=True
    ),
    model: str = typer.Option("o3", "--model", help="OpenAI model to use"),
    temp: float = typer.Option(0.2, "--temp", help="Sampling temperature"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Run the batch processor on *folder* using *prompts*."""
    if verbose:
        typer.echo(f"Folder: {folder}")
        typer.echo(f"Prompts: {', '.join(str(p) for p in prompts)}")
        typer.echo(f"Model: {model} Temperature: {temp}")
    process_folder(folder, list(prompts), model=model, temp=temp)
    if verbose:
        typer.echo("Done")


if __name__ == "__main__":  # pragma: no cover
    app()
