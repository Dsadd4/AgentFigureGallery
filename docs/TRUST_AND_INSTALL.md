# Trust and Install Notes

AgentFigureGallery should be easy to try without hiding what the installer does.

## One-command Install

```bash
curl -fsSL https://raw.githubusercontent.com/Dsadd4/AgentFigureGallery/main/scripts/install.sh | bash
```

The script is intended for Codex users who want the gallery and skill wrapper available immediately.

It does this:

- clones or updates this repository at `$HOME/AgentFigureGallery`;
- creates `$HOME/AgentFigureGallery/.venv`;
- installs the Python package in editable mode;
- installs the Codex skill wrapper into `$CODEX_HOME/skills` or `$HOME/.codex/skills`;
- runs `agentfiguregallery doctor` so failures are visible.

It does not do this:

- modify shell startup files;
- upload local data;
- install the full public reference pack unless you run `agentfiguregallery setup`;
- replace existing global agent configuration outside the skill wrapper path.

## First Run

After installing, run:

```bash
~/AgentFigureGallery/.venv/bin/agentfiguregallery first-run --open
```

This creates a starter embedding-plot reference session, opens the local gallery, and prints the bundle command to run after you select examples.

If you activated the virtual environment first, `agentfiguregallery first-run --open` is equivalent.

## Manual Install

```bash
git clone https://github.com/Dsadd4/AgentFigureGallery.git
cd AgentFigureGallery
python -m venv .venv
source .venv/bin/activate
pip install -e .
agentfiguregallery doctor
agentfiguregallery install-skill --target codex
```

## Installed Paths

| Item | Default path |
| --- | --- |
| Repository | `$HOME/AgentFigureGallery` |
| Python environment | `$HOME/AgentFigureGallery/.venv` |
| Codex skill | `$CODEX_HOME/skills/agent-figure-gallery` or `$HOME/.codex/skills/agent-figure-gallery` |
| Local sessions | `$HOME/AgentFigureGallery/outputs/reference_sessions` |

## Uninstall

Remove the repository and the installed skill wrapper:

```bash
rm -rf "$HOME/AgentFigureGallery"
rm -rf "${CODEX_HOME:-$HOME/.codex}/skills/agent-figure-gallery"
```

If you installed manually somewhere else, remove that checkout and the corresponding skill directory.

## Full Reference Pack

The default checkout includes a small reference pack for smoke tests. The full public pack is larger and is installed only when you run:

```bash
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
```
