# P0 Onboarding And Hugging Face Space Retro

Date: 2026-05-29

This note records the growth-oriented expansion that turned AgentFigureGallery from a repository that explains the workflow into a project that visitors can understand, trust, and try quickly.

## Goal

Reduce the gap between interest and first successful use.

The target visitor should be able to answer three questions in the first minute:

- What does AgentFigureGallery do?
- Can I trust the install path?
- What is the shortest path to seeing it work?

## What Changed

### First-run CLI

Added:

```bash
agentfiguregallery first-run --open
```

Why it matters:

- hides the multi-step gallery setup from new users;
- creates a starter reference session with real candidates;
- opens the local gallery when requested;
- prints the next bundle command after session creation.

Reusable rule: first-run commands should produce one visible success state and one concrete next command.

### README Quick Paths

Added a compact table near the top of both README files:

- first successful local run;
- bootstrap install;
- Awesome Skills install;
- install trust notes;
- live Hugging Face showcase;
- community pack contribution.

Why it matters:

- users scan tables faster than paragraphs;
- maintainers can point different audiences to the right path;
- the README now serves both developers and first-time evaluators.

Reusable rule: put the fastest useful action above detailed setup, but link to trust and manual-install docs nearby.

### Trust And Install Notes

Added `docs/TRUST_AND_INSTALL.md`.

The page states what the bootstrap script does, what it does not do, where files are installed, how to run the first session, and how to uninstall.

Why it matters:

- `curl | bash` creates understandable trust friction;
- the project should not ask users to trust hidden behavior;
- install transparency makes sharing safer.

Reusable rule: any one-command installer should have a plain-language trust page linked from the README.

### Static Hugging Face Space

Added `spaces/agentfiguregallery-static` and deployed it to:

- https://huggingface.co/spaces/dsadd4/AgentFigureGallery
- https://dsadd4-agentfiguregallery.static.hf.space/index.html

Why static first:

- no Python runtime;
- no server state;
- no full-public pack download;
- fast enough to ship and evaluate;
- good for social sharing and no-install preview.

Reusable rule: launch the no-install showcase as static first. Move to Gradio only when the interaction itself is proven valuable.

## Validation Checklist

Run before committing related onboarding or Space changes:

```bash
python3 -m py_compile agentfiguregallery/cli.py
bash -n scripts/install.sh
git diff --check
python3 -m agentfiguregallery.cli first-run --json --session-id commit_smoke
rm -rf outputs/reference_sessions/commit_smoke
```

Check Markdown and Space asset references:

```bash
python3 - <<'PY'
from pathlib import Path
import re, sys
files = [Path("README.md"), Path("README.zh-CN.md"), Path("docs/HF_SPACE.md"), Path("docs/TRUST_AND_INSTALL.md")]
missing = []
for path in files:
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0]
        if not target or re.match(r"[a-z]+://", target):
            continue
        if not (path.parent / target).resolve().exists():
            missing.append((str(path), target))
if missing:
    print(missing)
    sys.exit(1)
print("local markdown links ok")
PY
```

For visual checks:

- preview `spaces/agentfiguregallery-static` with `python -m http.server`;
- capture desktop and mobile screenshots;
- check that the hero title does not overlap with background text;
- check that command snippets do not overflow on mobile;
- verify the deployed Space returns HTTP 200.

## Pitfalls Found

- Hugging Face Space metadata requires `emoji` to be a real emoji. `AFG` failed validation.
- Static Spaces use the `*.static.hf.space` direct app URL, not the usual `*.hf.space` URL.
- A hero background that already contains large text can collide with the page H1. Use plot output or another low-text visual instead.
- README table cells containing shell pipes should use HTML code with `&#124;` so the command renders cleanly.
- The install script's final prompt must match the README's recommended first run; otherwise onboarding splits into two paths.

## Follow-up Ideas

- Add a short demo video or GIF specifically for the Hugging Face Space.
- Add a Gradio prototype only after the static Space attracts enough visits.
- Add analytics by tracking GitHub stars, HF Space likes, dataset downloads, install-script hits, and issues from first-time users.
- Create launch posts that point first to the Space, then to GitHub for installation.
