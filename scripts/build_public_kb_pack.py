#!/usr/bin/env python3
"""Build a private-filtered public KB asset pack from a Drawing development KB."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PRIVATE_PATTERNS = [
    "massspec",
    "msagent",
    "personalhpc",
    "personalhpcgpu",
    "aimslight",
    "yifanl/",
]

DROP_ABSOLUTE_KEYS = {
    "preview_path",
    "source_output_path",
    "script_path",
    "route_path",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_text(candidate: dict) -> str:
    return json.dumps(candidate, ensure_ascii=True).lower()


def is_private_candidate(candidate: dict, patterns: list[str]) -> bool:
    text = candidate_text(candidate)
    return any(pattern.lower() in text for pattern in patterns)


def source_path(source_root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return source_root / path


def stable_id(candidate: dict) -> str:
    return (
        candidate.get("stable_candidate_id")
        or candidate.get("display_id")
        or candidate.get("candidate_id")
        or candidate.get("reference_candidate_id")
        or "UNKNOWN"
    )


def clean_candidate(candidate: dict, preview_rel: Path) -> dict:
    item = {key: value for key, value in candidate.items() if key not in DROP_ABSOLUTE_KEYS}
    cid = stable_id(candidate)
    plot_type = candidate.get("plot_type") or candidate.get("primary_plot_type") or "unknown"
    item["candidate_id"] = cid
    item["stable_candidate_id"] = cid
    item["display_id"] = cid
    item["plot_type"] = plot_type
    item["primary_plot_type"] = candidate.get("primary_plot_type") or plot_type
    item["preview_path"] = preview_rel.as_posix()
    item["preview_path_rel"] = preview_rel.as_posix()
    item["source_repo"] = candidate.get("source_repo") or candidate.get("repo")
    item["repo"] = candidate.get("repo") or candidate.get("source_repo")
    item["curation"] = {
        "source": "private_filtered_public_pack",
        "curated_at": utc_now(),
    }
    return item


def copy_tree_if_exists(source: Path, destination: Path) -> None:
    if source.exists():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)


def make_tar_gz(source_dir: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:gz") as handle:
        handle.add(source_dir, arcname=".")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path.cwd().parent)
    parser.add_argument("--release-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pack", default="full-public", choices=["public-preview", "full-public"])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--max-candidates", type=int, default=0, help="Optional cap for testing. 0 means no cap.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--base-url", default="TODO_PUBLIC_URL", help="URL prefix used in the generated manifest fragment.")
    parser.add_argument("--exclude-private-pattern", action="append", default=[])
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    release_root = args.release_root.resolve()
    output_dir = (args.output_dir or (release_root / "assets" / "releases" / args.pack)).resolve()
    stage_dir = output_dir / "stage"
    archive_path = output_dir / f"{args.pack}.tar.gz"
    private_patterns = DEFAULT_PRIVATE_PATTERNS + args.exclude_private_pattern

    index = load_json(source_root / "data" / "reference_candidate_index.json")
    accepted: list[dict] = []
    skipped_private = 0
    skipped_missing_preview = 0

    if stage_dir.exists() and args.overwrite and not args.dry_run:
        shutil.rmtree(stage_dir)
    if not args.dry_run:
        stage_dir.mkdir(parents=True, exist_ok=True)

    for candidate in index.get("candidates", []):
        if args.max_candidates and len(accepted) >= args.max_candidates:
            break
        if is_private_candidate(candidate, private_patterns):
            skipped_private += 1
            continue
        preview_source = source_path(source_root, candidate.get("preview_path") or candidate.get("preview_path_rel"))
        if not preview_source or not preview_source.exists():
            skipped_missing_preview += 1
            continue
        plot_type = candidate.get("plot_type") or candidate.get("primary_plot_type") or "unknown"
        cid = stable_id(candidate)
        suffix = preview_source.suffix.lower() or ".png"
        preview_rel = Path("assets") / "packs" / args.pack / "previews" / plot_type / f"{cid}{suffix}"
        if not args.dry_run:
            target = stage_dir / preview_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(preview_source, target)
        accepted.append(clean_candidate(candidate, preview_rel))

    counts = Counter(item["plot_type"] for item in accepted)
    payload = {
        "schema_version": "agentfiguregallery.reference_candidate_index.v1",
        "generated_at": utc_now(),
        "source": {
            "type": args.pack,
            "source_root": str(source_root),
            "skipped_private": skipped_private,
            "skipped_missing_preview": skipped_missing_preview,
            "max_candidates": args.max_candidates,
        },
        "preview_root": f"assets/packs/{args.pack}/previews",
        "summary": {
            "candidate_count": len(accepted),
            "selectable_by_plot_type": dict(sorted(counts.items())),
        },
        "candidates": accepted,
    }
    facets = {
        "schema_version": "agentfiguregallery.reference_candidate_facets.v1",
        "generated_at": utc_now(),
        "candidate_count": len(accepted),
        "selectable_by_plot_type": dict(sorted(counts.items())),
        "pack": args.pack,
        "curation_source": "private_filtered_public_pack",
    }

    print(f"accepted candidates: {len(accepted)}")
    print(f"skipped private: {skipped_private}")
    print(f"skipped missing preview: {skipped_missing_preview}")
    print(f"plot_type counts: {dict(sorted(counts.items()))}")

    if args.dry_run:
        return 0

    write_json(stage_dir / "data" / "reference_candidate_index.json", payload)
    write_json(stage_dir / "data" / "reference_candidate_facets.json", facets)
    copy_tree_if_exists(release_root / "ExtendAgent", stage_dir / "ExtendAgent")
    copy_tree_if_exists(release_root / "docs", stage_dir / "docs")
    if args.pack == "full-public":
        copy_tree_if_exists(source_root / "templates", stage_dir / "templates")
        for name in ["PLOT_TYPE_PLAYBOOK.md", "PLOT_TYPE_DESIGN_CARDS.md", "AGENT_QUERY_PROTOCOL.md", "REFERENCE_SESSION_PROTOCOL.md"]:
            source = source_root / name
            if source.exists():
                target = stage_dir / name
                shutil.copy2(source, target)

    make_tar_gz(stage_dir, archive_path)
    digest = sha256_file(archive_path)
    manifest_fragment = {
        "name": args.pack,
        "description": f"Private-filtered {args.pack} AgentFigureGallery KB pack.",
        "entries": [
            {
                "path": f"assets/packs/{args.pack}/{archive_path.name}",
                "url": f"{args.base_url.rstrip('/')}/{args.pack}/{archive_path.name}",
                "sha256": digest,
                "size_bytes": archive_path.stat().st_size,
                "description": f"{args.pack} archive",
                "unpack": True,
            }
        ],
    }
    write_json(output_dir / "resource_manifest.fragment.json", manifest_fragment)
    print(f"archive: {archive_path}")
    print(f"sha256: {digest}")
    print(f"manifest fragment: {output_dir / 'resource_manifest.fragment.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

