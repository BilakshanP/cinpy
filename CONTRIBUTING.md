# Contributing to CinPy

## Setup

```bash
git clone https://github.com/bilakshanp/cinpy.git
cd cinpy
git config core.hooksPath .githooks
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

## Development

```bash
uv run cinpy-example benchmarks       # run an example
ruff check src/                        # lint
ruff format src/                       # format
basedpyright src/                      # type check
pytest                                 # run all tests
pytest --cov=cinpy                     # with coverage
```

## Pre-commit Hooks

The `.githooks/pre-commit` hook runs automatically on commit:
- `ruff check` — linting
- `ruff format --check` — formatting
- `basedpyright` — type checking

If any check fails, the commit is blocked. Fix the issues and retry.

## Code Style

- Follow existing patterns — match the surrounding code
- `ruff check src/` must pass (enforced by pre-commit hook)
- `ruff format src/` must pass (enforced by pre-commit hook)
- `basedpyright src/` must pass with 0 errors (enforced by pre-commit hook)
- Use `Any` sparingly — only where CFFI's dynamic nature requires it
- All new features need tests
