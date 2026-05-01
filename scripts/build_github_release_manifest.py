#!/usr/bin/env python3
"""Build a resource manifest that downloads full-public assets from GitHub Releases."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "manifests" / "resource_manifest.json"
DEFAULT_OUTPUT = ROOT / "manifests" / "resource_manifest.github-api.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def release_assets(repo: str, tag: str) -> dict[str, dict]:
    result = subprocess.run(
        ["gh", "release", "view", tag, "--repo", repo, "--json", "assets"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)
    return {asset["name"]: asset for asset in payload.get("assets", [])}


def asset_name_for_entry(path: str) -> str:
    return Path(path).name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="Dsadd4/AgentFigureGallery")
    parser.add_argument("--tag", default="full-public-v0.1.0")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source = read_json(args.source)
    assets = release_assets(args.repo, args.tag)
    manifest = {
        "version": source.get("version", "0.1.0"),
        "packs": [],
    }

    for pack in source.get("packs", []):
        if pack.get("name") != "full-public":
            manifest["packs"].append(pack)
            continue
        next_pack = dict(pack)
        next_pack["description"] = (
            "Full public AgentFigureGallery KB mirrored on GitHub Release assets "
            "for environments where Hugging Face is not reachable."
        )
        entries = []
        for entry in pack.get("entries", []):
            name = asset_name_for_entry(entry["path"])
            asset = assets.get(name)
            if not asset:
                raise SystemExit(f"release asset missing: {name}")
            next_entry = dict(entry)
            next_entry["url"] = asset.get("apiUrl") or asset["url"]
            next_entry["headers"] = {"Accept": "application/octet-stream"}
            next_entry["description"] = f"{entry.get('description', name)} (GitHub Release mirror)"
            entries.append(next_entry)
        next_pack["entries"] = entries
        manifest["packs"].append(next_pack)

    write_json(args.output, manifest)
    print(f"wrote: {args.output}")
    print(f"assets mapped: {len(assets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
