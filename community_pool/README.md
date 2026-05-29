# Community Pool

This directory is the Git-reviewed staging area for community-contributed AgentFigureGallery packs.

The pool is not the final asset archive. It should contain only small, inspectable pack definitions, metadata, preview examples, render scripts, and attribution files. Periodic community asset releases are built from accepted pool contributions and distributed through resource manifests.

## How to Contribute

1. Read `docs/COMMUNITY_PACKS.md`.
2. Create a pack under `community_pool/packs/<pack_name>/`.
3. Follow `pack_schema.example.yaml` and `candidate_schema.example.json`.
4. Include visible preview PNGs for every candidate.
5. Keep large raw data, upstream repository mirrors, and generated archives out of Git.
6. Run the validation checklist before opening a PR.

Recommended pack shape:

```text
community_pool/packs/<pack_name>/
  README.md
  pack.yaml
  LICENSES.md
  candidates/
    BAR-EXAMPLE-0001/
      metadata.json
      preview.png
      render.py
      source_data.csv
      requirements.txt
```

## Ask an Agent to Help

You can ask Codex, Claude Code, Cursor, or another coding agent:

```text
Read docs/COMMUNITY_PACKS.md and ExtendAgent/README.md, then prepare a community pack under community_pool/packs/<pack_name>. Render visible previews, write candidate metadata, preserve stable IDs and license/source attribution, run the private-path scan, and summarize what changed.
```

## Validation

Run:

```bash
agentfiguregallery doctor
python scripts/check_private_paths.py --root .
python -m json.tool community_pool/packs/<pack_name>/candidates/<candidate_id>/metadata.json >/dev/null
```

When a community release manifest exists, test installation with:

```bash
agentfiguregallery setup --pack community-latest --manifest-url <community_resource_manifest_url>
agentfiguregallery gallery --plot-type embedding_plot --limit 50 --serve
```
