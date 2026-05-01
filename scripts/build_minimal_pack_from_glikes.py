#!/usr/bin/env python3
"""Build the minimal public pack from global-liked candidates in a Drawing KB."""

from __future__ import annotations

import argparse
import json
import shutil
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

KEEP_KEYS = {
    "reference_candidate_id",
    "stable_candidate_id",
    "display_id",
    "plot_type",
    "primary_plot_type",
    "source_output_type",
    "source_output_path_rel",
    "script_path_rel",
    "route_path_rel",
    "repo",
    "source_repo",
    "role",
    "source_role",
    "workflow",
    "script_kind",
    "chart_family",
    "plot_libraries",
    "asset_match_type",
    "is_selectable",
    "visual_only",
    "quality_score",
    "summary",
    "why_suggested",
    "failure_flags",
    "image_stats",
    "tags",
    "what_to_borrow",
    "design_takeaways",
    "global_preference_key",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def global_key(candidate: dict) -> str:
    if candidate.get("global_preference_key"):
        return str(candidate["global_preference_key"])
    for prefix, key in [
        ("output", "source_output_path_rel"),
        ("output", "source_output_path"),
        ("reference", "reference_candidate_id"),
        ("preview", "preview_path_rel"),
        ("preview", "preview_path"),
        ("script", "script_path_rel"),
        ("script", "script_path"),
    ]:
        value = candidate.get(key)
        if value:
            return f"{prefix}:{value}"
    return f"candidate:{candidate.get('candidate_id') or candidate.get('stable_candidate_id') or 'unknown'}"


def candidate_lookup(candidates: list[dict]) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    for candidate in candidates:
        for key in [
            global_key(candidate),
            f"reference:{candidate.get('reference_candidate_id')}" if candidate.get("reference_candidate_id") else "",
            f"output:{candidate.get('source_output_path_rel')}" if candidate.get("source_output_path_rel") else "",
            f"preview:{candidate.get('preview_path_rel')}" if candidate.get("preview_path_rel") else "",
            f"script:{candidate.get('script_path_rel')}" if candidate.get("script_path_rel") else "",
        ]:
            if key:
                lookup.setdefault(key, candidate)
    return lookup


def source_path(source_root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return source_root / path


def public_candidate(source_root: Path, release_root: Path, pack_root: Path, candidate: dict, liked_key: str) -> dict | None:
    preview_source = source_path(source_root, candidate.get("preview_path") or candidate.get("preview_path_rel"))
    if not preview_source or not preview_source.exists():
        return None

    plot_type = candidate.get("plot_type") or candidate.get("primary_plot_type") or "unknown"
    stable_id = (
        candidate.get("stable_candidate_id")
        or candidate.get("display_id")
        or candidate.get("candidate_id")
        or candidate.get("reference_candidate_id")
    )
    if not stable_id:
        return None

    suffix = preview_source.suffix.lower() or ".png"
    preview_rel = Path("assets") / "packs" / "minimal" / "previews" / plot_type / f"{stable_id}{suffix}"
    preview_target = release_root / preview_rel
    preview_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(preview_source, preview_target)

    item = {
        key: value
        for key, value in candidate.items()
        if key in KEEP_KEYS and value is not None and value != ""
    }
    item["candidate_id"] = stable_id
    item["stable_candidate_id"] = stable_id
    item["display_id"] = stable_id
    item["plot_type"] = plot_type
    item["primary_plot_type"] = candidate.get("primary_plot_type") or plot_type
    item["preview_path"] = preview_rel.as_posix()
    item["preview_path_rel"] = preview_rel.as_posix()
    item["source_repo"] = candidate.get("source_repo") or candidate.get("repo")
    item["repo"] = candidate.get("repo") or candidate.get("source_repo")
    item["global_preference_key"] = liked_key
    item["curation"] = {
        "source": "global_like",
        "source_key": liked_key,
        "curated_at": utc_now(),
    }
    return item


def candidate_text(candidate: dict) -> str:
    return json.dumps(candidate, ensure_ascii=True).lower()


def is_private_candidate(candidate: dict, patterns: list[str]) -> bool:
    text = candidate_text(candidate)
    return any(pattern.lower() in text for pattern in patterns)


def iter_session_liked_candidates(source_root: Path, liked: set[str]) -> list[tuple[str, dict]]:
    matches: list[tuple[str, dict]] = []
    session_paths = sorted(
        source_root.glob("outputs/reference_sessions*/**/reference_session.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for session_json in session_paths:
        try:
            session = load_json(session_json)
        except Exception:
            continue
        session_plot_type = session.get("resolved", {}).get("plot_type")
        for candidate in session.get("candidates", []):
            key = global_key(candidate)
            if key not in liked:
                continue
            item = dict(candidate)
            item["plot_type"] = item.get("plot_type") or session_plot_type or item.get("primary_plot_type")
            item["primary_plot_type"] = item.get("primary_plot_type") or item.get("plot_type")
            matches.append((key, item))
    return matches


def iter_preference_item_liked_candidates(prefs: dict, liked: set[str]) -> list[tuple[str, dict]]:
    matches: list[tuple[str, dict]] = []
    for key in prefs.get("liked", []):
        if key not in liked:
            continue
        item = prefs.get("items", {}).get(key)
        if item:
            matches.append((key, dict(item)))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Development Drawing KB root. Defaults to the parent of release root.")
    parser.add_argument("--release-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--source",
        choices=["session-history", "preference-items"],
        default="session-history",
        help="Use session history to preserve plot-type context, or only preference item metadata.",
    )
    parser.add_argument("--max-per-plot-type", type=int, default=30)
    parser.add_argument(
        "--exclude-private-pattern",
        action="append",
        default=[],
        help="Case-insensitive text pattern that excludes a candidate. Defaults include massspec/MSagent/personalhpc/yifanl.",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    release_root = args.release_root.resolve()
    source_root = (args.source_root or release_root.parent).resolve()
    prefs = load_json(source_root / "data" / "reference_global_preferences.json")
    full_index = load_json(source_root / "data" / "reference_candidate_index.json")
    lookup = candidate_lookup(full_index.get("candidates", []))

    pack_root = release_root / "assets" / "packs" / "minimal"
    data_path = release_root / "data" / "reference_candidate_index.json"
    if pack_root.exists() and args.overwrite:
        shutil.rmtree(pack_root)
    pack_root.mkdir(parents=True, exist_ok=True)

    rejected = set(prefs.get("rejected", []))
    liked = [key for key in prefs.get("liked", []) if key not in rejected]
    liked_set = set(liked)
    private_patterns = DEFAULT_PRIVATE_PATTERNS + args.exclude_private_pattern
    if args.source == "session-history":
        candidates_to_consider = iter_session_liked_candidates(source_root, liked_set)
        # Add preference items as fallback for liked entries that were never seen
        # in a saved reference session.
        seen_keys = {key for key, _ in candidates_to_consider}
        candidates_to_consider.extend(
            (key, item)
            for key, item in iter_preference_item_liked_candidates(prefs, liked_set)
            if key not in seen_keys
        )
    else:
        candidates_to_consider = iter_preference_item_liked_candidates(prefs, liked_set)

    selected: list[dict] = []
    missing: list[str] = []
    seen_ids: set[tuple[str, str]] = set()
    per_type_counts: Counter[str] = Counter()
    for key, candidate in candidates_to_consider:
        if is_private_candidate(candidate, private_patterns):
            continue
        candidate = candidate or lookup.get(key)
        if not candidate:
            missing.append(key)
            continue
        plot_type = candidate.get("plot_type") or candidate.get("primary_plot_type") or "unknown"
        if args.max_per_plot_type > 0 and per_type_counts[plot_type] >= args.max_per_plot_type:
            continue
        item = public_candidate(source_root, release_root, pack_root, candidate, key)
        if not item:
            missing.append(key)
            continue
        identity = (item.get("plot_type") or "unknown", item["candidate_id"])
        if identity in seen_ids:
            continue
        seen_ids.add(identity)
        per_type_counts[item.get("plot_type") or "unknown"] += 1
        selected.append(item)

    counts = Counter(item.get("plot_type") or "unknown" for item in selected)
    payload = {
        "schema_version": "agentfiguregallery.reference_candidate_index.v1",
        "generated_at": utc_now(),
        "source": {
            "type": "global_like_minimal_pack",
            "liked_count": len(liked),
            "missing_count": len(missing),
        },
        "preview_root": "assets/packs/minimal/previews",
        "summary": {
            "candidate_count": len(selected),
            "selectable_by_plot_type": dict(sorted(counts.items())),
        },
        "candidates": selected,
        "missing_liked_keys": missing,
    }
    facets = {
        "schema_version": "agentfiguregallery.reference_candidate_facets.v1",
        "generated_at": utc_now(),
        "candidate_count": len(selected),
        "selectable_by_plot_type": dict(sorted(counts.items())),
        "pack": "minimal",
        "curation_source": "global_like",
    }
    write_json(data_path, payload)
    write_json(release_root / "data" / "reference_candidate_facets.json", facets)
    write_json(pack_root / "reference_candidate_index.json", payload)
    write_json(pack_root / "reference_candidate_facets.json", facets)

    global_prefs = {
        "schema_version": "agentfiguregallery.reference_global_preferences.v1",
        "scope": {"level": "global"},
        "liked": [item["global_preference_key"] for item in selected],
        "rejected": [],
        "items": {item["global_preference_key"]: item for item in selected},
        "notes": {},
        "updated_at": utc_now(),
    }
    write_json(release_root / "data" / "reference_global_preferences.json", global_prefs)

    print(f"wrote {len(selected)} candidates to {data_path}")
    print(f"plot_type counts: {dict(sorted(counts.items()))}")
    if missing:
        print(f"missing liked keys: {len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
