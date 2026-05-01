#!/usr/bin/env python3
"""Render the README demo GIF from committed preview assets."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "agentfiguregallery-demo.gif"
SIZE = (880, 500)
FPS_MS = 200


def pick_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


FONT = {
    "xs": pick_font(10),
    "sm": pick_font(12),
    "base": pick_font(14),
    "base_b": pick_font(14, True),
    "lg": pick_font(18, True),
    "xl": pick_font(22, True),
}


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str, outline: str = "", radius: int = 8, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline or None, width=width)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, font: str = "base", fill: str = "#1f2933") -> None:
    draw.text(xy, value, font=FONT[font], fill=fill)


def fit_preview(path: Path, box: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image = ImageOps.contain(image, box, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", box, "white")
    canvas.paste(image, ((box[0] - image.width) // 2, (box[1] - image.height) // 2))
    return canvas


def load_previews() -> list[tuple[str, Path]]:
    paths = [
        ROOT / "assets/packs/minimal/previews/embedding_plot/EMB-3663479D54.png",
        ROOT / "assets/packs/minimal/previews/embedding_plot/EMB-3928F88AD7.png",
        ROOT / "assets/packs/minimal/previews/embedding_plot/EMB-FE34642DA4.png",
    ]
    fallback = sorted((ROOT / "assets/packs/minimal/previews/embedding_plot").glob("*.*"))
    selected = paths if all(path.exists() for path in paths) else fallback[:3]
    return [(path.stem, path) for path in selected]


PREVIEWS = [(name, fit_preview(path, (206, 168))) for name, path in load_previews()]


def draw_button(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], label: str, active: bool = False, danger: bool = False) -> None:
    fill = "#d9f2ee" if active and not danger else "#fde3df" if active else "#ffffff"
    outline = "#0f766e" if active and not danger else "#b42318" if active else "#d9dde3"
    label_fill = "#064e46" if active and not danger else "#8a1f12" if active else "#24313c"
    rounded(draw, xy, fill, outline, radius=6)
    tw = draw.textlength(label, font=FONT["sm"])
    tx = xy[0] + (xy[2] - xy[0] - tw) / 2
    ty = xy[1] + 7
    draw.text((tx, ty), label, font=FONT["sm"], fill=label_fill)


def draw_cursor(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.polygon([(x, y), (x + 16, y + 28), (x + 20, y + 16), (x + 33, y + 15)], fill="#111827")
    draw.line([(x + 16, y + 28), (x + 23, y + 40)], fill="#111827", width=4)


def draw_sidebar(draw: ImageDraw.ImageDraw, phase: int) -> None:
    rounded(draw, (0, 0, 210, 500), "#ffffff", "#d9dde3", radius=0)
    rounded(draw, (20, 18, 60, 58), "#24313c", radius=8)
    text(draw, (29, 29), "AF", "base_b", "#ffffff")
    text(draw, (72, 22), "AgentFigureGallery", "base_b")
    text(draw, (72, 43), "taste memory for agents", "xs", "#667085")
    y = 86
    for label, value in [
        ("Plot Type", "embedding_plot"),
        ("Count", "50"),
        ("Strategy", "Explore"),
    ]:
        text(draw, (20, y), label, "sm", "#344054")
        rounded(draw, (20, y + 20, 190, y + 52), "#ffffff", "#d9dde3", radius=6)
        text(draw, (32, y + 28), value, "sm")
        y += 70
    text(draw, (20, y), "Task", "sm", "#344054")
    rounded(draw, (20, y + 20, 190, y + 88), "#ffffff", "#d9dde3", radius=6)
    for i, line in enumerate(wrap("Nature-style embedding map for cell atlas", width=22)):
        text(draw, (32, y + 28 + i * 15), line, "sm")
    draw_button(draw, (20, y + 104, 190, y + 138), "Generate", active=phase == 0)
    draw_button(draw, (20, y + 152, 190, y + 186), "Export Bundle", active=phase == 4)


def draw_topbar(draw: ImageDraw.ImageDraw, phase: int) -> None:
    title = "gallery_embedding_plot"
    meta = "embedding_plot | 50 candidates"
    if phase == 0:
        title = "Embedding references"
        meta = "query -> display -> prefer -> act"
    text(draw, (234, 18), title, "xl")
    text(draw, (234, 46), meta, "sm", "#667085")
    chips = [("All 50", False, False), ("Open 48", False, False), ("G Liked 1", phase >= 3, False), ("Rejected 1", phase >= 2, True)]
    x = 522
    for label, active, danger in chips:
        draw_button(draw, (x, 18, x + 78, 50), label, active=active, danger=danger)
        x += 86
    rounded(draw, (234, 74, 842, 110), "#ffffff", "#d9dde3", radius=6)
    text(draw, (250, 84), "Filter by id, repo, subtype, summary", "base", "#777777")


def draw_card(canvas: Image.Image, draw: ImageDraw.ImageDraw, x: int, y: int, name: str, image: Image.Image, idx: int, phase: int) -> None:
    status = "candidate"
    border = "#d9dde3"
    if idx == 0 and phase >= 2:
        status, border = "rejected", "#b42318"
    if idx == 1 and phase >= 3:
        status, border = "G liked", "#0f766e"
    rounded(draw, (x, y, x + 210, y + 334), "#ffffff", border, radius=8, width=2 if border != "#d9dde3" else 1)
    draw.rectangle((x + 1, y + 1, x + 209, y + 173), fill="#ffffff")
    if idx == 0 and phase >= 2:
        muted = Image.blend(image, Image.new("RGB", image.size, "#f4f4f4"), 0.55)
        canvas.paste(muted, (x + 2, y + 2))
        draw.text((x + 60, y + 76), "G Reject", font=FONT["lg"], fill="#b42318")
    else:
        canvas.paste(image, (x + 2, y + 2))
    draw.line((x, y + 174, x + 210, y + 174), fill="#d9dde3")
    text(draw, (x + 14, y + 190), name[:13], "base_b")
    rounded(draw, (x + 136, y + 187, x + 194, y + 210), "#f2f4f7", radius=12)
    text(draw, (x + 147, y + 193), status, "xs", "#667085")
    text(draw, (x + 14, y + 220), "mini-atlas | score 80", "sm", "#344054")
    text(draw, (x + 14, y + 240), "embedding reference", "sm", "#667085")
    actions_y = y + 274
    labels = ["Like", "Reject", "Select", "Clear"]
    for i, label in enumerate(labels):
        draw_button(draw, (x + 12 + i * 48, actions_y, x + 54 + i * 48, actions_y + 28), label)
    draw_button(draw, (x + 12, actions_y + 36, x + 74, actions_y + 64), "G Like", active=(idx == 1 and phase >= 3))
    draw_button(draw, (x + 80, actions_y + 36, x + 142, actions_y + 64), "G Reject", active=(idx == 0 and phase >= 2), danger=True)


def draw_toast(draw: ImageDraw.ImageDraw, phase: int) -> None:
    if phase < 4:
        return
    rounded(draw, (490, 398, 842, 470), "#24313c", radius=8)
    text(draw, (510, 416), "Bundle exported", "lg", "#ffffff")
    text(draw, (510, 444), "selected_references -> upstream_agent_prompt", "sm", "#d9f2ee")


def render_frame(frame_index: int) -> Image.Image:
    phase = min(4, frame_index // 8)
    frame = Image.new("RGB", SIZE, "#f6f7f9")
    draw = ImageDraw.Draw(frame)
    draw_sidebar(draw, phase)
    draw_topbar(draw, phase)
    if phase == 0:
        rounded(draw, (274, 185, 800, 306), "#ffffff", "#d9dde3", radius=8)
        text(draw, (310, 212), "Generate visual candidates before writing code", "xl")
        text(draw, (310, 250), "Let the human teach preference once; let the agent reuse it.", "base", "#667085")
    else:
        for i, (name, image) in enumerate(PREVIEWS):
            draw_card(frame, draw, 230 + i * 218, 118, name, image, i, phase)
    cursor_paths = [(152, 356), (250, 362), (354, 406), (500, 406), (126, 404)]
    cx, cy = cursor_paths[phase]
    wiggle = (frame_index % 4) - 1
    draw_cursor(draw, cx + wiggle, cy)
    draw_toast(draw, phase)
    return frame


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [render_frame(i).convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for i in range(40)]
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=FPS_MS,
        loop=0,
        disposal=2,
    )
    print(f"wrote: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
