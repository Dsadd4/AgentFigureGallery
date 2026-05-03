#!/usr/bin/env python3
"""Render one Nature-style smoke-test example for every plot type."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Ellipse, Rectangle
from PIL import Image, ImageDraw, ImageFont, ImageOps


EXAMPLE_DIR = Path(__file__).resolve().parent
ROOT = EXAMPLE_DIR.parents[1]
FIGURES_DIR = EXAMPLE_DIR / "figures"
DATA_DIR = EXAMPLE_DIR / "source_data"

INK = "#1F2329"
GRID = "#D9DEE6"
MID = "#7B8794"
LIGHT = "#E8ECF1"
NPG = ["#3C5488", "#00A087", "#E64B35", "#F39B7F", "#8491B4", "#91D1C2", "#7E6148", "#B09C85"]
TOL = ["#332288", "#88CCEE", "#44AA99", "#117733", "#DDCC77", "#CC6677", "#AA4499", "#999933"]


def apply_nature_style(figsize: tuple[float, float]) -> None:
    plt.rcParams.update(
        {
            "figure.figsize": figsize,
            "figure.dpi": 160,
            "savefig.dpi": 320,
            "axes.linewidth": 0.95,
            "axes.labelsize": 10.5,
            "axes.titlesize": 11.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 9.2,
            "ytick.labelsize": 9.2,
            "legend.fontsize": 8.4,
            "font.family": "DejaVu Sans",
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8")


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    keys: list[str] = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    strip_trailing_whitespace(path)


def save_figure(fig: plt.Figure, stem: str, rows: list[dict[str, object]] | None = None) -> dict[str, str]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    png = FIGURES_DIR / f"{stem}.png"
    pdf = FIGURES_DIR / f"{stem}.pdf"
    svg = FIGURES_DIR / f"{stem}.svg"
    fig.savefig(png, bbox_inches="tight", dpi=320, facecolor=fig.get_facecolor())
    fig.savefig(pdf, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    strip_trailing_whitespace(svg)
    if rows is not None:
        write_rows(DATA_DIR / f"{stem}.csv", rows)
    plt.close(fig)
    return {"png": str(png), "pdf": str(pdf), "svg": str(svg)}


def add_panel_label(ax: plt.Axes, label: str, x: float = -0.12, y: float = 1.04) -> None:
    ax.text(x, y, label, transform=ax.transAxes, fontsize=15, fontweight="bold", color=INK, ha="left", va="bottom")


def add_sig(ax: plt.Axes, x1: float, x2: float, y: float, text: str, dy: float = 0.035) -> None:
    ax.plot([x1, x1, x2, x2], [y - dy * 0.35, y, y, y - dy * 0.35], color=INK, lw=0.95, clip_on=False)
    ax.text((x1 + x2) / 2.0, y + dy * 0.18, text, ha="center", va="bottom", fontsize=7.8, color=INK)


def rotated_points(rng: np.random.Generator, center: tuple[float, float], scale: tuple[float, float], angle_deg: float, n: int) -> np.ndarray:
    theta = np.deg2rad(angle_deg)
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    pts = rng.normal(size=(n, 2)) * np.array(scale)
    return pts @ rot.T + np.array(center)


def render_bar_chart() -> dict[str, str]:
    rng = np.random.default_rng(11)
    apply_nature_style((4.5, 3.35))
    fig, ax = plt.subplots()
    categories = ["Control", "Stress", "Rescue", "Reference"]
    params = {
        "Control": (0.43, 0.045),
        "Stress": (0.61, 0.055),
        "Rescue": (0.72, 0.048),
        "Reference": (0.55, 0.040),
    }
    colors = ["#AAB3BE", NPG[0], NPG[2], NPG[1]]
    rows: list[dict[str, object]] = []
    means, sems = [], []
    for category in categories:
        mean, sd = params[category]
        values = np.clip(rng.normal(mean, sd, 9), 0.15, 0.95)
        means.append(float(np.mean(values)))
        sems.append(float(np.std(values, ddof=1) / np.sqrt(len(values))))
        for idx, value in enumerate(values, start=1):
            rows.append({"category": category, "replicate": idx, "value": float(value)})
    x = np.arange(len(categories), dtype=float)
    bars = ax.bar(x, means, yerr=sems, width=0.64, color=colors, edgecolor=colors, capsize=3.0, linewidth=0.8, alpha=0.92, zorder=2)
    for idx, category in enumerate(categories):
        values = [float(row["value"]) for row in rows if row["category"] == category]
        jitter = rng.normal(0, 0.045, len(values))
        ax.scatter(np.full(len(values), x[idx]) + jitter, values, s=18, color=INK, alpha=0.55, linewidths=0, zorder=3)
    for bar, value in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.026, f"{value:.2f}", ha="center", va="bottom", fontsize=8.0, fontweight="semibold")
    add_sig(ax, x[0], x[2], 0.84, "P = 0.002")
    ax.set_title("Grouped Response Summary")
    ax.set_ylabel("Relative signal")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 0.92)
    ax.grid(True, axis="y", color=GRID, lw=0.75, ls="--", zorder=0)
    fig.tight_layout()
    return save_figure(fig, "bar_chart_example", rows)


def render_benchmark_performance() -> dict[str, str]:
    apply_nature_style((5.8, 3.7))
    fig, ax = plt.subplots()
    metrics = ["Top-1", "Top-5", "Top-10", "Top-20"]
    methods = ["Baseline", "AtlasNet", "AgentFit", "AgentFit + RT"]
    values = {
        "Top-1": [22.1, 27.8, 30.4, 33.1],
        "Top-5": [38.0, 44.5, 48.8, 51.2],
        "Top-10": [47.6, 54.0, 58.1, 61.0],
        "Top-20": [57.4, 63.1, 67.3, 70.2],
    }
    errs = {
        "Top-1": [1.1, 1.0, 1.0, 0.9],
        "Top-5": [1.3, 1.2, 1.1, 1.0],
        "Top-10": [1.5, 1.2, 1.1, 1.1],
        "Top-20": [1.4, 1.3, 1.2, 1.0],
    }
    color_map = {"Baseline": "#BCC5D0", "AtlasNet": NPG[0], "AgentFit": NPG[1], "AgentFit + RT": NPG[2]}
    rows: list[dict[str, object]] = []
    x = np.arange(len(metrics), dtype=float)
    width = 0.18
    offsets = np.linspace(-1.5 * width, 1.5 * width, len(methods))
    for midx, method in enumerate(methods):
        ys = [values[metric][midx] for metric in metrics]
        es = [errs[metric][midx] for metric in metrics]
        bars = ax.bar(x + offsets[midx], ys, yerr=es, width=width * 0.94, color=color_map[method], edgecolor=color_map[method], linewidth=0.8, capsize=2.5, alpha=0.92, label=method, zorder=2)
        for metric, value, err in zip(metrics, ys, es):
            rows.append({"metric": metric, "method": method, "score": value, "sem": err})
        if method == "AgentFit + RT":
            for bar, value in zip(bars, ys):
                ax.text(bar.get_x() + bar.get_width() / 2, value + 2.0, f"{value:.1f}", ha="center", va="bottom", fontsize=7.4, color=INK, fontweight="bold")
    ax.set_title("Cross-modal Retrieval Benchmark")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 78)
    ax.grid(True, axis="y", color=GRID, lw=0.75, ls="--", zorder=0)
    ax.legend(frameon=False, loc="upper left", ncol=2)
    fig.tight_layout()
    return save_figure(fig, "benchmark_performance_example", rows)


def render_box_violin_distribution() -> dict[str, str]:
    rng = np.random.default_rng(19)
    apply_nature_style((5.0, 3.65))
    fig, ax = plt.subplots()
    groups = ["Vehicle", "Low dose", "High dose"]
    specs = [(0.54, 0.07), (0.63, 0.08), (0.72, 0.06)]
    colors = [NPG[0], NPG[1], NPG[2]]
    data = [np.clip(rng.normal(mean, sd, 48), 0.25, 0.95) for mean, sd in specs]
    rows = [{"group": group, "sample": idx + 1, "score": float(value)} for group, values in zip(groups, data) for idx, value in enumerate(values)]
    positions = np.arange(len(groups), dtype=float)
    parts = ax.violinplot(data, positions=positions, widths=0.72, showmeans=False, showmedians=False, showextrema=False)
    for body, color in zip(parts["bodies"], colors):
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_alpha(0.28)
        body.set_linewidth(0.8)
    bp = ax.boxplot(data, positions=positions, widths=0.23, patch_artist=True, showfliers=False, medianprops={"color": INK, "linewidth": 1.2}, whiskerprops={"color": INK, "linewidth": 0.9}, capprops={"color": INK, "linewidth": 0.9})
    for box, color in zip(bp["boxes"], colors):
        box.set_facecolor(mcolors.to_rgba(color, 0.78))
        box.set_edgecolor(color)
    for xpos, values, color in zip(positions, data, colors):
        jitter = rng.normal(0, 0.045, len(values))
        ax.scatter(np.full(len(values), xpos) + jitter, values, s=10, color=color, alpha=0.48, linewidths=0, zorder=3)
        ax.scatter(xpos, float(np.mean(values)), marker="D", s=34, color="white", edgecolor=INK, linewidth=1.0, zorder=5)
    add_sig(ax, 0, 2, 0.93, "P < 0.001", dy=0.04)
    ax.set_title("Distribution Shift Across Conditions")
    ax.set_ylabel("Normalized phenotype score")
    ax.set_xticks(positions)
    ax.set_xticklabels(groups)
    ax.set_ylim(0.25, 1.0)
    ax.grid(True, axis="y", color=GRID, lw=0.75, ls="--", zorder=0)
    fig.tight_layout()
    return save_figure(fig, "box_violin_distribution_example", rows)


def render_embedding_plot() -> dict[str, str]:
    rng = np.random.default_rng(23)
    apply_nature_style((5.0, 4.0))
    fig, ax = plt.subplots()
    specs = [
        ("Radial glia", (-3.1, 1.2), (0.78, 0.28), 18, TOL[0]),
        ("IPC", (-1.3, 2.0), (0.62, 0.24), -18, TOL[4]),
        ("Excitatory", (0.9, 1.3), (0.84, 0.34), 20, TOL[2]),
        ("Inhibitory", (2.8, 0.1), (0.72, 0.27), -22, TOL[5]),
        ("Glia", (-0.8, -1.0), (0.70, 0.26), 8, TOL[1]),
        ("Oligo", (1.6, -1.5), (0.56, 0.20), -35, TOL[3]),
    ]
    rows: list[dict[str, object]] = []
    for label, center, scale, angle, color in specs:
        pts = rotated_points(rng, center, scale, angle, 220)
        ax.scatter(pts[:, 0], pts[:, 1], s=7, color=color, alpha=0.36, edgecolors="none", rasterized=True)
        med = np.median(pts, axis=0)
        cov = np.cov(pts[:, 0], pts[:, 1])
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        vals, vecs = vals[order], vecs[:, order]
        theta = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
        ax.add_patch(Ellipse(med, 4.1 * np.sqrt(vals[0]), 4.1 * np.sqrt(vals[1]), angle=theta, fill=False, lw=1.0, ec=color, alpha=0.9))
        ax.text(med[0], med[1], label, fontsize=8.1, fontweight="bold", color=color, ha="center", va="center", path_effects=[pe.withStroke(linewidth=3, foreground="white")])
        rows.extend({"cell_type": label, "umap1": float(x), "umap2": float(y)} for x, y in pts)
    ax.set_title("Cell Atlas Embedding")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal", adjustable="box")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    return save_figure(fig, "embedding_plot_example", rows)


def render_heatmap_matrix() -> dict[str, str]:
    rng = np.random.default_rng(29)
    apply_nature_style((5.1, 4.05))
    fig, ax = plt.subplots()
    rows_lab = ["IFNG", "GZMB", "CXCL10", "IL7R", "LST1", "MS4A1"]
    cols_lab = ["Ctrl", "Early", "Mid", "Late", "Rescue"]
    base = np.array(
        [
            [-0.4, 0.6, 1.2, 1.6, 0.4],
            [-0.7, 0.5, 1.4, 1.8, 0.6],
            [-0.2, 0.7, 1.1, 1.5, 0.2],
            [0.9, 0.4, -0.1, -0.6, 0.5],
            [0.3, 0.5, 0.8, 1.0, 0.4],
            [0.8, 0.3, -0.3, -0.8, 0.2],
        ]
    )
    matrix = base + rng.normal(0, 0.12, base.shape)
    rows = [{"gene": rows_lab[i], "state": cols_lab[j], "z_score": float(matrix[i, j])} for i in range(matrix.shape[0]) for j in range(matrix.shape[1])]
    norm = mcolors.TwoSlopeNorm(vmin=-2.0, vcenter=0.0, vmax=2.0)
    im = ax.imshow(matrix, cmap="RdBu_r", norm=norm, aspect="auto")
    ax.set_title("Immune Program Delta Matrix")
    ax.set_xticks(np.arange(len(cols_lab)))
    ax.set_xticklabels(cols_lab)
    ax.set_yticks(np.arange(len(rows_lab)))
    ax.set_yticklabels(rows_lab)
    ax.set_xticks(np.arange(-0.5, len(cols_lab), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows_lab), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:+.1f}", ha="center", va="center", fontsize=7.3, color=INK if abs(matrix[i, j]) < 1.2 else "white")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.035)
    cb.outline.set_visible(False)
    cb.set_label("Row z-score", fontsize=8.5)
    fig.tight_layout()
    return save_figure(fig, "heatmap_matrix_example", rows)


def render_line_chart() -> dict[str, str]:
    rng = np.random.default_rng(31)
    apply_nature_style((5.2, 3.45))
    fig, ax = plt.subplots()
    steps = np.array([0, 20, 40, 60, 80, 100], dtype=float)
    series = {
        "Baseline": (np.array([42, 50, 56, 60, 62, 63], dtype=float), "#BCC5D0"),
        "AgentFit": (np.array([43, 55, 64, 70, 74, 76], dtype=float), NPG[0]),
        "AgentFit + RT": (np.array([43, 58, 68, 76, 82, 85], dtype=float), NPG[2]),
    }
    rows: list[dict[str, object]] = []
    for name, (ys, color) in series.items():
        band = np.linspace(3.2, 1.4, len(steps)) + rng.normal(0, 0.12, len(steps))
        ax.fill_between(steps, ys - band, ys + band, color=color, alpha=0.13, linewidth=0)
        ax.plot(steps, ys, color=color, lw=2.0 if name == "AgentFit + RT" else 1.7, marker="o", ms=4.8, label=name, zorder=3)
        ax.annotate(name, (steps[-1], ys[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.0, color=color)
        rows.extend({"step": int(step), "method": name, "score": float(y), "ci": float(b)} for step, y, b in zip(steps, ys, band))
    ax.axhline(80, color=GRID, ls="--", lw=0.9, zorder=1)
    ax.text(2, 81.2, "deployment threshold", fontsize=7.8, color=MID)
    ax.set_title("Training Progression")
    ax.set_xlabel("Training step (%)")
    ax.set_ylabel("Validation score (%)")
    ax.set_xlim(-2, 114)
    ax.set_ylim(36, 91)
    ax.grid(True, axis="y", color=GRID, lw=0.75, ls="--", zorder=0)
    fig.tight_layout()
    return save_figure(fig, "line_chart_example", rows)


def render_scatter_plot() -> dict[str, str]:
    rng = np.random.default_rng(37)
    apply_nature_style((4.4, 4.0))
    fig, ax = plt.subplots()
    x = rng.uniform(0.15, 0.95, 130)
    y = np.clip(0.08 + 0.86 * x + rng.normal(0, 0.055, len(x)), 0.05, 1.0)
    residual = y - x
    highlight = np.abs(residual) > 0.13
    labels = np.array([""] * len(x), dtype=object)
    labels[np.where(highlight)[0][:5]] = ["S12", "S27", "S44", "S81", "S99"]
    rows = [{"observed": float(a), "predicted": float(b), "highlight": bool(h), "label": str(l)} for a, b, h, l in zip(x, y, highlight, labels)]
    ax.scatter(x[~highlight], y[~highlight], s=23, color=NPG[0], alpha=0.42, edgecolors="none", zorder=2)
    ax.scatter(x[highlight], y[highlight], s=42, color=NPG[2], alpha=0.92, edgecolors="white", linewidths=0.6, zorder=3)
    ax.plot([0, 1], [0, 1], ls="--", lw=1.0, color="#AAB3BE", zorder=1)
    slope, intercept = np.polyfit(x, y, 1)
    xs = np.linspace(0.1, 1.0, 200)
    ax.plot(xs, slope * xs + intercept, lw=1.4, color=INK, zorder=2)
    for a, b, label in zip(x, y, labels):
        if label:
            ax.text(a + 0.015, b + 0.01, str(label), fontsize=7.8, color=INK, path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    corr = float(np.corrcoef(x, y)[0, 1])
    ax.text(0.13, 0.91, f"r = {corr:.2f}", fontsize=8.5, color=INK)
    ax.set_title("Prediction Agreement")
    ax.set_xlabel("Observed score")
    ax.set_ylabel("Predicted score")
    ax.set_xlim(0.1, 1.0)
    ax.set_ylim(0.1, 1.0)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color=GRID, lw=0.75, ls="--", zorder=0)
    fig.tight_layout()
    return save_figure(fig, "scatter_plot_example", rows)


def add_scale_bar(ax: plt.Axes, x0: float, y0: float, length: float, label: str, color: str = INK) -> None:
    ax.plot([x0, x0 + length], [y0, y0], color=color, lw=2.0, solid_capstyle="butt", zorder=10)
    ax.text(x0 + length / 2, y0 + 2.4, label, ha="center", va="bottom", fontsize=7.5, color=color, zorder=11)


def render_spatial_map() -> dict[str, str]:
    rng = np.random.default_rng(41)
    apply_nature_style((7.6, 5.8))
    fig = plt.figure()
    gs = GridSpec(2, 2, figure=fig, wspace=0.17, hspace=0.25)
    axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
    xx, yy = np.meshgrid(np.linspace(5, 95, 42), np.linspace(6, 92, 36))
    x = xx.ravel() + rng.normal(0, 0.75, xx.size)
    y = yy.ravel() + rng.normal(0, 0.75, yy.size)
    mask = ((x - 52) / 42) ** 2 + ((y - 50) / 34) ** 2 + 0.08 * np.sin(x / 7) < 1.0
    x, y = x[mask], y[mask]
    abundance = 0.8 * np.exp(-((x - 36) ** 2 + (y - 68) ** 2) / 760) + 0.55 * np.exp(-((x - 70) ** 2 + (y - 34) ** 2) / 620) + rng.normal(0, 0.035, len(x))
    delta = 0.95 * np.exp(-((x - 72) ** 2 + (y - 30) ** 2) / 560) - 0.75 * np.exp(-((x - 34) ** 2 + (y - 66) ** 2) / 610) + rng.normal(0, 0.06, len(x))
    region = np.where(y > 63, "Cortex", np.where(x < 38, "White matter", np.where(y < 34, "Striatum", "Stroma")))
    hub = np.full(len(x), "Background", dtype=object)
    hub[((x - 58) ** 2 + (y - 58) ** 2) < 135] = "Peri-tumoral"
    hub[((x - 72) ** 2 + (y - 38) ** 2) < 110] = "Stromal hub"
    hub[((x - 31) ** 2 + (y - 31) ** 2) < 105] = "Immune hub"
    rows = [{"x": float(a), "y": float(b), "abundance": float(c), "delta": float(d), "region": str(e), "hub": str(f)} for a, b, c, d, e, f in zip(x, y, abundance, delta, region, hub)]

    panels = [
        ("a", "Tissue abundance", abundance, "continuous", "Aging score"),
        ("b", "Intervention delta", delta, "delta", "Delta age"),
        ("c", "Region atlas", region, "region", ""),
        ("d", "Hub overlay", hub, "hub", ""),
    ]
    region_colors = {"Cortex": TOL[0], "White matter": TOL[1], "Striatum": TOL[2], "Stroma": TOL[5]}
    hub_colors = {"Background": "#EFF2F5", "Peri-tumoral": NPG[2], "Stromal hub": NPG[1], "Immune hub": NPG[0]}
    for ax, (label, title, values, kind, cb_label) in zip(axes, panels):
        if kind == "continuous":
            sc = ax.scatter(x, y, c=values, cmap=mcolors.LinearSegmentedColormap.from_list("npg_seq", ["#F7F8FA", "#A1B4D1", NPG[0]]), s=15, linewidths=0, zorder=3)
            cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
            cb.outline.set_visible(False)
            cb.set_label(cb_label, fontsize=7.8)
        elif kind == "delta":
            norm = mcolors.TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=1.0)
            cmap = mcolors.LinearSegmentedColormap.from_list("npg_div", [NPG[0], "#F7F8FA", NPG[2]])
            sc = ax.scatter(x, y, c=values, cmap=cmap, norm=norm, s=15, linewidths=0, zorder=3)
            cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
            cb.outline.set_visible(False)
            cb.set_label(cb_label, fontsize=7.8)
            ax.annotate("rescue zone", xy=(34, 66), xytext=(12, 88), fontsize=7.5, arrowprops=dict(arrowstyle="-", color=INK, lw=0.8), path_effects=[pe.withStroke(linewidth=3, foreground="white")])
        elif kind == "region":
            for group, color in region_colors.items():
                m = values == group
                ax.scatter(x[m], y[m], s=15, color=color, alpha=0.9, linewidths=0, label=group)
            for group in ["Cortex", "White matter", "Striatum"]:
                m = values == group
                ax.text(float(np.median(x[m])), float(np.median(y[m])), group, color=region_colors[group], fontsize=7.4, fontweight="bold", ha="center", va="center", path_effects=[pe.withStroke(linewidth=3, foreground="white")])
        else:
            ax.scatter(x, y, s=12, color="#F2F4F7", linewidths=0, zorder=1)
            for group in ["Peri-tumoral", "Stromal hub", "Immune hub"]:
                m = values == group
                ax.scatter(x[m], y[m], s=24, color=hub_colors[group], alpha=0.92, linewidths=0.25, edgecolors="white", label=group, zorder=3)
            ax.legend(frameon=False, loc="lower right", fontsize=7.3)
        add_panel_label(ax, label, x=-0.08, y=1.03)
        ax.set_title(title, loc="left", pad=7)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
        for spine in ax.spines.values():
            spine.set_visible(False)
        add_scale_bar(ax, 70, 8, 16, "250 um")
    fig.suptitle("Spatial Tissue Map", x=0.02, y=0.99, ha="left", fontsize=13, fontweight="bold", color=INK)
    return save_figure(fig, "spatial_map_example", rows)


def normalize(image: np.ndarray, low: float = 1.0, high: float = 99.6, gamma: float = 1.0) -> np.ndarray:
    lo, hi = np.percentile(image, [low, high])
    out = np.clip((image - lo) / max(hi - lo, 1e-6), 0, 1)
    return out ** (1.0 / gamma)


def make_microscopy_channels() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(47)
    n = 256
    yy, xx = np.mgrid[0:n, 0:n]
    dapi = rng.normal(0.015, 0.01, (n, n))
    cd8 = rng.normal(0.01, 0.008, (n, n))
    ki67 = rng.normal(0.01, 0.008, (n, n))
    mask = np.zeros((n, n), dtype=bool)
    centers = rng.uniform(18, n - 18, (120, 2))
    cd8_idx = set(rng.choice(np.arange(120), 32, replace=False).tolist())
    ki67_idx = set(rng.choice(np.arange(120), 24, replace=False).tolist())
    for idx, (cx, cy) in enumerate(centers):
        r = rng.uniform(4.0, 7.2)
        dist2 = (xx - cx) ** 2 + (yy - cy) ** 2
        dapi += rng.uniform(0.55, 1.0) * np.exp(-dist2 / (2 * (r * 0.62) ** 2))
        mask |= dist2 < (r * 1.35) ** 2
        if idx in cd8_idx:
            cd8 += rng.uniform(0.45, 0.9) * np.exp(-dist2 / (2 * (r * 1.2) ** 2))
        if idx in ki67_idx:
            ki67 += rng.uniform(0.50, 0.95) * np.exp(-dist2 / (2 * (r * 0.82) ** 2))
    inner = mask.copy()
    inner[1:-1, 1:-1] &= mask[:-2, 1:-1] & mask[2:, 1:-1] & mask[1:-1, :-2] & mask[1:-1, 2:]
    boundary = mask & ~inner
    return normalize(dapi, gamma=1.0), normalize(cd8, gamma=1.1), normalize(ki67, gamma=1.0), boundary


def microscopy_rgb(dapi: np.ndarray, cd8: np.ndarray, ki67: np.ndarray) -> np.ndarray:
    rgb = np.zeros((*dapi.shape, 3), dtype=float)
    rgb[..., 2] += dapi * 0.95
    rgb[..., 1] += cd8 * 0.9
    rgb[..., 0] += ki67 * 0.95
    rgb[..., 0] += dapi * 0.12
    return np.clip(rgb, 0, 1)


def render_microscopy_panel() -> dict[str, str]:
    apply_nature_style((7.0, 5.7))
    dapi, cd8, ki67, boundary = make_microscopy_channels()
    rgb = microscopy_rgb(dapi, cd8, ki67)
    fig = plt.figure(facecolor="#FAFBFD")
    gs = GridSpec(2, 2, figure=fig, wspace=0.08, hspace=0.18)
    axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(2)]
    crop = (92, 70, 102, 102)
    panels = [
        ("a", "DAPI", np.dstack([dapi * 0.15, dapi * 0.25, dapi]), []),
        ("b", "Composite", rgb, [("DAPI", "#77AADD"), ("CD8", "#55A868"), ("Ki67", "#E06C75")]),
        ("c", "Segmentation overlay", rgb.copy(), [("boundary", "white")]),
        ("d", "Zoomed niche", rgb[crop[1] : crop[1] + crop[3], crop[0] : crop[0] + crop[2]], [("CD8-rich", "#55A868"), ("Ki67-high", "#E06C75")]),
    ]
    for ax, (label, title, image, labels) in zip(axes, panels):
        ax.imshow(image, interpolation="nearest")
        if label == "c":
            overlay = np.zeros((*boundary.shape, 4), dtype=float)
            overlay[..., :3] = 1.0
            overlay[..., 3] = boundary.astype(float) * 0.85
            ax.imshow(overlay, interpolation="nearest")
            ax.add_patch(Rectangle((crop[0], crop[1]), crop[2], crop[3], fill=False, ec=NPG[2], lw=1.5))
        if label == "d":
            b = boundary[crop[1] : crop[1] + crop[3], crop[0] : crop[0] + crop[2]]
            overlay = np.zeros((*b.shape, 4), dtype=float)
            overlay[..., :3] = 1.0
            overlay[..., 3] = b.astype(float) * 0.85
            ax.imshow(overlay, interpolation="nearest")
            ax.annotate("CD8-rich niche", xy=(40, 58), xytext=(10, 18), color="white", fontsize=8.0, arrowprops=dict(arrowstyle="-", color="white", lw=0.9), path_effects=[pe.withStroke(linewidth=2.5, foreground=INK)])
            ax.annotate("Ki67-high", xy=(70, 36), xytext=(55, 12), color="white", fontsize=8.0, arrowprops=dict(arrowstyle="-", color="white", lw=0.9), path_effects=[pe.withStroke(linewidth=2.5, foreground=INK)])
        ax.set_title(title, loc="left", pad=7, color=INK, fontweight="bold")
        add_panel_label(ax, label, x=-0.08, y=1.03)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        width = image.shape[1]
        height = image.shape[0]
        bar_len = 52 if label != "d" else 36
        ax.plot([width * 0.68, width * 0.68 + bar_len], [height * 0.90, height * 0.90], color="white", lw=2.2, solid_capstyle="butt")
        ax.text(width * 0.68 + bar_len / 2, height * 0.84, "50 um" if label != "d" else "20 um", color="white", fontsize=7.4, ha="center", va="bottom", path_effects=[pe.withStroke(linewidth=2.5, foreground=INK)])
        for idx, (text, color) in enumerate(labels):
            ax.text(0.03, 0.96 - idx * 0.08, text, transform=ax.transAxes, fontsize=7.8, fontweight="bold", color=color, ha="left", va="top", path_effects=[pe.withStroke(linewidth=2.5, foreground=INK)])
    fig.suptitle("Microscopy Panel", x=0.03, y=0.995, ha="left", fontsize=13, fontweight="bold", color=INK)
    rows = [{"asset": "synthetic_microscopy", "height": int(dapi.shape[0]), "width": int(dapi.shape[1]), "channels": "DAPI,CD8,Ki67,boundary"}]
    return save_figure(fig, "microscopy_panel_example", rows)


def render_multi_panel_figure(previous: dict[str, dict[str, str]]) -> dict[str, str]:
    apply_nature_style((9.2, 6.8))
    fig = plt.figure()
    gs = GridSpec(3, 3, figure=fig, wspace=0.12, hspace=0.22, left=0.04, right=0.985, top=0.90, bottom=0.06)
    panel_specs = [
        ("a", "Embedding overview", previous["embedding_plot"]["png"], (slice(0, 2), slice(0, 2))),
        ("b", "Benchmark snapshot", previous["benchmark_performance"]["png"], (slice(0, 1), slice(2, 3))),
        ("c", "Expression matrix", previous["heatmap_matrix"]["png"], (slice(1, 2), slice(2, 3))),
        ("d", "Microscopy evidence", previous["microscopy_panel"]["png"], (slice(2, 3), slice(0, 2))),
    ]
    rows: list[dict[str, object]] = []
    for label, title, path, (rs, cs) in panel_specs:
        ax = fig.add_subplot(gs[rs, cs])
        image = plt.imread(path)
        ax.imshow(image)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(title, loc="left", pad=5, fontsize=9.5, fontweight="bold")
        add_panel_label(ax, label, x=-0.055 if label in {"a", "d"} else -0.12, y=1.02)
        rows.append({"panel": label, "source_png": repo_relative(path), "title": title})
    ax = fig.add_subplot(gs[2, 2])
    ax.axis("off")
    ax.text(0.00, 0.95, "e", fontsize=15, fontweight="bold", color=INK, ha="left", va="top")
    ax.text(0.12, 0.92, "Assembly notes", fontsize=10.5, fontweight="bold", color=NPG[0], ha="left", va="top")
    notes = [
        "One anchor panel carries the main spatial story.",
        "Benchmark and matrix panels use tighter hierarchy.",
        "Image evidence remains readable at print scale.",
    ]
    for idx, note in enumerate(notes):
        ax.text(0.12, 0.72 - idx * 0.18, f"- {note}", fontsize=8.6, color=INK, ha="left", va="top", wrap=True)
    rows.append({"panel": "e", "source_png": "", "title": "Assembly notes"})
    fig.text(0.04, 0.975, "Integrated multi-panel figure", fontsize=14, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.04, 0.945, "Smoke-test composition from generated AgentFigureGallery plot-type examples.", fontsize=8.8, color=MID, ha="left", va="top")
    return save_figure(fig, "multi_panel_figure_example", rows)


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_contact_sheet(results: dict[str, dict[str, str]]) -> str:
    order = [
        "bar_chart",
        "benchmark_performance",
        "box_violin_distribution",
        "embedding_plot",
        "heatmap_matrix",
        "line_chart",
        "microscopy_panel",
        "multi_panel_figure",
        "scatter_plot",
        "spatial_map",
    ]
    label_font = load_font(30)
    small_font = load_font(18)
    cell_w, cell_h = 430, 300
    margin, label_h = 28, 46
    cols, rows = 5, 2
    sheet = Image.new("RGB", (cols * cell_w + margin * 2, rows * cell_h + margin * 2 + 68), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, 16), "AgentFigureGallery plot-type smoke examples", font=label_font, fill=INK)
    draw.text((margin, 52), "PNG preview assembled from newly rendered examples; PDF/SVG are saved beside each PNG.", font=small_font, fill=MID)
    y0 = margin + 58
    for idx, key in enumerate(order):
        row, col = divmod(idx, cols)
        left = margin + col * cell_w
        top = y0 + row * cell_h
        draw.text((left + 8, top + 4), key, font=small_font, fill=INK)
        image = Image.open(results[key]["png"]).convert("RGB")
        thumb = ImageOps.contain(image, (cell_w - 22, cell_h - label_h - 16), method=Image.Resampling.LANCZOS)
        x = left + (cell_w - thumb.width) // 2
        y = top + label_h + (cell_h - label_h - thumb.height) // 2
        sheet.paste(thumb, (x, y))
        draw.rectangle([left, top, left + cell_w - 10, top + cell_h - 10], outline="#E1E6EE", width=1)
    out = FIGURES_DIR / "agentfiguregallery_plot_type_examples_preview.png"
    sheet.save(out, quality=95)
    return str(out)


def repo_relative(path: str | Path) -> str:
    return Path(path).resolve().relative_to(ROOT).as_posix()


def main() -> int:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, str]] = {}
    results["bar_chart"] = render_bar_chart()
    results["benchmark_performance"] = render_benchmark_performance()
    results["box_violin_distribution"] = render_box_violin_distribution()
    results["embedding_plot"] = render_embedding_plot()
    results["heatmap_matrix"] = render_heatmap_matrix()
    results["line_chart"] = render_line_chart()
    results["microscopy_panel"] = render_microscopy_panel()
    results["scatter_plot"] = render_scatter_plot()
    results["spatial_map"] = render_spatial_map()
    results["multi_panel_figure"] = render_multi_panel_figure(results)
    preview = make_contact_sheet(results)
    plot_types = {
        plot_type: {kind: repo_relative(path) for kind, path in paths.items()}
        for plot_type, paths in results.items()
    }
    manifest = {
        "description": "Codex-equipped AgentFigureGallery skill smoke test: one Nature-style example for each supported plot type.",
        "plot_types": plot_types,
        "preview_png": repo_relative(preview),
        "screenshots": {
            "codex_skill_discovered": repo_relative(EXAMPLE_DIR / "screenshots" / "codex-skill-discovered.png")
        },
        "source_data_dir": repo_relative(DATA_DIR),
    }
    manifest_path = EXAMPLE_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "figures_dir": repo_relative(FIGURES_DIR),
                "source_data_dir": repo_relative(DATA_DIR),
                "manifest": repo_relative(manifest_path),
                "preview_png": repo_relative(preview),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
