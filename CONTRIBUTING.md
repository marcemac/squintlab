# Contributing

squintlab is developed one small task at a time. Each task is written down before it is coded, and each lands as one pull request.

## Task format

Every task has:

- **ID**: milestone and number, such as `M1-T03`.
- **Goal and files touched**: one or two sentences on what changes, and the files expected to change.
- **Done when**: a test that passes only if the task is finished. Its numeric tolerances live in the test itself, not in prose, so the test is the single source of truth.
- **Depends on**: the task IDs that must be merged first, or "none".

Open a task with the "Task" issue form. The plan for all milestones is in [ROADMAP.md](ROADMAP.md).

## Session protocol

1. Read the task and every [DECISIONS.md](DECISIONS.md) entry it names.
2. Write the failing test first.
3. Implement until `pytest`, `ruff` and `mypy` all pass.
4. Open one pull request per task and fill in its checklist.
5. Whenever a design choice changes, add a DECISIONS.md entry that states what was decided, why, and the accepted cost. Never delete an older entry: mark it as superseded by the new one.

## Repository rules

1. **No text or images from any book.** Cite sources; do not copy from them.
2. **No trained models, language-model features, or face or person detection.** Analyses are closed-form and deterministic.
3. **No personal data, passwords, keys or tokens**, in code, tests, fixtures, issues or pull requests.
4. **Benchmark images come only from the manifest** ([benchmarks/manifest.toml](benchmarks/manifest.toml)): public domain or CC0 at the holding museum, checksum-verified, and never committed.

## Running the checks

The project uses [uv](https://docs.astral.sh/uv/). From the repository root:

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
lychee --config lychee.toml --offline './**/*.md'
```

The last command checks Markdown links without network access, as CI does (lychee v0.21.0). Tests that need the internet are marked `network` and run only with `--run-network`.
