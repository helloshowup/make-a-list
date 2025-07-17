import importlib
from pathlib import Path

from typer.testing import CliRunner


def import_cli():
    if "md_batch_gpt.cli" in importlib.sys.modules:
        del importlib.sys.modules["md_batch_gpt.cli"]
    return importlib.import_module("md_batch_gpt.cli")


def test_run_dry_run(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

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


def test_run_max_tokens(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    cli = import_cli()

    captured = {}

    def fake_process_folder(
        folder: Path,
        prompt_paths: list[Path],
        model: str,
        max_tokens: int | None = None,
        regex_json: Path | None = None,
        dry_run: bool = False,
        verbose: bool = False,
        inplace: bool = False,
        log_file: Path | None = None,
    ) -> None:
        captured["max_tokens"] = max_tokens

    monkeypatch.setattr(cli, "process_folder", fake_process_folder)

    (tmp_path / "a.md").write_text("A")

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            str(tmp_path),
            "--prompts",
            "tests/data/p1.txt",
            "--max-tokens",
            "123",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert captured["max_tokens"] == 123


def test_run_auto_prompt_dir(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    cli = import_cli()
    monkeypatch.setattr("md_batch_gpt.orchestrator.send_prompt", lambda *a, **k: "")

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("A")

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    for i in range(1, 4):
        (prompts_dir / f"{i:02d}.txt").write_text(f"p{i}")

    dummy_cli_path = tmp_path / "pkg" / "cli.py"
    dummy_cli_path.parent.mkdir()
    dummy_cli_path.write_text("")
    monkeypatch.setattr(cli, "__file__", str(dummy_cli_path))

    runner = CliRunner()
    result = runner.invoke(cli.app, [str(docs), "--verbose"])

    assert result.exit_code == 0, result.stdout
    assert "pass 3/3" in result.stdout


def test_run_regex_json(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    cli = import_cli()

    captured = {}

    def fake_process_folder(
        folder: Path,
        prompt_paths: list[Path],
        model: str,
        max_tokens: int | None = None,
        regex_json: Path | None = None,
        dry_run: bool = False,
        verbose: bool = False,
        inplace: bool = False,
        log_file: Path | None = None,
    ) -> None:
        captured["regex_json"] = regex_json

    monkeypatch.setattr(cli, "process_folder", fake_process_folder)

    (tmp_path / "a.md").write_text("A")
    regex_path = tmp_path / "regex.json"
    regex_path.write_text("{}")

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            str(tmp_path),
            "--prompts",
            "tests/data/p1.txt",
            "--regex-json",
            str(regex_path),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert captured["regex_json"] == regex_path


def test_end_to_end_modes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    cli = import_cli()

    monkeypatch.setattr(
        "md_batch_gpt.orchestrator.send_prompt",
        lambda prompt, content, model, max_tokens=None: f"{content}[{prompt.strip()}]",
    )

    p1 = tmp_path / "p1.txt"
    p1.write_text("P1")
    p2 = tmp_path / "p2.txt"
    p2.write_text("P2")

    docs = tmp_path / "docs"
    docs.mkdir()
    f1 = docs / "a.md"
    f1.write_text("A")
    f2 = docs / "b.md"
    f2.write_text("B")

    log_file = tmp_path / "extracted.txt"

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            str(docs),
            "--prompts",
            str(p1),
            "--prompts",
            str(p2),
            "--log-file",
            str(log_file),
            "--no-inplace",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert f1.read_text() == "A"
    assert f2.read_text() == "B"
    log_content = log_file.read_text()
    assert "=== a.md | prompt: p1.txt ===" in log_content
    assert "A[P1]" in log_content
    assert "A[P1][P2]" in log_content
    assert "=== b.md | prompt: p2.txt ===" in log_content
    assert "B[P1][P2]" in log_content

    log_file.write_text("")
    result = runner.invoke(
        cli.app,
        [
            str(docs),
            "--prompts",
            str(p1),
            "--prompts",
            str(p2),
            "--log-file",
            str(log_file),
            "--inplace",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert f1.read_text() == "A[P1][P2]"
    assert f2.read_text() == "B[P1][P2]"
    assert log_file.read_text() == ""


def test_unwritable_log_file(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    cli = import_cli()
    monkeypatch.setattr(
        "md_batch_gpt.orchestrator.send_prompt",
        lambda prompt, content, model, max_tokens=None: content,
    )

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "a.md").write_text("A")

    log_dir = tmp_path / "log"
    log_dir.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            str(docs),
            "--prompts",
            "tests/data/p1.txt",
            "--log-file",
            str(log_dir),
            "--no-inplace",
        ],
    )

    assert result.exit_code == 1
    assert "Cannot write to log file" in result.stderr


def test_log_file_resolution(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    cli = import_cli()

    captured = {}

    def fake_process_folder(
        folder: Path,
        prompt_paths: list[Path],
        model: str,
        max_tokens: int | None = None,
        regex_json: Path | None = None,
        dry_run: bool = False,
        verbose: bool = False,
        inplace: bool = False,
        log_file: Path | None = None,
    ) -> None:
        captured["log_file"] = log_file

    monkeypatch.setattr(cli, "process_folder", fake_process_folder)

    (tmp_path / "a.md").write_text("A")

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            str(tmp_path),
            "--prompts",
            "tests/data/p1.txt",
            "--log-file",
            "out.txt",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert captured["log_file"] == Path.cwd() / Path("out.txt")
