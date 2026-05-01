#!/usr/bin/env python3
"""Download AgentFigureGallery asset packs from a manifest.

The script is intentionally dependency-free so a fresh clone can use it before
the Python package is installed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import tempfile
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "resource_manifest.json"
EXAMPLE_MANIFEST = ROOT / "manifests" / "resource_manifest.example.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    if not path.exists() and path == DEFAULT_MANIFEST:
        path = EXAMPLE_MANIFEST
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_manifest_from_url(url: str) -> dict:
    with urlopen(Request(url)) as response:
        return json.loads(response.read().decode("utf-8"))


def select_pack(manifest: dict, pack_name: str) -> dict:
    for pack in manifest.get("packs", []):
        if pack.get("name") == pack_name:
            return pack
    names = ", ".join(pack.get("name", "<unnamed>") for pack in manifest.get("packs", []))
    raise SystemExit(f"Unknown pack {pack_name!r}. Available packs: {names}")


def is_placeholder_url(url: str) -> bool:
    return not url or url.startswith("TODO_") or "TODO_PUBLIC_URL" in url


def download_one(
    url: str,
    target: Path,
    expected_sha256: str = "",
    force: bool = False,
    headers: dict[str, str] | None = None,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not force:
        if expected_sha256 and sha256_file(target) != expected_sha256:
            print(f"checksum mismatch, redownloading: {target}")
        else:
            print(f"exists: {target}")
            return

    part = target.with_suffix(target.suffix + ".part")
    resume_at = part.stat().st_size if part.exists() and not force else 0
    request_headers = dict(headers or {})
    request_headers.setdefault("User-Agent", "AgentFigureGallery/0.1")
    mode = "ab"
    if resume_at:
        request_headers["Range"] = f"bytes={resume_at}-"
    else:
        mode = "wb"

    request = Request(url, headers=request_headers)
    try:
        with urlopen(request) as response:
            if resume_at and response.getcode() == 200:
                print(f"server ignored resume range, restarting: {target}")
                mode = "wb"
            with part.open(mode) as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
    except HTTPError as exc:
        if resume_at and exc.code == 416:
            pass
        else:
            raise
    except URLError as exc:
        raise SystemExit(f"download failed for {url}: {exc}") from exc

    os.replace(part, target)

    if expected_sha256:
        actual = sha256_file(target)
        if actual != expected_sha256:
            raise SystemExit(f"sha256 mismatch for {target}: expected {expected_sha256}, got {actual}")
    print(f"downloaded: {target}")


def safe_extract_tar(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with tarfile.open(archive, "r:*") as handle:
        for member in handle.getmembers():
            target = (destination / member.name).resolve()
            try:
                target.relative_to(destination)
            except ValueError as exc:
                raise SystemExit(f"refusing unsafe tar member path: {member.name}") from exc
        handle.extractall(destination)


def safe_extract_zip(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as handle:
        for member in handle.namelist():
            target = (destination / member).resolve()
            try:
                target.relative_to(destination)
            except ValueError as exc:
                raise SystemExit(f"refusing unsafe zip member path: {member}") from exc
        handle.extractall(destination)


def unpack_archive(path: Path, destination: Path) -> None:
    if path.suffix == ".zip":
        safe_extract_zip(path, destination)
    elif path.suffix in {".gz", ".tgz", ".bz2", ".xz"} or ".tar." in path.name:
        safe_extract_tar(path, destination)
    else:
        raise SystemExit(f"don't know how to unpack archive: {path}")
    print(f"unpacked: {path} -> {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download AgentFigureGallery asset packs.")
    parser.add_argument("--pack", default="minimal", help="Pack name from the manifest.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Resource manifest JSON.")
    parser.add_argument("--manifest-url", help="Remote resource manifest URL.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Output root for manifest paths.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without downloading.")
    parser.add_argument("--force", action="store_true", help="Redownload existing files.")
    parser.add_argument("--unpack", action="store_true", help="Unpack entries marked with unpack=true.")
    args = parser.parse_args()

    manifest = load_manifest_from_url(args.manifest_url) if args.manifest_url else load_manifest(args.manifest)
    pack = select_pack(manifest, args.pack)

    print(f"manifest version: {manifest.get('version', 'unknown')}")
    print(f"pack: {pack.get('name')} - {pack.get('description', '')}")

    for entry in pack.get("entries", []):
        url = entry.get("url", "")
        target = args.root / entry["path"]
        expected_sha256 = entry.get("sha256", "")
        size = entry.get("size_bytes", 0)
        print(f"{entry.get('description', '').strip()}")
        print(f"  target: {target}")
        print(f"  size: {size}")

        if is_placeholder_url(url):
            print(f"  skipped placeholder url: {url}")
            continue
        if args.dry_run:
            print(f"  would download: {url}")
            if args.unpack or entry.get("unpack"):
                print("  would unpack after download")
            continue
        download_one(
            url,
            target,
            expected_sha256=expected_sha256,
            force=args.force,
            headers=entry.get("headers"),
        )
        if args.unpack or entry.get("unpack"):
            unpack_archive(target, args.root)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
