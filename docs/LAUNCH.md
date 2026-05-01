# Launch Plan

## One-Line Positioning

Teach your plotting agent Nature, Cell, and Science figure taste in one minute.

Clone once, run one command, and your Codex learns to query a human-curated scientific figure gallery before writing plotting code.

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
One-command Codex skill install.
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

1. Open the README and show the GIF.
2. Run:
   ```bash
   agentfiguregallery gallery --plot-type embedding_plot --limit 50 --serve
   ```
3. G Reject one bad image.
4. G Like one strong image.
5. Select one candidate.
6. Export bundle.
7. Tell the agent to implement a plot using the exported reference bundle.

## Launch Readiness

- README has a two-line value proposition.
- Demo GIF is visible above the fold.
- GitHub topics are configured.
- Full-public pack has remote validation.
- Hugging Face dataset card can be synced with `python scripts/upload_full_public_to_hf.py --card-only`.
- Faster mirror for China/Huawei Cloud deployments is still recommended before claiming frictionless full-public setup everywhere.
