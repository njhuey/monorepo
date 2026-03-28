# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git rules

- Never commit directly to `main` or push to `main`
- Every PR must contain exactly one commit
- Never mention that the pull request was written by claude

## Python style

- Docstrings: NumPy format, first line on a new line after `"""`

## Build system

This repo uses [Pants 2.31](https://www.pantsbuild.org/2.31/docs). All commands are run via `pants` from the repo root.

```bash
pants list ::                              # list all targets
pants run monorepo/connections:connections # run a binary
pants lint ::                              # ruff lint
pants fmt ::                               # ruff format
pants check ::                             # mypy type check
pants test ::                              # run all tests
pants test monorepo/some/path:tests        # run a single test target
```

## Structure

- `monorepo/` — Python source packages (repo root is the Pants source root)
- `third_party/python/default.lock` — Python dependency lockfile
- `pants.toml` — Pants configuration (backends, interpreter constraints, resolves)

## Adding a new Python project

Create `monorepo/<name>/BUILD` with `python_sources` and optionally a `pex_binary`:

```python
python_sources(name="lib")

pex_binary(
    name="my_tool",
    entry_point="__main__.py",
    dependencies=[":lib"],
)
```

## Adding third-party dependencies

Add requirements to a `python_requirement` in a BUILD file, then regenerate the lockfile:

```bash
pants generate-lockfiles --resolve=default
```

## Ruff backends

The ruff backends in Pants 2.31 are under `experimental`:
- `pants.backend.experimental.python.lint.ruff.check`
- `pants.backend.experimental.python.lint.ruff.format`
