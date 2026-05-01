# AgentFigureGallery

Human-in-the-loop visual reference memory for scientific plotting agents.

AgentFigureGallery is built around one loop:

```text
agent query -> gallery display -> human like/reject/select -> agent action
```

The repository is not meant to be another plotting template dump. It is a compact controller for scientific figure agents:

- query by task, plot type, subtype, motif, or design pattern
- show real visual candidates before code is chosen
- record local and global human preferences
- export a bundle with selected references, source code paths, templates, palettes, and implementation notes
- let an upstream agent act on the selected bundle

## Target Quickstart

```bash
git clone https://github.com/Dsadd4/AgentFigureGallery.git
cd AgentFigureGallery
python -m venv .venv
source .venv/bin/activate
pip install -e .
agentfiguregallery gallery --plot-type bar_chart --limit 50 --serve
```

The first public release should make the command above work end to end.

The current development cut already includes a Glike-curated `minimal` pack:

- 284 human-liked candidates after private-path filtering
- 10 plot types represented
- preview assets under `assets/packs/minimal/previews`
- candidate index at `data/reference_candidate_index.json`

For the full public KB, keep the GitHub repo light and configure assets with one command:

```bash
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
```

If Hugging Face is blocked in the deployment environment, use the GitHub Release mirror manifest after cloning the repo:

```bash
agentfiguregallery setup --pack full-public --manifest manifests/resource_manifest.github-api.json
```

The extension workflow for other agents lives in `ExtendAgent/`.

## Public Repo Shape

The GitHub repository should stay small and reproducible. Large preview packs, raw source repositories, and rendered corpora should live outside git and be fetched by manifest.

Keep in git:

- agent CLI and backend controller
- reference gallery frontend
- Codex skill wrapper
- lightweight templates and examples
- small manifest files
- sampled reference index for smoke tests
- docs for the agent-human-agent loop

Keep out of git:

- downloaded upstream repositories
- full preview image cache
- raw notebooks and raw data from source repos
- long-running discovery outputs
- local preference logs, unless intentionally published as a curated benchmark

## Core Commands

The public CLI should expose these verbs:

```bash
agentfiguregallery query --task "Nature-style heatmap for pathway activity"
agentfiguregallery gallery --plot-type heatmap_matrix --limit 50 --serve
agentfiguregallery prefer --session outputs/reference_sessions/<id> --like HEAT-... --reject HEAT-...
agentfiguregallery bundle --session outputs/reference_sessions/<id> --copy-scripts
agentfiguregallery act --bundle outputs/reference_sessions/<id>/export_bundle/reference_bundle.json
```

The internal implementation can keep the existing lower-level scripts. The public README should teach the loop, not the internals.

## Release Asset Strategy

Use named packs:

- `minimal`: tiny smoke-test pack, enough for CI and screenshots; this can live in git
- `public-preview`: all curated preview images and candidate index files
- `source-scripts`: script-only source excerpts needed for selected bundles
- `full-corpus`: optional research corpus; never required for normal users

See `docs/RESOURCE_STRATEGY.md` and `manifests/resource_manifest.example.json`.

See `docs/FULL_KB_DISTRIBUTION.md` for the upload and one-command setup plan.

See `docs/REMOTE_FULL_VALIDATION.md` for the first remote full-public validation and the current network caveat for GitHub Release downloads on China/Huawei Cloud style hosts.

## Current Local Baseline

The development workspace currently has more than 16k selectable visual candidates across 10 plot types. This is enough to justify an external asset-pack design before publishing.

The first full-public release is mirrored as GitHub Release assets under `full-public-v0.1.0` for environments where Hugging Face is not reachable.
