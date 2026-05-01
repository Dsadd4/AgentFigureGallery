# AgentFigureGallery

Make plotting agents learn Nature, Cell, and Science figure taste in one minute.
It turns real visual references plus human like/reject feedback into action-ready plotting guidance for upstream agents.

## Install

```bash
git clone https://github.com/Dsadd4/AgentFigureGallery.git
cd AgentFigureGallery
python -m venv .venv
source .venv/bin/activate
pip install -e .
agentfiguregallery gallery --plot-type heatmap_matrix --limit 50 --serve
```

Full public KB:

```bash
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
```

Fallback when Hugging Face is blocked:

```bash
agentfiguregallery setup --pack full-public --manifest manifests/resource_manifest.github-api.json
```

## Dynamic Gallery

```text
agent query -> gallery display -> human like/reject/select -> agent action
```

Use the browser gallery to generate candidates by plot type, remove bad references globally, keep type-specific preferences, and export selected references for the agent that will write the final plotting code.

```bash
agentfiguregallery query --task "Nature-style heatmap for pathway activity"
agentfiguregallery gallery --plot-type bar_chart --limit 100 --serve
```

## What Is Inside

- 16,341 full-public visual candidates across 10 scientific plot types.
- Glike-curated minimal pack committed for instant smoke tests.
- Backend CLI, browser gallery, Codex skill wrapper, and agent expansion guide.
- Candidate IDs, global/type-level preferences, and export bundles for agent handoff.

## Search Keywords

`scientific-figures` `nature-style` `cell-style` `science-style` `plotting-agent` `ai-agent` `human-in-the-loop` `data-visualization` `bioinformatics` `matplotlib` `ggplot2` `reference-gallery`

## Docs

- `ExtendAgent/`: instructions for agents that expand the gallery.
- `docs/FULL_KB_DISTRIBUTION.md`: public asset-pack strategy.
- `docs/REMOTE_FULL_VALIDATION.md`: first remote full-public validation and current mirror-speed caveat.
