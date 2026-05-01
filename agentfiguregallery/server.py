from __future__ import annotations

import json
import mimetypes
import random
import re
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


PLOT_TYPE_CODES = {
    "scatter_plot": "SCAT",
    "bar_chart": "BAR",
    "line_chart": "LINE",
    "heatmap_matrix": "HEAT",
    "box_violin_distribution": "BOX",
    "embedding_plot": "EMB",
    "benchmark_performance": "BENCH",
    "multi_panel_figure": "MULTI",
    "spatial_map": "SPAT",
    "microscopy_panel": "MICRO",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str, fallback: str = "reference_session") -> str:
    text = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return text[:80] or fallback


def read_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_path(root: Path, raw: str) -> Path:
    path = Path(unquote(raw)).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not is_under(path, root):
        raise ValueError(f"Path is outside AgentFigureGallery root: {path}")
    return path


def global_preference_key(candidate: dict) -> str:
    if candidate.get("global_preference_key"):
        return str(candidate["global_preference_key"])
    for prefix, key in [
        ("output", "source_output_path_rel"),
        ("reference", "reference_candidate_id"),
        ("preview", "preview_path_rel"),
        ("script", "script_path_rel"),
    ]:
        if candidate.get(key):
            return f"{prefix}:{candidate[key]}"
    return f"candidate:{candidate.get('candidate_id') or candidate.get('stable_candidate_id') or 'unknown'}"


def global_preferences_path(root: Path) -> Path:
    return root / "data" / "reference_global_preferences.json"


def initial_global_preferences() -> dict:
    return {
        "schema_version": "agentfiguregallery.reference_global_preferences.v1",
        "scope": {"level": "global"},
        "liked": [],
        "rejected": [],
        "items": {},
        "notes": {},
        "updated_at": utc_now(),
    }


def load_global_preferences(root: Path) -> dict:
    prefs = read_json(global_preferences_path(root), initial_global_preferences())
    prefs.setdefault("liked", [])
    prefs.setdefault("rejected", [])
    prefs.setdefault("items", {})
    prefs.setdefault("notes", {})
    return prefs


def write_global_preferences(root: Path, payload: dict) -> None:
    payload["updated_at"] = utc_now()
    write_json(global_preferences_path(root), payload)


def global_status(root: Path, candidate: dict) -> str:
    prefs = load_global_preferences(root)
    key = global_preference_key(candidate)
    if key in set(prefs.get("rejected", [])):
        return "global_rejected"
    if key in set(prefs.get("liked", [])):
        return "global_liked"
    return "none"


def index_path(root: Path) -> Path:
    return root / "data" / "reference_candidate_index.json"


def load_index(root: Path) -> dict:
    return read_json(index_path(root), {"candidates": [], "summary": {}})


def session_roots(root: Path) -> list[Path]:
    return [root / "outputs"]


def discover_sessions(root: Path) -> list[dict]:
    sessions: list[dict] = []
    for base in session_roots(root):
        for session_json in sorted(base.glob("reference_sessions*/**/reference_session.json")):
            try:
                payload = read_json(session_json)
            except Exception:
                continue
            resolved = payload.get("resolved", {})
            sessions.append(
                {
                    "session_id": payload.get("session_id") or session_json.parent.name,
                    "session_json": str(session_json),
                    "workdir": str(session_json.parent),
                    "plot_type": resolved.get("plot_type"),
                    "candidate_count": len(payload.get("candidates", [])),
                    "updated_at": payload.get("updated_at") or payload.get("created_at"),
                    "candidate_sheets": payload.get("paths", {}).get("candidate_sheets", []),
                }
            )
    sessions.sort(key=lambda item: (item.get("updated_at") or "", item["session_id"]), reverse=True)
    return sessions


def resolve_session(root: Path, value: str | None) -> Path:
    if not value:
        sessions = discover_sessions(root)
        if not sessions:
            raise FileNotFoundError("No reference sessions found.")
        return Path(sessions[0]["session_json"])
    raw = unquote(value)
    path = Path(raw)
    if path.suffix == ".json" or "/" in raw:
        if path.is_dir():
            path = path / "reference_session.json"
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        if not is_under(path, root):
            raise ValueError("Session path is outside AgentFigureGallery root.")
        return path
    for item in discover_sessions(root):
        if item["session_id"] == raw:
            return Path(item["session_json"])
    raise FileNotFoundError(f"Unknown session: {raw}")


def prefs_path(session_json: Path) -> Path:
    return session_json.parent / "preferences.json"


