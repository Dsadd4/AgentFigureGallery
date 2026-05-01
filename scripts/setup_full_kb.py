#!/usr/bin/env python3
"""One-command AgentFigureGallery KB setup.

This command downloads a named asset pack, unpacks it when needed, and writes a
small local config file that tells agents which pack is active.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", default="public-preview", help="Pack name in the resource manifest.")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifests" / "resource_manifest.json")
    parser.add_argument("--manifest-url", help="Remote resource manifest URL.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "download_assets.py"),
        "--pack",
        args.pack,
        "--root",
        str(args.root),
        "--unpack",
    ]
    if args.manifest_url:
        cmd.extend(["--manifest-url", args.manifest_url])
    else:
        cmd.extend(["--manifest", str(args.manifest)])
    if args.dry_run:
        cmd.append("--dry-run")
    if args.force:
        cmd.append("--force")

    result = subprocess.run(cmd, cwd=args.root, check=False)
    if result.returncode != 0:
        return result.returncode

    config = {
        "schema_version": "agentfiguregallery.local_config.v1",
        "configured_at": utc_now(),
        "active_pack": args.pack,
        "root": str(args.root.resolve()),
        "manifest": str(args.manifest_url or args.manifest),
        "expected_index": "data/reference_candidate_index.json",
        "serve_command": "agentfiguregallery gallery --plot-type heatmap_matrix --limit 50 --serve",
    }
    if not args.dry_run:
        write_json(args.root / ".agentfiguregallery" / "config.json", config)
        index_path = args.root / "data" / "reference_candidate_index.json"
        if not index_path.exists():
            print(f"warning: setup completed but candidate index is missing: {index_path}")
        else:
            print(f"configured pack: {args.pack}")
            print(f"candidate index: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
