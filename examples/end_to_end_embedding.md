# End-To-End Embedding Example

Goal: make a Nature-style embedding plot for a single-cell atlas without asking the agent to invent the visual style from text alone.

## 1. Ask The Agent

```text
I need a Nature-style embedding plot for a single-cell atlas.
Use AgentFigureGallery first, let me select visual references, then implement the figure from the exported bundle.
```

## 2. Query And Open Candidates

```bash
agentfiguregallery doctor
agentfiguregallery query --task "Nature-style embedding map for cell atlas"
agentfiguregallery gallery --plot-type embedding_plot --task "Nature-style embedding map for cell atlas" --limit 50 --serve
```

The browser gallery shows stable candidate IDs such as `E01`, `E02`, and `E03`.

## 3. Record Human Preference

After the human marks examples in the browser, the same actions can be recorded from the CLI:

```bash
agentfiguregallery prefer --session <session_id> --like E01 E02 --global-like E03 --select E02
```

Use `--reject` for bad references in the current plot type and `--global-reject` for references that should disappear from future sessions.

## 4. Export The Bundle

```bash
agentfiguregallery bundle --session <session_id> --copy-scripts
```

The agent should read:

```text
outputs/reference_sessions/<session_id>/export_bundle/reference_bundle.json
```

## 5. Implement The Plot

The downstream agent should use the selected references as visual and code guidance, preserve candidate IDs in final notes, and only then write or revise the plotting code.

See the runnable generated-plot example:

```text
examples/generated_embedding_plot/README.md
```
