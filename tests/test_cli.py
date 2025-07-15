import importlib
from pathlib import Path

import typer
from typer.testing import CliRunner


def import_cli():
    if "md_batch_gpt.cli" in importlib.sys.modules:
        del importlib.sys.modules["md_batch_gpt.cli"]
    return importlib.import_module("md_batch_gpt.cli")


def test_run_dry_run(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    original_option = typer.Option

    def fake_option(*args, **kwargs):
        kwargs.pop("nargs", None)
        return original_option(*args, **kwargs)

    monkeypatch.setattr(typer, "Option", fake_option)

    cli = import_cli()
    monkeypatch.setattr("md_batch_gpt.orchestrator.send_prompt", lambda *a, **k: "")

    (tmp_path / "a.md").write_text("A")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.md").write_text("B")

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            str(tmp_path),
            "--dry-run",
            "--prompts",
            "tests/data/p1.txt",
            "--prompts",
            "tests/data/p2.txt",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "a.md" in result.stdout
    assert "b.md" in result.stdout
    assert "Prompt count: 2" in result.stdout
