#!/usr/bin/env python3
"""Upload generated full-public resource archives to a Hugging Face dataset repo."""

from __future__ import annotations

import argparse
import os
from io import BytesIO
from pathlib import Path

from huggingface_hub import HfApi


def format_mb(path: Path) -> str:
    return f"{path.stat().st_size / (1024 * 1024):.1f}MB"


def upload_file(api: HfApi, repo_id: str, local: Path, remote: str, repo_type: str, skip_existing: bool) -> None:
    if skip_existing and api.file_exists(repo_id=repo_id, filename=remote, repo_type=repo_type):
        print(f"SKIP_EXISTS {remote}")
        return
    print(f"UPLOAD_START {remote} {format_mb(local)}", flush=True)
    api.upload_file(
        path_or_fileobj=str(local),
        path_in_repo=remote,
        repo_id=repo_id,
        repo_type=repo_type,
        commit_message=f"Upload {remote}",
    )
    print(f"UPLOAD_DONE {remote}", flush=True)


def load_dataset_card(root: Path) -> str:
    source = root / "docs" / "HF_DATASET_CARD.md"
    text = source.read_text(encoding="utf-8")
    start_marker = "````markdown\n"
    end_marker = "\n````"
    start = text.find(start_marker)
    end = text.rfind(end_marker)
    if start == -1 or end == -1 or end <= start:
        raise SystemExit(f"Could not extract markdown card from {source}")
    return text[start + len(start_marker) : end].strip() + "\n"


def upload_text(api: HfApi, repo_id: str, content: str, remote: str, repo_type: str) -> None:
    print(f"UPLOAD_START {remote} {len(content.encode('utf-8'))}B", flush=True)
    api.upload_file(
        path_or_fileobj=BytesIO(content.encode("utf-8")),
        path_in_repo=remote,
        repo_id=repo_id,
        repo_type=repo_type,
        commit_message=f"Update {remote}",
    )
    print(f"UPLOAD_DONE {remote}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", default="dsadd4/AgentFigureGallery")
    parser.add_argument("--repo-type", default="dataset")
    parser.add_argument("--release-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--skip-card", action="store_true")
    parser.add_argument("--card-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token and not args.dry_run:
        raise SystemExit("HF_TOKEN is required in the environment.")

    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    root = args.release_root.resolve()
    card = load_dataset_card(root) if not args.skip_card else ""
    archive_root = root / "assets" / "releases" / "full-public"
    files: list[tuple[Path, str]] = []
    if not args.card_only:
        files = [(archive_root / "core.tar.gz", "full-public/core.tar.gz")]
        files.extend(
            (path, f"full-public/previews/{path.name}")
            for path in sorted((archive_root / "previews").glob("*.tar.gz"))
        )
        files.append((root / "manifests" / "resource_manifest.json", "resource_manifest.json"))

    missing = [str(path) for path, _ in files if not path.exists()]
    if missing:
        raise SystemExit("Missing upload files:\n" + "\n".join(missing))

    if args.dry_run:
        for local, remote in files:
            print(f"DRY_RUN upload {local} -> {args.repo_id}/{remote}")
        if card:
            print(f"DRY_RUN upload dataset card -> {args.repo_id}/README.md ({len(card.encode('utf-8'))}B)")
        return 0

    api = HfApi(token=token)
    api.create_repo(repo_id=args.repo_id, repo_type=args.repo_type, private=False, exist_ok=True)

    for local, remote in files:
        upload_file(api, args.repo_id, local, remote, args.repo_type, args.skip_existing)
    if card:
        upload_text(api, args.repo_id, card, "README.md", args.repo_type)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