def load_preferences(session_json: Path, session: dict) -> dict:
    prefs = read_json(prefs_path(session_json), session.get("preferences") or {})
    prefs.setdefault("liked", [])
    prefs.setdefault("rejected", [])
    prefs.setdefault("selected", [])
    prefs.setdefault("notes", {})
    prefs.setdefault(
        "scope",
        {
            "level": "plot_type_session",
            "plot_type": session.get("resolved", {}).get("plot_type"),
            "session_id": session.get("session_id"),
        },
    )
    return prefs


def candidate_aliases(candidate: dict) -> set[str]:
    return {
        str(value)
        for value in [
            candidate.get("candidate_id"),
            candidate.get("stable_candidate_id"),
            candidate.get("display_id"),
            candidate.get("session_candidate_id"),
            candidate.get("reference_candidate_id"),
        ]
        if value
    }


def apply_status(root: Path, candidate: dict, prefs: dict) -> dict:
    item = dict(candidate)
    stable_id = item.get("stable_candidate_id") or item.get("candidate_id")
    item["candidate_id"] = item.get("candidate_id") or stable_id
    item["stable_candidate_id"] = stable_id
    item["display_id"] = item.get("display_id") or stable_id
    item["global_preference_key"] = global_preference_key(item)
    item["global_status"] = global_status(root, item)
    cid = item["candidate_id"]
    if cid in set(prefs.get("selected", [])):
        item["status"] = "selected"
    elif cid in set(prefs.get("rejected", [])):
        item["status"] = "rejected"
    elif cid in set(prefs.get("liked", [])):
        item["status"] = "liked"
    else:
        item["status"] = "candidate"
    if item.get("preview_path"):
        item["preview_url"] = f"/media?path={item['preview_path']}"
    return item


def session_payload(root: Path, session_json: Path) -> dict:
    session = read_json(session_json)
    prefs = load_preferences(session_json, session)
    candidates = [apply_status(root, item, prefs) for item in session.get("candidates", [])]
    result = dict(session)
    result["session_json"] = str(session_json)
    result["preferences"] = prefs
    result["candidates"] = candidates
    result["status_counts"] = {
        "candidate": sum(1 for item in candidates if item["status"] == "candidate"),
        "liked": sum(1 for item in candidates if item["status"] == "liked"),
        "rejected": sum(1 for item in candidates if item["status"] == "rejected"),
        "selected": sum(1 for item in candidates if item["status"] == "selected"),
    }
    result["global_status_counts"] = {
        "global_liked": sum(1 for item in candidates if item.get("global_status") == "global_liked"),
        "global_rejected": sum(1 for item in candidates if item.get("global_status") == "global_rejected"),
    }
    result["global_preferences_path"] = str(global_preferences_path(root))
    return result


def choose_candidates(root: Path, plot_type: str, limit: int, strategy: str, seed: int | None) -> list[dict]:
    index = load_index(root)
    prefs = load_global_preferences(root)
    rejected = set(prefs.get("rejected", []))
    candidates = [
        item
        for item in index.get("candidates", [])
        if (item.get("plot_type") or item.get("primary_plot_type")) == plot_type
        and global_preference_key(item) not in rejected
        and item.get("preview_path")
    ]
    candidates.sort(key=lambda item: (-(float(item.get("quality_score") or 0)), item.get("stable_candidate_id") or ""))
    if strategy in {"explore", "random"}:
        rng = random.Random(seed)
        if strategy == "random":
            rng.shuffle(candidates)
        else:
            head = candidates[: min(5, len(candidates))]
            tail = candidates[min(5, len(candidates)) :]
            rng.shuffle(tail)
            candidates = head + tail
    return candidates[: max(1, limit)]


