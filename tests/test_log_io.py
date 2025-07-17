from md_batch_gpt.log_io import append_log_record


def test_append_log_record(tmp_path):
    log = tmp_path / "log.txt"
    src = tmp_path / "a.md"
    src.write_text("dummy")
    prm = tmp_path / "p.txt"
    prm.write_text("prompt")
    append_log_record(log, src, prm, "OUTPUT")
    content = log.read_text(encoding="utf-8")
    assert "=== a.md | prompt: p.txt ===" in content
    assert "OUTPUT" in content
