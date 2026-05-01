# Contributing

AgentFigureGallery contributions should improve the agent-human-agent loop:

```text
agent query -> gallery display -> human select -> agent action
```

## Good Contributions

- New public plotting sources with visible previews.
- Better plot-type routing.
- Better candidate metadata and source attribution.
- Better preference-aware ranking.
- Improvements to `ExtendAgent/` instructions.

## Before Opening a PR

Run:

```bash
agentfiguregallery doctor
agentfiguregallery install-skill --target codex --dest /tmp/afg-skills-test
python scripts/check_private_paths.py --root .
python scripts/download_assets.py --pack minimal --dry-run
agentfiguregallery query --plot-type heatmap_matrix --json
```

Do not commit tokens, local private paths, raw upstream repository mirrors, or large generated outputs.

## Gallery Expansion Checklist

- Every accepted candidate has a visible preview image.
- Every accepted candidate has a stable `candidate_id`.
- Source repository, license, and attribution metadata are preserved when available.
- Bad references should be rejected instead of silently deleted when they carry useful preference signal.
- Full-public archives should stay outside the Python wheel and be distributed through manifests.
