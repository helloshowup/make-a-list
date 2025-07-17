from pathlib import Path
from .runner import run_cli


def test_extraction_mode(tmp_path: Path):
    # create sample markdown files
    docs = tmp_path / "docs"
    docs.mkdir()
    files = [docs / "a.md", docs / "b.md"]
    for f in files:
        f.write_text(f"{f.stem.upper()}")

    # create prompts
    p1 = tmp_path / "p1.txt"
    p1.write_text("P1")
    p2 = tmp_path / "p2.txt"
    p2.write_text("P2")

    log_path = tmp_path / "log.txt"

    proc = run_cli(
        [
            str(docs),
            "--prompts",
            str(p1),
            "--prompts",
            str(p2),
            "--log-file",
            str(log_path),
            "--no-inplace",
        ],
        cwd=Path(__file__).resolve().parent.parent,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr

    # files should be unchanged
    assert [f.read_text() for f in files] == ["A", "B"]

    content = log_path.read_text()
    blocks = [b for b in content.split("\n---\n") if b.strip()]
    assert len(blocks) == 4

    expected = [
        ("=== a.md | prompt: p1.txt ===", "A[P1]"),
        ("=== a.md | prompt: p2.txt ===", "A[P1][P2]"),
        ("=== b.md | prompt: p1.txt ===", "B[P1]"),
        ("=== b.md | prompt: p2.txt ===", "B[P1][P2]"),
    ]

    for header, text in expected:
        matching = [b for b in blocks if header in b]
        assert matching, f"missing block for {header}"
        assert text in matching[0]

    # run again in inplace mode and ensure log stays empty
    proc = run_cli(
        [
            str(docs),
            "--prompts",
            str(p1),
            "--prompts",
            str(p2),
            "--log-file",
            str(log_path),
            "--inplace",
        ],
        cwd=Path(__file__).resolve().parent.parent,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [f.read_text() for f in files] == ["A[P1][P2]", "B[P1][P2]"]
    assert log_path.read_text() == content
