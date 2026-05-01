# Launch Plan

## One-Line Positioning

Teach your plotting agent Nature, Cell, and Science figure taste in one minute.

Clone once, run one command, and your coding agent learns to query a human-curated scientific figure gallery before writing plotting code.

## Short Launch Copy

AgentFigureGallery is a human-preference memory loop for publication-quality scientific figures.

Before an AI agent writes plotting code, it queries real scientific visual references, shows candidates in a browser gallery, records human like/reject/select feedback, and exports a selected bundle for agent action.

The first public KB contains 16,341 visual candidates across 10 scientific plot types.

## Social Post

```text
I built AgentFigureGallery: a human-preference memory loop for scientific plotting agents.

Instead of asking an agent to invent a Nature/Cell/Science-style figure from text, it first looks at real visual references, lets the human like/reject/select, then writes code from the selected bundle.

16k+ public figure candidates.
Dynamic browser gallery.
One-command bootstrap plus Codex, Claude Code, and Cursor rule install.
Global and plot-type preference memory.

GitHub: https://github.com/Dsadd4/AgentFigureGallery
```

## Target Channels

- GitHub topics and README
- Hugging Face dataset card
- PyPI once packaging is ready
- Reddit: `r/bioinformatics`, `r/datascience`, `r/MachineLearning`
- X / LinkedIn demo GIF post
- Awesome lists for scientific visualization, bioinformatics, and AI agents

## Demo Script

1. Run:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/Dsadd4/AgentFigureGallery/main/scripts/install.sh | bash
   ```
2. Open the README and show the GIF.
3. Run:
   ```bash
   agentfiguregallery gallery --plot-type embedding_plot --limit 50 --serve
   ```
4. G Reject one bad image.
5. G Like one strong image.
6. Select one candidate.
7. Export bundle.
8. Tell the agent to implement a plot using the exported reference bundle.

## Social Preview

Use `docs/assets/agentfiguregallery-social-preview.png` as the GitHub repository social preview image. Pair it with the README GIF for posts on X, LinkedIn, Reddit, and bioinformatics/scientific-visualization awesome-list submissions.

## Launch Readiness

- README has a two-line value proposition.
- Demo GIF is visible above the fold.
- GitHub social preview image is uploaded.
- GitHub topics are configured.
- Full-public pack has remote validation.
- Hugging Face dataset card can be synced with `python scripts/upload_full_public_to_hf.py --card-only`.
- Faster mirror for China/Huawei Cloud deployments is still recommended before claiming frictionless full-public setup everywhere.
