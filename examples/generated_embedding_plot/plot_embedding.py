#!/usr/bin/env python3
"""Render a publication-style embedding plot from a tiny synthetic atlas."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data.csv"
BUNDLE = ROOT / "reference_bundle_example.json"
FIGURES = ROOT / "figures"

CELL_COLORS = {
    "Naive T": "#4C78A8",
    "Effector T": "#E45756",
    "B cell": "#72B7B2",
    "NK cell": "#F58518",
    "Monocyte": "#54A24B",
    "Dendritic": "#B279A2",
}


def load_rows() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_reference_ids() -> str:
    if not BUNDLE.exists():
        return "not provided"
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    ids = [item["candidate_id"] for item in bundle.get("selected_references", [])]
    return ", ".join(ids) if ids else "not provided"


def strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8")


def centroid(rows: list[dict[str, str]]) -> tuple[float, float]:
    return (
        sum(float(row["x"]) for row in rows) / len(rows),
        sum(float(row["y"]) for row in rows) / len(rows),
    )


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    reference_ids = load_reference_ids()
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["cell_type"]].append(row)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.linewidth": 0.7,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "agentfiguregallery-generated-embedding",
        }
    )

    fig, ax = plt.subplots(figsize=(5.8, 4.25), constrained_layout=True)
    ax.set_facecolor("white")

    all_x = [float(row["x"]) for row in rows]
    all_y = [float(row["y"]) for row in rows]
    ax.scatter(all_x, all_y, s=26, c="#D8DCE2", edgecolors="none", alpha=0.72, zorder=1)

    for cell_type, cell_rows in grouped.items():
        reference = [row for row in cell_rows if row["condition"] == "reference"]
        disease = [row for row in cell_rows if row["condition"] == "disease"]
        color = CELL_COLORS[cell_type]
        ax.scatter(
            [float(row["x"]) for row in reference],
            [float(row["y"]) for row in reference],
            s=34,
            c=color,
            edgecolors="white",
            linewidths=0.45,
            alpha=0.92,
            label=cell_type,
            zorder=3,
        )
        ax.scatter(
            [float(row["x"]) for row in disease],
            [float(row["y"]) for row in disease],
            s=44,
            c=color,
            edgecolors="#1F2933",
            linewidths=0.62,
            alpha=0.96,
            zorder=4,
        )

    for cell_type, cell_rows in grouped.items():
        x, y = centroid(cell_rows)
        ax.text(
            x,
            y + 0.36,
            cell_type,
            ha="center",
            va="bottom",
            color="#202A33",
            fontsize=7.6,
            weight="medium",
        )

    ax.annotate(
        "activation gradient",
        xy=(3.75, 2.08),
        xytext=(2.55, 3.48),
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": "#2F3A45"},
        color="#2F3A45",
        fontsize=8,
        ha="center",
    )
    ax.text(
        -4.65,
        3.72,
        "Synthetic single-cell atlas",
        fontsize=10.5,
        weight="bold",
        color="#17202A",
    )
    ax.text(
        -4.65,
        3.37,
        f"Selected visual guidance: {reference_ids}",
        fontsize=7.4,
        color="#536173",
    )

    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_xlim(-4.85, 5.15)
    ax.set_ylim(-1.95, 4.05)
    ax.set_xticks([-4, -2, 0, 2, 4])
    ax.set_yticks([-1, 0, 1, 2, 3, 4])
    ax.tick_params(length=2.5, width=0.65, color="#3A4652")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#3A4652")
    ax.spines["bottom"].set_color("#3A4652")

    color_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=0.45,
            markersize=5.4,
            label=cell_type,
        )
        for cell_type, color in CELL_COLORS.items()
    ]
    state_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#ABB6C2",
            markeredgecolor="white",
            markersize=5.4,
            label="reference",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#ABB6C2",
            markeredgecolor="#1F2933",
            markeredgewidth=0.75,
            markersize=5.8,
            label="disease",
        ),
    ]
    legend = ax.legend(
        handles=color_handles + state_handles,
        loc="lower right",
        frameon=False,
        ncol=2,
        columnspacing=0.9,
        handletextpad=0.35,
        borderpad=0.2,
    )
    legend.set_title("Cell state", prop={"size": 7.8, "weight": "bold"})

    outputs = {
        "png": FIGURES / "embedding_preview.png",
        "pdf": FIGURES / "embedding_nature_style.pdf",
        "svg": FIGURES / "embedding_nature_style.svg",
    }
    fig.savefig(outputs["png"], dpi=240)
    fig.savefig(outputs["pdf"], metadata={"Creator": "AgentFigureGallery", "CreationDate": None, "ModDate": None})
    fig.savefig(outputs["svg"], metadata={"Date": None})
    strip_trailing_whitespace(outputs["svg"])
    plt.close(fig)

    for kind, path in outputs.items():
        print(f"{kind}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
