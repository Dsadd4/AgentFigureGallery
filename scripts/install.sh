#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${AFG_REPO_URL:-https://github.com/Dsadd4/AgentFigureGallery.git}"
INSTALL_DIR="${AFG_INSTALL_DIR:-$HOME/AgentFigureGallery}"
AGENT_TARGETS="${AFG_AGENT_TARGETS:-codex}"
INSTALL_FULL_PUBLIC="${AFG_INSTALL_FULL_PUBLIC:-0}"
MANIFEST_URL="${AFG_MANIFEST_URL:-https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json}"

log() {
  printf '[AgentFigureGallery] %s\n' "$*"
}

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

python_is_supported() {
  "$1" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
}

select_python() {
  if [ -n "${AFG_PYTHON:-}" ]; then
    if ! command -v "$AFG_PYTHON" >/dev/null 2>&1; then
      printf 'AFG_PYTHON is not executable: %s\n' "$AFG_PYTHON" >&2
      exit 1
    fi
    if ! python_is_supported "$AFG_PYTHON"; then
      printf 'AFG_PYTHON must be Python 3.10 or newer: %s\n' "$AFG_PYTHON" >&2
      exit 1
    fi
    printf '%s\n' "$AFG_PYTHON"
    return
  fi

  for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && python_is_supported "$candidate"; then
      printf '%s\n' "$candidate"
      return
    fi
  done

  printf 'Python 3.10+ is required. Set AFG_PYTHON=/path/to/python3.10+ and rerun.\n' >&2
  exit 1
}

need_command git
PYTHON_BIN="$(select_python)"
need_command "$PYTHON_BIN"

log "repo: $REPO_URL"
log "install dir: $INSTALL_DIR"
log "python: $PYTHON_BIN"

if [ -d "$INSTALL_DIR/.git" ]; then
  log "updating existing clone"
  git -C "$INSTALL_DIR" pull --ff-only
elif [ -e "$INSTALL_DIR" ]; then
  printf 'Install dir already exists but is not a git clone: %s\n' "$INSTALL_DIR" >&2
  printf 'Set AFG_INSTALL_DIR to a different path or move the existing directory.\n' >&2
  exit 1
else
  log "cloning repository"
  mkdir -p "$(dirname "$INSTALL_DIR")"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

log "creating Python environment"
"$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv"
VENV_PY="$INSTALL_DIR/.venv/bin/python"
VENV_CLI="$INSTALL_DIR/.venv/bin/agentfiguregallery"

log "installing package"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -e "$INSTALL_DIR"

export AGENT_FIGURE_GALLERY_ROOT="$INSTALL_DIR"

NORMALIZED_TARGETS="${AGENT_TARGETS//,/ }"
for target in $NORMALIZED_TARGETS; do
  case "$target" in
    codex|claude-code|cursor)
      log "installing agent skill: $target"
      "$VENV_CLI" install-skill --target "$target" --force
      ;;
    *)
      printf 'Unsupported AFG_AGENT_TARGETS item: %s\n' "$target" >&2
      printf 'Supported targets: codex, claude-code, cursor\n' >&2
      exit 1
      ;;
  esac

  if [ "$target" = "cursor" ]; then
    if [ -n "${AFG_CURSOR_PROJECT:-}" ]; then
      log "installing Cursor project rule into $AFG_CURSOR_PROJECT"
      "$VENV_CLI" install-cursor-rule --project "$AFG_CURSOR_PROJECT" --force
    else
      log "Cursor project rule skipped; set AFG_CURSOR_PROJECT=/path/to/project to install .cursor/rules/agent-figure-gallery.mdc"
    fi
  fi
done

log "running doctor"
"$VENV_CLI" doctor

if [ "$INSTALL_FULL_PUBLIC" = "1" ]; then
  log "downloading full-public KB from Hugging Face"
  "$VENV_CLI" setup --pack full-public --manifest-url "$MANIFEST_URL"
else
  log "full-public KB download skipped"
  log "run later: $VENV_CLI setup --pack full-public --manifest-url $MANIFEST_URL"
fi

cat <<EOF

AgentFigureGallery is installed.

Add this to your shell when using the KB:
  export AGENT_FIGURE_GALLERY_ROOT=$INSTALL_DIR

Tell your agent:
  Read the agent-figure-gallery skill, then use AgentFigureGallery before writing publication figure code.

Try:
  $VENV_CLI gallery --plot-type embedding_plot --limit 50 --serve
EOF
