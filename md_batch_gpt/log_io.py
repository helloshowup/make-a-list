from pathlib import Path


def append_log_record(log_path: Path, file_path: Path, prompt_path: Path, output: str):
    try:
        relative = file_path.relative_to(Path.cwd())
    except ValueError:
        relative = file_path.name
    header = f"=== {relative} | prompt: {prompt_path.name} ===\n"
    sep = "\n---\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(output.rstrip("\n") + "\n")
        f.write(sep)
