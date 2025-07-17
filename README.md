# md-batch-gpt (a.k.a. two-prong)

Batch-process Markdown files with one or more LLM prompt passes. Originally built to *rewrite files in place*; now supports a safer **Extraction Mode (default)** that **leaves sources untouched** and appends each model output to a log file for later review / downstream processing.

---

## Quick Start

```bash
# install deps
poetry install
```

Create a `.env` in the project root (or export in your shell):

```bash
OPENAI_API_KEY=sk-...
```

The client reads `OPENAI_API_KEY` at import. If missing, it raises at startup.

### Basic Run (Extraction Mode – default)

Processes every `*.md` under `<FOLDER>`, applies each prompt in the order given, and appends one log record per prompt pass per file to `extracted.txt` (or a path you choose).

```bash
poetry run mdgpt run \
  path/to/docs \
  --prompts prompts/extract_course.txt prompts/clean_output.txt \
  --log-file extracted.txt          # optional; default=./extracted.txt \
  --no-inplace                      # default; explicit for clarity
```

The `--log-file` path may be relative or absolute; relative paths are resolved
against your current working directory.
If the path cannot be written to, the command exits with an error.

### Log Record Format (human-readable blocks)

Each record starts with a header line, then the model output, then a `---` separator:

```yaml
=== relative/path/to/file.md | prompt: extract_course.txt ===
<model output text...may span multiple lines>
---
```

One record is written after each prompt pass. So 2 prompts × 5 files ⇒ 10 records.
Outputs are encoded UTF-8.

### Legacy In-Place Rewrite Mode

If you want the old behavior (each prompt pass mutates the file on disk), enable:

```bash
poetry run mdgpt run path/to/docs \
  --prompts prompts/fix_typos.txt \
  --inplace
```

In this mode the tool writes the transformed text back to the same file atomically after each pass (temp file + `os.replace`). Use with caution; source content is overwritten.

### Options

| Option | Type | Default | Notes |
|-------|------|---------|-------|
| folder | path (positional) | required | Root dir scanned recursively for *.md (dotfiles skipped). |
| --prompts | list[path] | auto-discover prompts/*.txt if omitted | Prompts applied in order. |
| --model | str | from pyproject.toml or o3 fallback | Passed to OpenAI Chat Completions. |
| --max-tokens | int | None | Cap completion size. |
| --regex-json | path | None | Optional regex filters (future / experimental). |
| --verbose, -v | flag | False | Echo progress (file, pass idx); also prints log record info in Extraction Mode. |
| --dry-run | flag | False | Print files + prompt count; no API calls; no log writes; no disk changes. |
| --log-file | path | ./extracted.txt | Where Extraction Mode appends records. (new) |
| --inplace / --no-inplace | flag | --no-inplace | Toggle Extraction vs Rewrite modes. (new) |

When verbose mode is active, each log record is announced with its index, file path, and prompt name.

### Dry Run

Use `--dry-run` first to sanity-check which files will be processed and how many prompts will run. Nothing is sent to OpenAI; nothing is written or appended. Combine with `--verbose` for extra context.

### Prompt Files

Prompt files are plain text. When not supplied, all `*.txt` in the package `prompts/` dir are auto-loaded (sorted). Prompts become system messages; the Markdown file content is sent as the user message.

### Example ADHD-Friendly Extraction Workflow

1. Draft an extraction prompt that pulls the fields you need from a course module (title, learning outcomes, durations, etc.).
2. Run Extraction Mode over your course folder.
3. Open `extracted.txt`, search for the file headers, copy/paste outputs into your tracking sheet or next pipeline step.
4. Re-run with additional prompts that clean / normalize fields; outputs append below prior runs, preserving history.

### Development

Standard Python 3.11 / Poetry project. Run tests:

```bash
poetry run pytest -q
```

### License

MIT (see `LICENSE`).

