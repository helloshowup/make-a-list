from pathlib import Path

from md_batch_gpt.file_io import iter_markdown_files, write_atomic


def test_iter_markdown_files(tmp_path: Path):
    (tmp_path / "a.md").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / ".hidden.md").write_text("hidden")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.md").write_text("c")
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "d.md").write_text("d")

    results = sorted(p.relative_to(tmp_path) for p in iter_markdown_files(tmp_path))
    assert results == [Path("a.md"), Path("sub/c.md")]


def test_write_atomic(tmp_path: Path):
    target = tmp_path / "file.txt"
    write_atomic(target, "first")
    assert target.read_text() == "first"
    write_atomic(target, "second")
    assert target.read_text() == "second"
    # ensure no temporary files remain
    files = list(tmp_path.iterdir())
    assert files == [target]


def test_write_atomic_creates_parents(tmp_path: Path):
    nested_target = tmp_path / "subdir" / "nested" / "file.txt"
    write_atomic(nested_target, "content")
    assert nested_target.read_text() == "content"
    assert (tmp_path / "subdir" / "nested").is_dir()
