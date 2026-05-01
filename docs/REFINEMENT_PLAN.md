# Refinement Plan

## Goal

Turn the current development workspace into a clean public repository without losing the value of the large local corpus.

## Stage 1: Carve the Public Core

Move or copy only stable, reusable components:

- CLI controller and reference-session backend
- reference gallery frontend
- preference persistence logic
- bundle export logic
- templates and design cards
- Codex skill wrapper
- small tests and smoke examples

Do not copy raw discovery repos or generated outputs into git.

## Stage 2: Normalize Public Commands

Expose user-facing commands around the loop:

```bash
agentfiguregallery query
agentfiguregallery gallery
agentfiguregallery prefer
agentfiguregallery bundle
agentfiguregallery act
agentfiguregallery assets download
```

Keep old internal script names as implementation details until the public CLI is stable.

## Stage 3: Build the Minimal Pack

Create a tiny pack that proves the system works:

- 10 plot types
- 5 to 10 visible candidates per plot type
- stable candidate IDs
- source metadata
- license metadata
- a few copied scripts for selected-reference demos

This pack should be small enough for GitHub and CI.

Initial policy: seed this pack from `global_like` candidates, because those are already human-approved through the gallery loop. Preserve the saved session plot-type context instead of collapsing one global key into one candidate, and filter private-path signals such as massspec, MSagent, personalhpc, aimslight, and yifanl. If one plot type has no Glike examples yet, add a small manually selected fallback only after recording the reason in the pack manifest.

## Stage 4: Publish the Preview Pack

Generate the public-preview pack from the current local candidate index:

- include all curated preview images
- include candidate index and facets
- include source attribution
- exclude raw upstream `.git` directories and raw data

Preferred host: Hugging Face Dataset or GitHub Release asset for the first version.

## Stage 5: Add CI

CI should verify:

- package installs
- `download_assets.py --pack minimal` works against real URLs
- gallery server starts
- a reference session can be generated
- preferences persist
- bundle export includes stable IDs

## Stage 6: Public Launch

GitHub launch checklist:

- short demo GIF
- screenshot of gallery with stable candidate IDs
- screenshot or snippet of exported bundle
- clear license and third-party attribution policy
- roadmap with contribution instructions for new reference packs
