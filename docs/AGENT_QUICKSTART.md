# Agent Quickstart

Use AgentFigureGallery before writing publication figure code.

## One Prompt

```text
Use AgentFigureGallery as your scientific figure taste memory.
First query visual references for my plotting task, open a gallery for human like/reject/select feedback, then export a bundle and implement the figure from the selected references.
Read skills/agent-figure-gallery/SKILL.md before acting.
```

## Minimal Flow

```bash
export AGENT_FIGURE_GALLERY_ROOT=/path/to/AgentFigureGallery
agentfiguregallery doctor
agentfiguregallery install-skill --target codex
agentfiguregallery query --task "Nature-style embedding map for cell atlas"
agentfiguregallery gallery --plot-type embedding_plot --task "Nature-style embedding map for cell atlas" --limit 50 --serve
```

After the human chooses candidates:

```bash
agentfiguregallery prefer --session <session_id> --like E01 E02 --reject E04 --select E03
agentfiguregallery bundle --session <session_id>
```

Then read:

```text
outputs/reference_sessions/<session_id>/export_bundle/reference_bundle.json
```

## Rules For Agents

- Do not write final plotting code before querying visual references.
- Preserve stable candidate IDs in notes and commit messages.
- Treat `like` and `reject` as plot-type preferences.
- Treat `global_like` and `global_reject` as reusable cross-task taste memory.
- If no reference fits, ask the human to reject bad candidates and generate another gallery.

## Codex Skill Install

```bash
agentfiguregallery install-skill --target codex
```

This copies only the lightweight skill wrapper into `~/.codex/skills/agent-figure-gallery`. The visual KB stays in the AgentFigureGallery clone and is located through `AGENT_FIGURE_GALLERY_ROOT`.
