# Human Preference Loop

## Goal

Turn human visual judgement into an agent-readable plotting decision.

## Loop

1. Agent receives a plotting task.
2. Agent queries by task, plot type, subtype, motif, or design pattern.
3. Backend creates a reference session with visible candidates.
4. Human marks candidates:
   - `like`: good for this plot type or task
   - `reject`: bad for this plot type or task
   - `select`: use this candidate for the current action
   - `global_like`: generally valuable across tasks
   - `global_reject`: should not appear again
5. Backend exports a bundle.
6. Agent reads the bundle and writes, revises, or critiques code.

## Stable IDs

Every candidate must have a stable ID such as:

```text
BAR-...
HEAT-...
BOX-...
SCAT-...
```

Session-local IDs like `B01` or `H03` are useful for quick UI references but must not be used as permanent identifiers.

## Preference Scope

Local preferences are plot-type aware. A candidate rejected for `bar_chart` should not automatically disappear from `multi_panel_figure`.

Global preferences are cross-task memory:

- `global_reject` hides the candidate from future generated sessions.
- `global_like` increases trust or keeps the candidate visible.

## Bundle Contract

A selected bundle should contain:

- selected candidate IDs
- preview paths
- source repository metadata
- source script paths or copied scripts
- recommended template
- recommended palette
- plot-type self-check
- upstream-agent prompt

The upstream agent should not guess from screenshots alone. It should inspect the selected code and template before acting.