def generate_session(
    *,
    root: Path,
    plot_type: str,
    task: str,
    limit: int,
    session_id: str = "",
    strategy: str = "explore",
    seed: int | None = None,
) -> dict:
    session_id = session_id or f"gallery_{plot_type}_{int(datetime.now().timestamp())}"
    session_id = slugify(session_id)
    workdir = root / "outputs" / "reference_sessions" / session_id
    candidates = choose_candidates(root, plot_type, limit, strategy, seed)
    code = PLOT_TYPE_CODES.get(plot_type, plot_type[:4].upper())
    normalized: list[dict] = []
    for index, candidate in enumerate(candidates, start=1):
        item = dict(candidate)
        stable_id = item.get("stable_candidate_id") or item.get("candidate_id") or item.get("reference_candidate_id")
        item["candidate_id"] = stable_id
        item["stable_candidate_id"] = stable_id
        item["display_id"] = stable_id
        item["session_candidate_id"] = f"{code[:1]}{index:02d}"
        item.setdefault("source_repo", item.get("repo") or item.get("source_repo"))
        item.setdefault("status", "candidate")
        normalized.append(item)
    preferences = {
        "scope": {"level": "plot_type_session", "plot_type": plot_type, "session_id": session_id},
        "liked": [],
        "rejected": [],
        "selected": [],
        "notes": {},
        "updated_at": utc_now(),
    }
    session = {
        "schema_version": "agentfiguregallery.reference_session.v1",
        "session_id": session_id,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "workdir": str(workdir),
        "query": {"task": task, "plot_type": plot_type},
        "generation": {"strategy": strategy, "seed": seed, "limit": limit},
        "resolved": {"plot_type": plot_type},
        "selection": {
            "title": plot_type.replace("_", " ").title(),
            "goal": task,
            "recommended_palettes": [],
            "self_check": [],
        },
        "paths": {
            "session_json": str(workdir / "reference_session.json"),
            "preferences_json": str(workdir / "preferences.json"),
            "candidate_sheets": [],
        },
        "candidate_summary": {
            "count": len(normalized),
            "source_repos": sorted({item.get("source_repo") or item.get("repo") or "local" for item in normalized}),
        },
        "candidates": normalized,
        "preferences": preferences,
    }
    write_json(workdir / "preferences.json", preferences)
    write_json(workdir / "reference_session.json", session)
    return session


def set_list_value(items: list[str], additions: list[str], removals: set[str]) -> list[str]:
    result = [item for item in items if item not in removals]
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def update_preference(root: Path, session_json: Path, body: dict) -> dict:
    session = read_json(session_json)
    prefs = load_preferences(session_json, session)
    candidates = session.get("candidates", [])
    alias_to_id: dict[str, str] = {}
    by_id: dict[str, dict] = {}
    for candidate in candidates:
        canonical = candidate["candidate_id"]
        by_id[canonical] = candidate
        for alias in candidate_aliases(candidate):
            alias_to_id[alias] = canonical
    raw_ids = body.get("candidate_ids") or [body.get("candidate_id")]
    requested = [str(item) for item in raw_ids if item]
    ids = [alias_to_id.get(item, item) for item in requested]
    unknown = [item for item in ids if item not in by_id]
    if unknown:
        raise ValueError(f"Unknown candidate ids: {', '.join(requested)}")
    action = body.get("action")
    if action == "like":
        prefs["liked"] = set_list_value(prefs.get("liked", []), ids, set())
        prefs["rejected"] = set_list_value(prefs.get("rejected", []), [], set(ids))
    elif action == "reject":
        prefs["rejected"] = set_list_value(prefs.get("rejected", []), ids, set())
        prefs["liked"] = set_list_value(prefs.get("liked", []), [], set(ids))
        prefs["selected"] = set_list_value(prefs.get("selected", []), [], set(ids))
    elif action == "select":
        prefs["selected"] = set_list_value(prefs.get("selected", []), ids, set())
        prefs["liked"] = set_list_value(prefs.get("liked", []), ids, set())
        prefs["rejected"] = set_list_value(prefs.get("rejected", []), [], set(ids))
    elif action == "clear":
        for key in ["liked", "rejected", "selected"]:
            prefs[key] = set_list_value(prefs.get(key, []), [], set(ids))
    elif action == "clear_rejected":
        prefs["rejected"] = []
    elif action in {"global_like", "global_reject", "global_clear"}:
        global_prefs = load_global_preferences(root)
        for cid in ids:
            candidate = dict(by_id[cid])
            key = global_preference_key(candidate)
            global_prefs["liked"] = [item for item in global_prefs.get("liked", []) if item != key]
            global_prefs["rejected"] = [item for item in global_prefs.get("rejected", []) if item != key]
            if action == "global_like":
                global_prefs["liked"].append(key)
            elif action == "global_reject":
                global_prefs["rejected"].append(key)
                prefs["rejected"] = set_list_value(prefs.get("rejected", []), [cid], set())
                prefs["liked"] = set_list_value(prefs.get("liked", []), [], {cid})
                prefs["selected"] = set_list_value(prefs.get("selected", []), [], {cid})
            elif action == "global_clear":
                prefs["rejected"] = set_list_value(prefs.get("rejected", []), [], {cid})
            candidate["global_preference_key"] = key
            candidate["last_seen_candidate_id"] = cid
            candidate["last_seen_session_id"] = session.get("session_id")
            candidate["last_seen_plot_type"] = session.get("resolved", {}).get("plot_type")
            candidate["global_action"] = action
            global_prefs.setdefault("items", {})[key] = candidate
        write_global_preferences(root, global_prefs)
    else:
        raise ValueError(f"Unsupported action: {action}")
    prefs["updated_at"] = body.get("updated_at") or utc_now()
    write_json(prefs_path(session_json), prefs)
    session["preferences"] = prefs
    session["updated_at"] = utc_now()
    write_json(session_json, session)
    return session_payload(root, session_json)


