# PyPI Release Plan

Goal:

```bash
pip install agentfiguregallery
```

Checked on 2026-05-01: `https://pypi.org/pypi/agentfiguregallery/json` returned 404, so the name appears available.

## Release Scope

The first PyPI release should be a controller package:

- CLI: `agentfiguregallery`
- gallery server
- preference and bundle commands
- setup command for external asset packs
- no full public preview corpus inside the wheel

Users should point the CLI at a KB root when using an external clone:

```bash
export AGENT_FIGURE_GALLERY_ROOT=/path/to/AgentFigureGallery
```

## Build

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

## Publish

Prefer PyPI Trusted Publishing from GitHub Actions. If using a token, keep it outside the repository and shell history.

After publishing:

```bash
python -m pip install agentfiguregallery
agentfiguregallery --help
```

## Preflight

- `agentfiguregallery query` works with `AGENT_FIGURE_GALLERY_ROOT`.
- `agentfiguregallery prefer` writes preferences.
- `agentfiguregallery bundle` writes `reference_bundle.json`.
- README still teaches the clone workflow until standalone package resources are finalized.
