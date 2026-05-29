# Contributing

AgentFigureGallery contributions should improve the agent-human-agent loop:

```text
agent query -> gallery display -> human like/reject/select -> agent action
```

## Good Contributions

- New public plotting sources with visible previews.
- Better plot-type routing.
- Better candidate metadata and source attribution.
- Better preference-aware ranking.
- Improvements to `ExtendAgent/` instructions.
- Community packs under `community_pool/packs/<pack_name>/` that follow `docs/COMMUNITY_PACKS.md`.

## Community Pack Contributions

Use community packs when you want to contribute a reusable set of plotting references rather than a one-off source suggestion.

Required path:

```text
community_pool/packs/<pack_name>/
```

Before opening a PR:

- Read `docs/COMMUNITY_PACKS.md`.
- Follow `community_pool/pack_schema.example.yaml`.
- Follow `community_pool/candidate_schema.example.json`.
- Include visible preview PNGs for every candidate.
- Preserve source attribution and license metadata.
- Keep large generated assets, raw upstream mirrors, private paths, and tokens out of Git.

If you only have source ideas, open a Gallery Expansion or Community Pack issue first.

## Translation Contributions

The default GitHub entrypoint is `README.md` in English. The Simplified Chinese entrypoint is `README.zh-CN.md`.

When changing user-facing README content:

- Keep install commands, paths, issue links, and code blocks synchronized across both files.
- Prefer human-reviewed Simplified Chinese wording for `README.zh-CN.md`; avoid machine-only translation PRs for maintainer-facing instructions.
- If a translation falls behind, note the English README as canonical until the Chinese version is updated.

## Before Opening a PR

From the repo root, after installing with `pip install -e .` in an active virtual environment, run:

```bash
agentfiguregallery doctor
agentfiguregallery install-skill --target codex --dest /tmp/afg-skills-test
agentfiguregallery install-skill --target claude-code --dest /tmp/afg-claude-skills-test
agentfiguregallery install-skill --target cursor --dest /tmp/afg-cursor-skills-test
agentfiguregallery install-cursor-rule --project /tmp/afg-cursor-project-test --force
bash -n scripts/install.sh
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
