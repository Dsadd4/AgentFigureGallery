#!/usr/bin/env python3
"""Scan public AgentFigureGallery files for private-path signals."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_PATTERNS = [
    "massspec",
    "MSagent",
    "personalhpc",
    "personalhpcgpu",
    "aimslight",
    "yifanl/",
]

DEFAULT_SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "outputs",
    "scripts",
    "agentfiguregallery",
    "docs",
    "ExtendAgent",
    "assets/releases",
    "assets/packs/full-private",
}


def iter_files(root: Path, skip_dirs: set[str]):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        rel_parts = set(path.relative_to(root).parts)
        if any(skip in rel_parts or rel == skip or rel.startswith(skip + "/") for skip in skip_dirs):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pattern", action="append", default=[])
    parser.add_argument("--include-docs", action="store_true", help="Also scan docs and ExtendAgent instructions.")
    args = parser.parse_args()

    root = args.root.resolve()
    patterns = DEFAULT_PATTERNS + args.pattern
    skip_dirs = set(DEFAULT_SKIP_DIRS)
    if args.include_docs:
        skip_dirs.discard("docs")
        skip_dirs.discard("ExtendAgent")
    hits: list[tuple[str, str]] = []
    for path in iter_files(root, skip_dirs):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lower = text.lower()
        for pattern in patterns:
            if pattern.lower() in lower:
                hits.append((path.relative_to(root).as_posix(), pattern))

    if hits:
        for rel, pattern in hits[:200]:
            print(f"{rel}: {pattern}")
        print(f"private-path scan failed: {len(hits)} hits")
        return 1
    print("private-path scan passed: 0 hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
