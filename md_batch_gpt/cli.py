from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import typer

from .orchestrator import process_folder


def validate_prompts(_: typer.Context, value: Tuple[Path, ...]) -> List[Path]:
    """Return *value* if all paths exist, otherwise raise BadParameter."""
    for p in value:
        if not p.exists():
            raise typer.BadParameter(f"File not found: {p}")
    return list(value)


app = typer.Typer()


@app.command()
def run(
    folder: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    prompts: List[Path] = typer.Option(
        ...,
        "--prompts",
        help="Space-separated list of prompt files",
        callback=validate_prompts,
    ),
    model: str = typer.Option("o3", "--model", help="OpenAI model to use"),
    temp: float = typer.Option(0.2, "--temp", help="Sampling temperature"),
    max_tokens: int | None = typer.Option(
        None, "--max-tokens", help="Max tokens for completion"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="List files to be processed without sending prompts",
    ),
) -> None:
    """Run the batch processor on *folder* using *prompts*."""
    if verbose:
        typer.echo(f"Folder: {folder}")
        typer.echo(f"Prompts: {', '.join(str(p) for p in prompts)}")
        typer.echo(f"Model: {model} Temperature: {temp} Max tokens: {max_tokens}")
    process_folder(
        folder,
        list(prompts),
        model=model,
        temp=temp,
        max_tokens=max_tokens,
        dry_run=dry_run,
        verbose=verbose,
    )
    if verbose:
        typer.echo("Done")


if __name__ == "__main__":  # pragma: no cover
    app()
