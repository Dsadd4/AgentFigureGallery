#!/usr/bin/env python3
"""Render the GitHub social preview image for AgentFigureGallery."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.patches as patches
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "assets" / "agentfiguregallery-social-preview.png"
PREVIEW = ROOT / "examples" / "generated_embedding_plot" / "figures" / "embedding_preview.png"


def add_workflow(ax: plt.Axes) -> None:
    labels = ["agent query", "visual gallery", "human taste", "plot code"]
    colors = ["#245B5F", "#E45756", "#F2A541", "#3A6EA5"]
    x0 = 0.08
    y = 0.19
    gap = 0.22
    for index, (label, color) in enumerate(zip(labels, colors)):
        x = x0 + index * gap
        circle = patches.Circle((x, y), 0.045, transform=ax.transAxes, facecolor=color, edgecolor="none")
        ax.add_patch(circle)
        ax.text(x, y, str(index + 1), transform=ax.transAxes, ha="center", va="center", color="white", fontsize=15, weight="bold")
        ax.text(x, y - 0.08, label, transform=ax.transAxes, ha="center", va="center", color="#263238", fontsize=13)
        if index < len(labels) - 1:
            ax.annotate(
                "",
                xy=(x + gap - 0.055, y),
                xytext=(x + 0.055, y),
                xycoords=ax.transAxes,
                arrowprops={"arrowstyle": "->", "lw": 2.0, "color": "#667085"},
            )


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "figure.dpi": 100,
            "savefig.dpi": 100,
        }
    )

    fig = plt.figure(figsize=(12.8, 6.4), facecolor="#F8FAFC")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.add_patch(patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="#F8FAFC", edgecolor="none"))
    ax.add_patch(patches.Rectangle((0.0, 0.0), 0.035, 1.0, transform=ax.transAxes, facecolor="#245B5F", edgecolor="none"))
    ax.add_patch(patches.Rectangle((0.965, 0.0), 0.035, 1.0, transform=ax.transAxes, facecolor="#E45756", edgecolor="none"))

    ax.text(0.075, 0.78, "AgentFigureGallery", transform=ax.transAxes, fontsize=42, weight="bold", color="#18202A")
    ax.text(
        0.078,
        0.665,
        "Nature / Cell / Science figure taste\nfor coding agents in one minute.",
        transform=ax.transAxes,
        fontsize=19,
        color="#344054",
        linespacing=1.2,
    )
    ax.text(
        0.078,
        0.545,
        "Human preference memory for scientific figures",
        transform=ax.transAxes,
        fontsize=17,
        color="#0F766E",
        weight="bold",
    )

    command_box = patches.FancyBboxPatch(
        (0.078, 0.42),
        0.49,
        0.085,
        boxstyle="round,pad=0.018,rounding_size=0.018",
        transform=ax.transAxes,
        facecolor="#101828",
        edgecolor="none",
    )
    ax.add_patch(command_box)
    ax.text(
        0.098,
        0.455,
        "agentfiguregallery install-skill --target codex",
        transform=ax.transAxes,
        fontsize=13.2,
        family="DejaVu Sans Mono",
        color="#ECFDF3",
        va="center",
    )

    ax.text(0.078, 0.34, "Codex | Claude Code | Cursor-compatible", transform=ax.transAxes, fontsize=15, color="#4B5563")
    add_workflow(ax)

    if PREVIEW.exists():
        image = mpimg.imread(PREVIEW)
        image_ax = fig.add_axes([0.64, 0.18, 0.26, 0.61])
        image_ax.imshow(image)
        image_ax.axis("off")
        for spine in image_ax.spines.values():
            spine.set_visible(False)
        border = patches.FancyBboxPatch(
            (0.625, 0.15),
            0.30,
            0.67,
            boxstyle="round,pad=0.008,rounding_size=0.02",
            transform=ax.transAxes,
            facecolor="none",
            edgecolor="#CBD5E1",
            linewidth=2.0,
        )
        ax.add_patch(border)
        ax.text(0.64, 0.845, "Reference-guided output", transform=ax.transAxes, fontsize=15, color="#1F2937", weight="bold")

    fig.savefig(OUTPUT, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
