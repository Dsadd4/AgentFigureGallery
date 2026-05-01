# Hugging Face Dataset Card Draft

Use this as the README for `dsadd4/AgentFigureGallery` on Hugging Face.

Sync only the dataset card:

```bash
export HF_TOKEN="your_huggingface_write_token"
python scripts/upload_full_public_to_hf.py --card-only
```

````markdown
---
pretty_name: AgentFigureGallery
language:
- en
tags:
- scientific-figures
- data-visualization
- bioinformatics
- ai-agents
- human-in-the-loop
- nature-style
- cell-style
- science-style
license: mit
---

# AgentFigureGallery Full Public KB

Full public visual reference pack for AgentFigureGallery, a human-preference memory system for scientific plotting agents.

The pack contains 16,341 public visual candidates across 10 scientific plot types, plus metadata needed by the AgentFigureGallery CLI and browser gallery.

## Use

```bash
git clone https://github.com/Dsadd4/AgentFigureGallery.git
cd AgentFigureGallery
pip install -e .
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
agentfiguregallery gallery --plot-type embedding_plot --limit 50 --serve
```

## Candidate Counts

- bar_chart: 1,516
- benchmark_performance: 2,310
- box_violin_distribution: 1,026
- embedding_plot: 1,273
- heatmap_matrix: 1,122
- line_chart: 1,035
- microscopy_panel: 1,756
- multi_panel_figure: 4,148
- scatter_plot: 1,489
- spatial_map: 666

## Intended Use

This dataset is intended for visual reference retrieval, human preference selection, and agent-guided scientific figure generation.

It is not intended as a benchmark for biological conclusions, image classification, or clinical decision making.

## Source And Filtering

The full-public pack is filtered to remove private local paths and private repositories. Public source attribution is preserved in candidate metadata when available.
````
