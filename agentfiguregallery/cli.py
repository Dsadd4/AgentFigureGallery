from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from . import __version__
from .server import export_bundle, generate_session, resolve_session, run_server, update_preference


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentfiguregallery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local KB readiness and print next commands.")
    doctor.add_argument("--json", action="store_true")

    query = subparsers.add_parser("query", help="Resolve a task or plot type to available candidate counts.")
    query.add_argument("--task", default="")
    query.add_argument("--plot-type", default="")
    query.add_argument("--json", action="store_true")

    gallery = subparsers.add_parser("gallery", help="Generate a reference session, optionally serving the UI.")
    gallery.add_argument("--plot-type", required=True)
    gallery.add_argument("--task", default="")
    gallery.add_argument("--limit", type=int, default=50)
    gallery.add_argument("--session-id", default="")
    gallery.add_argument("--strategy", choices=["top", "explore", "random"], default="explore")
    gallery.add_argument("--seed", type=int)
    gallery.add_argument("--serve", action="store_true")
    gallery.add_argument("--host", default="127.0.0.1")
    gallery.add_argument("--port", type=int, default=8765)

    serve = subparsers.add_parser("serve", help="Serve the local gallery UI.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    prefer = subparsers.add_parser("prefer", help="Record human preferences for a reference session.")
    prefer.add_argument("--session", required=True)
    prefer.add_argument("--like", nargs="+", action="append", default=[])
    prefer.add_argument("--reject", nargs="+", action="append", default=[])
    prefer.add_argument("--select", nargs="+", action="append", default=[])
    prefer.add_argument("--clear", nargs="+", action="append", default=[])
    prefer.add_argument("--global-like", nargs="+", action="append", default=[])
    prefer.add_argument("--global-reject", nargs="+", action="append", default=[])
    prefer.add_argument("--global-clear", nargs="+", action="append", default=[])

    bundle = subparsers.add_parser("bundle", help="Export selected references for upstream agent action.")
    bundle.add_argument("--session", required=True)
    bundle.add_argument("--copy-scripts", action="store_true")
    bundle.add_argument("--json", action="store_true")

    setup = subparsers.add_parser("setup", help="Download and configure a full KB asset pack.")
    setup.add_argument("--pack", default="public-preview")
    setup.add_argument("--manifest", default="")
    setup.add_argument("--manifest-url", default="")
    setup.add_argument("--dry-run", action="store_true")
    setup.add_argument("--force", action="store_true")

    assets = subparsers.add_parser("assets", help="Asset utilities.")
    assets_sub = assets.add_subparsers(dest="assets_command", required=True)
    download = assets_sub.add_parser("download", help="Download an asset pack.")
    download.add_argument("--pack", default="minimal")

    return parser


def root() -> Path:
    for key in ["AGENT_FIGURE_GALLERY_ROOT", "DRAWING_KB_ROOT"]:
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def flatten_ids(groups: list[list[str]]) -> list[str]:
    return [candidate_id for group in groups for candidate_id in group]


def load_index() -> dict:
    path = root() / "data" / "reference_candidate_index.json"
    if not path.exists():
        return {"candidates": [], "summary": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def plot_type_counts(candidates: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in candidates:
        key = item.get("plot_type") or item.get("primary_plot_type") or "unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def command_doctor(args: argparse.Namespace) -> int:
    kb_root = root()
    index_path = kb_root / "data" / "reference_candidate_index.json"
    skill_path = kb_root / "skills" / "agent-figure-gallery" / "SKILL.md"
    frontend_path = kb_root / "frontend" / "reference_gallery" / "index.html"
    manifest_path = kb_root / "manifests" / "resource_manifest.json"
    hub_manifest_url = "https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json"

    index = load_index()
    candidates = index.get("candidates", [])
    counts = plot_type_counts(candidates)
    checks = {
        "candidate_index": index_path.exists(),
        "skill": skill_path.exists(),
        "frontend": frontend_path.exists(),
        "full_public_manifest": manifest_path.exists(),
    }
    payload = {
        "version": __version__,
        "root": str(kb_root),
        "ok": all(checks.values()) and bool(candidates),
        "checks": checks,
        "candidate_total": len(candidates),
        "plot_type_counts": counts,
        "agent_skill": str(skill_path),
        "recommended_commands": [
            "agentfiguregallery query --task \"Nature-style embedding map for cell atlas\"",
            "agentfiguregallery gallery --plot-type embedding_plot --limit 50 --serve",
            f"agentfiguregallery setup --pack full-public --manifest-url {hub_manifest_url}",
        ],
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        print(f"AgentFigureGallery {payload['version']}")
        print(f"root: {payload['root']}")
        for name, passed in checks.items():
            print(f"{'OK' if passed else 'MISSING'} {name}")
        print(f"candidate_total: {payload['candidate_total']}")
        if counts:
            print("plot_types:")
            for plot_type, count in counts.items():
                print(f"  {plot_type}: {count}")
        print(f"agent_skill: {payload['agent_skill']}")
        print("next:")
        for command in payload["recommended_commands"]:
            print(f"  {command}")
    return 0 if payload["ok"] else 1


def infer_plot_type(task: str, explicit: str) -> str:
    if explicit:
        return explicit
    text = task.lower()
    hints = [
        ("heatmap_matrix", ["heatmap", "matrix"]),
        ("box_violin_distribution", ["box", "violin", "distribution"]),
        ("bar_chart", ["bar", "column"]),
        ("line_chart", ["line", "trend", "trajectory"]),
        ("embedding_plot", ["umap", "tsne", "embedding"]),
        ("scatter_plot", ["scatter", "correlation"]),
        ("spatial_map", ["spatial", "tissue"]),
        ("microscopy_panel", ["microscopy", "image", "segmentation"]),
        ("benchmark_performance", ["benchmark", "performance", "accuracy"]),
        ("multi_panel_figure", ["multi-panel", "multipanel", "panel"]),
    ]
    for plot_type, words in hints:
        if any(word in text for word in words):
            return plot_type
    return "multi_panel_figure"


def command_query(args: argparse.Namespace) -> int:
    index = load_index()
    plot_type = infer_plot_type(args.task, args.plot_type)
    candidates = index.get("candidates", [])
    counts = plot_type_counts(candidates)
    payload = {
        "resolved": {"plot_type": plot_type},
        "available_candidates": counts.get(plot_type, 0),
        "selectable_by_plot_type": counts,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        print(f"resolved plot_type: {plot_type}")
        print(f"available candidates: {payload['available_candidates']}")
    return 0


def command_gallery(args: argparse.Namespace) -> int:
    session = generate_session(
        root=root(),
        plot_type=args.plot_type,
        task=args.task or f"Reference session for {args.plot_type}",
        limit=args.limit,
        session_id=args.session_id or "",
        strategy=args.strategy,
        seed=args.seed,
    )
    print(f"session: {session['session_id']}")
    print(f"candidates: {len(session.get('candidates', []))}")
    print(f"session_json: {session['paths']['session_json']}")
    if args.serve:
        run_server(root=root(), host=args.host, port=args.port)
    return 0


def command_assets(args: argparse.Namespace) -> int:
    if args.assets_command != "download":
        raise SystemExit(f"Unsupported assets command: {args.assets_command}")
    import subprocess
    import sys

    script = root() / "scripts" / "download_assets.py"
    return subprocess.call([sys.executable, str(script), "--pack", args.pack], cwd=root())


def command_prefer(args: argparse.Namespace) -> int:
    kb_root = root()
    session_json = resolve_session(kb_root, args.session)
    actions = [
        ("like", flatten_ids(args.like)),
        ("reject", flatten_ids(args.reject)),
        ("select", flatten_ids(args.select)),
        ("clear", flatten_ids(args.clear)),
        ("global_like", flatten_ids(args.global_like)),
        ("global_reject", flatten_ids(args.global_reject)),
        ("global_clear", flatten_ids(args.global_clear)),
    ]
    updated = None
    for action, ids in actions:
        if not ids:
            continue
        updated = update_preference(
            kb_root,
            session_json,
            {
                "session": str(session_json),
                "candidate_ids": ids,
                "action": action,
            },
        )
    if updated is None:
        raise SystemExit("No preference action supplied.")
    print(f"session: {updated.get('session_id')}")
    print(f"preferences: {session_json.parent / 'preferences.json'}")
    print(json.dumps(updated.get("status_counts", {}), indent=2, ensure_ascii=True))
    return 0


def command_bundle(args: argparse.Namespace) -> int:
    kb_root = root()
    session_json = resolve_session(kb_root, args.session)
    bundle = export_bundle(kb_root, session_json, copy_scripts=args.copy_scripts)
    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=True))
    else:
        print(f"session: {bundle.get('session_id')}")
        print(f"bundle_json: {bundle.get('paths', {}).get('bundle_json')}")
        print(f"selected_references: {len(bundle.get('selected_references', []))}")
    return 0


def command_setup(args: argparse.Namespace) -> int:
    import subprocess
    import sys

    script = root() / "scripts" / "setup_full_kb.py"
    cmd = [sys.executable, str(script), "--pack", args.pack, "--root", str(root())]
    if args.manifest_url:
        cmd.extend(["--manifest-url", args.manifest_url])
    if args.manifest:
        cmd.extend(["--manifest", args.manifest])
    if args.dry_run:
        cmd.append("--dry-run")
    if args.force:
        cmd.append("--force")
    return subprocess.call(cmd, cwd=root())


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "doctor":
        return command_doctor(args)
    if args.command == "query":
        return command_query(args)
    if args.command == "gallery":
        return command_gallery(args)
    if args.command == "serve":
        return run_server(root=root(), host=args.host, port=args.port)
    if args.command == "prefer":
        return command_prefer(args)
    if args.command == "bundle":
        return command_bundle(args)
    if args.command == "setup":
        return command_setup(args)
    if args.command == "assets":
        return command_assets(args)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
