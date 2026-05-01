# Agent Quickstart

Use AgentFigureGallery before writing publication figure code.

## One Prompt

```text
Use AgentFigureGallery as your scientific figure taste memory.
First query visual references for my plotting task, open a gallery for human like/reject/select feedback, then export a bundle and implement the figure from the selected references.
Read skills/agent-figure-gallery/SKILL.md before acting.
```

## Minimal Flow

One-command bootstrap:

```bash
curl -fsSL https://raw.githubusercontent.com/Dsadd4/AgentFigureGallery/main/scripts/install.sh | bash
```

Manual flow:

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

## Agent Skill Install

```bash
agentfiguregallery install-skill --target codex
agentfiguregallery install-skill --target claude-code
agentfiguregallery install-skill --target cursor
agentfiguregallery install-cursor-rule --project /path/to/your-cursor-project
```

This copies only the lightweight skill wrapper into the target agent's personal skill directory. The visual KB stays in the AgentFigureGallery clone and is located through `AGENT_FIGURE_GALLERY_ROOT`.

Default personal locations:

- Codex: `~/.codex/skills/agent-figure-gallery`
- Claude Code: `~/.claude/skills/agent-figure-gallery`
- Cursor-compatible: `~/.cursor/skills/agent-figure-gallery`
- Cursor Project Rule: `.cursor/rules/agent-figure-gallery.mdc` in the target project

Project-local install is also available:

```bash
agentfiguregallery install-skill --target claude-code --scope project
agentfiguregallery install-skill --target cursor --scope project
```

Claude Code officially discovers project skills from `.claude/skills`. Cursor's official reusable instruction system is `.cursor/rules`; the Cursor target is provided as a SKILL.md-compatible bridge for users following the emerging Cursor skills convention.

Bootstrap variants:

```bash
AFG_AGENT_TARGETS="codex claude-code cursor" bash scripts/install.sh
AFG_CURSOR_PROJECT=/path/to/your-cursor-project AFG_AGENT_TARGETS="cursor" bash scripts/install.sh
AFG_INSTALL_FULL_PUBLIC=1 bash scripts/install.sh
```
