#!/usr/bin/env python3
"""Render a small before/after benchmark for reference-guided plotting."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "generated_embedding_plot" / "data.csv"
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


def grouped_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["cell_type"]].append(row)
    return grouped


def strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8")


def centroid(rows: list[dict[str, str]]) -> tuple[float, float]:
    return (
        sum(float(row["x"]) for row in rows) / len(rows),
        sum(float(row["y"]) for row in rows) / len(rows),
    )


def draw_baseline(ax: plt.Axes, rows: list[dict[str, str]], grouped: dict[str, list[dict[str, str]]]) -> None:
    colors = plt.cm.tab20.colors
    for index, (cell_type, cell_rows) in enumerate(grouped.items()):
        ax.scatter(
            [float(row["x"]) for row in cell_rows],
            [float(row["y"]) for row in cell_rows],
            s=58,
            color=colors[index % len(colors)],
            marker=["o", "s", "^", "D", "P", "X"][index % 6],
            edgecolors="black",
            linewidths=0.35,
            alpha=0.82,
            label=cell_type,
        )
    ax.set_title("Before: prompt-only plotting", fontsize=12, weight="bold")
    ax.set_xlabel("umap_1")
    ax.set_ylabel("umap_2")
    ax.grid(True, color="#D0D5DD", linewidth=0.9)
    ax.legend(frameon=True, fontsize=7.2, loc="upper left", title="clusters")
    ax.text(
        0.03,
        0.04,
        "No visual references\nlegend-heavy, weak hierarchy",
        transform=ax.transAxes,
        fontsize=8,
        color="#344054",
        bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#D0D5DD"},
    )
    ax.set_xlim(-4.9, 5.2)
    ax.set_ylim(-2.0, 4.1)


def draw_guided(ax: plt.Axes, rows: list[dict[str, str]], grouped: dict[str, list[dict[str, str]]]) -> None:
    all_x = [float(row["x"]) for row in rows]
    all_y = [float(row["y"]) for row in rows]
    ax.scatter(all_x, all_y, s=24, c="#D8DCE2", edgecolors="none", alpha=0.70, zorder=1)
    for cell_type, cell_rows in grouped.items():
        reference = [row for row in cell_rows if row["condition"] == "reference"]
        disease = [row for row in cell_rows if row["condition"] == "disease"]
        color = CELL_COLORS[cell_type]
        ax.scatter(
            [float(row["x"]) for row in reference],
            [float(row["y"]) for row in reference],
            s=32,
            c=color,
            edgecolors="white",
            linewidths=0.45,
            alpha=0.92,
            zorder=3,
        )
        ax.scatter(
            [float(row["x"]) for row in disease],
            [float(row["y"]) for row in disease],
            s=42,
            c=color,
            edgecolors="#1F2933",
            linewidths=0.62,
            alpha=0.96,
            zorder=4,
        )
        x, y = centroid(cell_rows)
        ax.text(x, y + 0.34, cell_type, ha="center", va="bottom", color="#202A33", fontsize=7.6, weight="medium")

    ax.annotate(
        "activation gradient",
        xy=(3.75, 2.08),
        xytext=(2.45, 3.47),
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": "#2F3A45"},
        color="#2F3A45",
        fontsize=8,
        ha="center",
    )
    ax.set_title("After: AgentFigureGallery-guided", fontsize=12, weight="bold")
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_xlim(-4.9, 5.2)
    ax.set_ylim(-2.0, 4.1)
    ax.set_xticks([-4, -2, 0, 2, 4])
    ax.set_yticks([-1, 0, 1, 2, 3, 4])
    ax.tick_params(length=2.5, width=0.65, color="#3A4652")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#3A4652")
    ax.spines["bottom"].set_color("#3A4652")

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#ABB6C2", markeredgecolor="white", markersize=5.4, label="reference"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#ABB6C2", markeredgecolor="#1F2933", markersize=5.8, label="disease"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=7.6, handletextpad=0.4)


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    grouped = grouped_rows(rows)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "agentfiguregallery-before-after",
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.2), constrained_layout=True)
    fig.set_facecolor("white")
    for ax in axes:
        ax.set_facecolor("white")

    draw_baseline(axes[0], rows, grouped)
    draw_guided(axes[1], rows, grouped)
    fig.suptitle("Same data, different agent workflow", fontsize=13.5, weight="bold", color="#17202A")

    outputs = {
        "png": FIGURES / "before_after_benchmark.png",
        "pdf": FIGURES / "before_after_benchmark.pdf",
        "svg": FIGURES / "before_after_benchmark.svg",
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
