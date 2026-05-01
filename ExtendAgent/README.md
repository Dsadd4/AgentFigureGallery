# ExtendAgent

This folder is for agents that expand AgentFigureGallery.

The mission is to discover high-quality public scientific plotting sources, turn them into visible reference candidates, and preserve human preference signals.

## Trigger

Use this workflow when the user asks to expand the gallery, improve low-coverage plot types, add Cell/Science/Nature/PNAS/eLife-style references, or ingest public plotting repositories.

## Non-Negotiable Rules

1. Every useful reference must become visible.
   A script without a preview is not enough for the human selection loop.

2. Preserve stable IDs.
   Use stable `candidate_id` values like `HEAT-...`; session slots like `H03` are temporary.

3. Preserve human preference memory.
   Do not overwrite:
   - `data/reference_global_preferences.json`
   - `outputs/reference_sessions/**/preferences.json`

4. Keep private assets out of public packs.
   Exclude candidates containing private-path signals such as:
   - `massspec`
   - `MSagent`
   - `personalhpc`
   - `aimslight`
   - `yifanl/`

5. Respect source licenses.
   Keep source repository metadata and license metadata with every candidate.

## Expansion Loop

For a full Drawing development KB:

```bash
python3 scripts/drawing_agent_cli.py github-discovery \
  --profile expanded \
  --pages 2 \
  --per-page 50 \
  --inspect-limit 120 \
  --apply-top 30 \
  --min-score 58 \
  --run-ingest \
  --json
```

For low-coverage plot types:

```bash
nohup .venv-nature-plot/bin/python scripts/run_agentexpand_overnight.py \
  --profile low_coverage \
  --pages 4 \
  --per-page 50 \
  --inspect-limit 280 \
  --apply-top 40 \
  --min-score 58 \
  --pause 8 \
  --json \
  > outputs/agentexpand_overnight/overnight_<timestamp>.log 2>&1 &
```

After expansion, rebuild visible candidates:

```bash
python3 scripts/drawing_agent_cli.py reference-index --overwrite
```

Then refresh the public minimal pack from human-approved global likes:

```bash
python3 AgentFigureGallery/scripts/build_minimal_pack_from_glikes.py --overwrite
```

## Quality Gate

Accept sources that have at least one strong signal:

- paper reproduction repository with figures or notebooks
- publication-quality plotting gallery
- high-quality scientific plotting style library
- domain-specific visualization examples with clear scripts and outputs

Reject or downgrade:

- awesome lists
- course homework
- prompt collections
- repositories without scripts or visible outputs
- private or local-only paths

## Required Report

Every expansion agent must report:

- raw GitHub result count
- inspected repository count
- accepted repository count
- candidate count before and after
- selectable count by plot type
- private-path scan result
- top new sources by candidate contribution

