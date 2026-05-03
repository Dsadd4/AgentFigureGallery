# Codex Skill Plot-Type Smoke Test

This example captures a small toy test run immediately after Codex was equipped with the `agent-figure-gallery` skill.

The test asks the agent to verify the skill, then render one Nature-style smoke example for every supported AgentFigureGallery plot type. It is intentionally synthetic and lightweight, but it exercises the same practical claim as the full workflow: the agent can move from installed skill and plot-type awareness to publication-style figure outputs.

## Preview

![AgentFigureGallery plot-type smoke examples](figures/agentfiguregallery_plot_type_examples_preview.png)

## Plot Types

- `bar_chart`
- `benchmark_performance`
- `box_violin_distribution`
- `embedding_plot`
- `heatmap_matrix`
- `line_chart`
- `microscopy_panel`
- `multi_panel_figure`
- `scatter_plot`
- `spatial_map`

## Run

```bash
python examples/plot_type_examples/render_plot_type_examples.py
```

The script writes regenerated outputs into this example folder:

- `figures/*.png`
- `figures/*.pdf`
- `figures/*.svg`
- `source_data/*.csv`
- `manifest.json`

The plotting script uses `matplotlib`, `numpy`, and `Pillow`.

## Why This Example Exists

This is not a benchmark of model intelligence. It is a smoke test for the installed skill and the repository's visual contract:

- the agent recognizes the available AgentFigureGallery plot types
- every plot type can produce a readable Nature-style toy example
- PNG previews are paired with high-resolution PDF/SVG outputs
- the contact sheet gives a quick first-screen demonstration for README and release pages
