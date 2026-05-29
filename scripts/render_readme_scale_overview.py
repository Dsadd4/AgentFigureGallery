#!/usr/bin/env python3
"""Render the README bar chart from the candidate facets."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
FACETS = ROOT / "data" / "reference_candidate_facets.json"
OUT_BASE = ROOT / "docs" / "assets" / "agentfiguregallery-scale-overview"

LABELS = {
    "bar_chart": "bar chart",
    "benchmark_performance": "benchmark",
    "box_violin_distribution": "box / violin",
    "embedding_plot": "embedding",
    "heatmap_matrix": "heatmap",
    "line_chart": "line chart",
    "microscopy_panel": "microscopy",
    "multi_panel_figure": "multi-panel",
    "scatter_plot": "scatter",
    "spatial_map": "spatial",
}

COLORS = {
    "multi_panel_figure": "#2A6F6F",
    "benchmark_performance": "#4E79A7",
    "microscopy_panel": "#8B6BB1",
    "bar_chart": "#D95F59",
    "scatter_plot": "#5B8CC0",
    "embedding_plot": "#E6A23C",
    "heatmap_matrix": "#6B9B68",
    "line_chart": "#9A7B42",
    "box_violin_distribution": "#D6812A",
    "spatial_map": "#7A858C",
}


def load_facets() -> dict:
    return json.loads(FACETS.read_text(encoding="utf-8"))


def thousands(value: float, _pos: int) -> str:
    if value == 0:
        return "0"
    return f"{value / 1000:g}k"


def main() -> int:
    facets = load_facets()
    counts = facets["selectable_by_plot_type"]
    total = facets["candidate_count"]
    generated_at = facets.get("generated_at", "").split("T", maxsplit=1)[0]
    rows = sorted(counts.items(), key=lambda item: item[1], reverse=True)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.8,
            "axes.linewidth": 0.8,
            "axes.edgecolor": "#222222",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    fig, ax = plt.subplots(figsize=(8.2, 4.75), facecolor="white")
    fig.subplots_adjust(left=0.25, right=0.90, top=0.875, bottom=0.14)
    ax.set_facecolor("white")

    y_positions = list(range(len(rows)))
    values = [value for _key, value in rows]
    labels = [LABELS[key] for key, _value in rows]
    colors = [COLORS[key] for key, _value in rows]

    ax.barh(y_positions, values, color=colors, height=0.50)
    ax.set_yticks(y_positions, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.20)
    ax.xaxis.set_major_formatter(FuncFormatter(thousands))
    ax.grid(False)

    fig.text(0.25, 0.955, "Reference coverage by plot type", ha="left", va="top", fontsize=13.4, weight="bold", color="#111111")
    fig.text(
        0.25,
        0.910,
        f"AgentFigureGallery full-public pack: {total:,} preview-backed candidates across {len(counts)} plot types",
        ha="left",
        va="top",
        fontsize=8.3,
        color="#555555",
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)

    for y, value in zip(y_positions, values):
        pct = value / total * 100
        ax.text(
            value + max(values) * 0.022,
            y,
            f"{value:,} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=8.2,
            color="#333333",
        )

    fig.text(0.25, 0.058, f"Source: data/reference_candidate_facets.json; generated {generated_at}", fontsize=7.0, color="#666666")
    fig.text(0.25, 0.032, "Rendered with scripts/render_readme_scale_overview.py", fontsize=7.0, color="#666666")

    OUT_BASE.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "pdf", "svg"]:
        fig.savefig(OUT_BASE.with_suffix(f".{suffix}"), dpi=240, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    svg_path = OUT_BASE.with_suffix(".svg")
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")

    print(OUT_BASE.with_suffix(".png"))
    print(OUT_BASE.with_suffix(".pdf"))
    print(OUT_BASE.with_suffix(".svg"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
