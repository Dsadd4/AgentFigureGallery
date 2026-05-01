# Release Architecture

## Product Thesis

AgentFigureGallery should be presented as a visual memory system for plotting agents.

The central contract is:

```text
agent query -> candidate gallery -> human preference -> reference bundle -> agent action
```

This is stronger than "Nature-style plotting templates" because the human preference signal becomes part of the agent workflow.

## Repository Split

### GitHub main repo

Purpose: installable controller, frontend, skill, documentation, and small examples.

Include:

- CLI wrapper
- backend reference-session commands
- gallery frontend
- Codex skill wrapper
- templates
- small smoke-test candidate pack
- manifest downloader
- docs and examples

Exclude:

- full `repos/` mirror
- full `outputs/`
- large PDF/notebook/data artifacts from upstream repositories
- full preview cache unless it is small enough for a release asset

### External asset packs

Purpose: ship large visual and code-reference resources without bloating git history.

Recommended packs:

- `minimal`: smoke tests and examples
- `public-preview`: curated previews plus candidate index
- `source-scripts`: reusable source scripts and notebooks excerpts
- `full-corpus`: optional raw research corpus

## Current Development Workspace Risk

The current workspace is too large to publish directly:

- workspace: about 22 GB
- `outputs/`: about 447 MB
- `data/`: about 73 MB
- `scripts/`: about 1.2 MB
- `templates/`: under 1 MB
- `skills/`: tiny
- selectable candidates: 16,341

Most size risk comes from downloaded upstream repositories and their `.git` packs, notebooks, PDFs, and raw data files.

## Public v0.1 Scope

The first release should avoid perfection and prove the loop:

1. Install package.
2. Download `minimal` or `public-preview` pack.
3. Start gallery locally.
4. Generate 50 candidates for a plot type.
5. Like, reject, global reject, and select.
6. Export a reference bundle.
7. Let an agent use the bundle to write or revise plotting code.

## Source Mapping From Development Repo

Copy or refactor these into the public repo:

- `scripts/drawing_agent_cli.py`
- `scripts/query_drawing_agent_knowledge.py`
- `scripts/generate_reference_session.py`
- `scripts/update_reference_preferences.py`
- `scripts/export_reference_bundle.py`
- `scripts/serve_reference_gallery.py`
- `scripts/build_reference_candidate_index.py`
- `scripts/reference_workflow_common.py`
- `frontend/reference_gallery/`
- `templates/`
- `skills/nature-figure-agent/`
- `data/agent_kit_registry.json`
- `data/reference_candidate_facets.json`
- a sampled `data/reference_candidate_index.sample.json`

Do not copy directly:

- `repos/`
- full `outputs/`
- local discovery scratch files
- private tokens or machine-specific paths