def export_bundle(root: Path, session_json: Path, copy_scripts: bool = False) -> dict:
    del copy_scripts
    session = session_payload(root, session_json)
    prefs = session.get("preferences", {})
    selected = set(prefs.get("selected", []))
    liked = set(prefs.get("liked", []))
    candidates = session.get("candidates", [])
    selected_candidates = [item for item in candidates if item.get("candidate_id") in selected]
    if not selected_candidates:
        selected_candidates = [item for item in candidates if item.get("candidate_id") in liked]
    bundle_dir = session_json.parent / "export_bundle"
    bundle = {
        "schema_version": "agentfiguregallery.reference_bundle.v1",
        "session_id": session.get("session_id"),
        "resolved": session.get("resolved", {}),
        "selected_references": selected_candidates,
        "preferences": prefs,
        "upstream_agent_prompt": (
            "Use the selected_references as visual and code references. "
            "Preserve stable candidate IDs in notes and inspect source metadata before implementing."
        ),
    }
    write_json(bundle_dir / "reference_bundle.json", bundle)
    return bundle


def make_handler(root: Path):
    static_root = root / "frontend" / "reference_gallery"

    class GalleryHandler(BaseHTTPRequestHandler):
        server_version = "AgentFigureGallery/0.1"

        def log_message(self, fmt: str, *args) -> None:  # noqa: A003
            return

        def send_json(self, payload: dict | list, status: int = 200) -> None:
            data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def send_error_json(self, message: str, status: int = 400) -> None:
            self.send_json({"error": message}, status=status)

        def read_body(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def serve_static(self, path: Path) -> None:
            if not path.exists() or not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            data = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mimetypes.guess_type(str(path))[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                if parsed.path == "/":
                    self.serve_static(static_root / "index.html")
                elif parsed.path.startswith("/static/"):
                    self.serve_static(static_root / parsed.path.removeprefix("/static/"))
                elif parsed.path == "/api/sessions":
                    self.send_json({"sessions": discover_sessions(root)})
                elif parsed.path == "/api/session":
                    query = parse_qs(parsed.query)
                    self.send_json(session_payload(root, resolve_session(root, (query.get("session") or [None])[0])))
                elif parsed.path == "/media":
                    query = parse_qs(parsed.query)
                    self.serve_static(safe_path(root, (query.get("path") or [""])[0]))
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)
            except Exception as exc:  # noqa: BLE001
                self.send_error_json(str(exc), status=400)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                body = self.read_body()
                if parsed.path == "/api/generate":
                    plot_type = body.get("plot_type")
                    if not plot_type:
                        raise ValueError("plot_type is required")
                    session = generate_session(
                        root=root,
                        plot_type=plot_type,
                        task=body.get("task") or f"Reference session for {plot_type}",
                        limit=int(body.get("limit") or 50),
                        session_id=body.get("session_id") or f"gallery_{plot_type}",
                        strategy=body.get("strategy") or "explore",
                        seed=int(body["seed"]) if body.get("seed") not in {None, ""} else None,
                    )
                    self.send_json(session)
                elif parsed.path == "/api/preferences":
                    self.send_json(update_preference(root, resolve_session(root, body.get("session")), body))
                elif parsed.path == "/api/export":
                    self.send_json(export_bundle(root, resolve_session(root, body.get("session")), bool(body.get("copy_scripts"))))
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)
            except Exception as exc:  # noqa: BLE001
                self.send_error_json(str(exc), status=400)

    return GalleryHandler


def run_server(*, root: Path, host: str = "127.0.0.1", port: int = 8765) -> int:
    server = ThreadingHTTPServer((host, port), make_handler(root.resolve()))
    print(f"Serving AgentFigureGallery at http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0

