from pathlib import Path

import importlib


def import_orchestrator():
    if "md_batch_gpt.orchestrator" in importlib.sys.modules:
        del importlib.sys.modules["md_batch_gpt.orchestrator"]
    return importlib.import_module("md_batch_gpt.orchestrator")


def test_process_folder(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    orch = import_orchestrator()

    calls = []

    def fake_send_prompt(prompt: str, content: str, model: str, temp: float) -> str:
        calls.append((prompt, content, model, temp))
        return f"{content}[{prompt}]"

    monkeypatch.setattr(orch, "send_prompt", fake_send_prompt)

    (tmp_path / "a.md").write_text("A")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.md").write_text("B")
    (tmp_path / ".hidden.md").write_text("hidden")

    p1 = tmp_path / "p1.txt"
    p1.write_text("p1")
    p2 = tmp_path / "p2.txt"
    p2.write_text("p2")

    orch.process_folder(tmp_path, [p1, p2], model="m", temp=0.5)

    assert (tmp_path / "a.md").read_text() == "A[p1][p2]"
    assert (sub / "b.md").read_text() == "B[p1][p2]"
    assert (tmp_path / ".hidden.md").read_text() == "hidden"
    assert len(calls) == 4
    assert all(call[2:] == ("m", 0.5) for call in calls)
