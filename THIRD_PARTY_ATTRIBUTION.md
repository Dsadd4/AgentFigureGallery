# Third-Party Attribution

AgentFigureGallery indexes public scientific plotting repositories and rendered reference previews.

## Policy

- Every candidate should keep source repository metadata when available.
- Preview images are used as visual references for human-in-the-loop curation.
- Source scripts or notebook excerpts should only be redistributed when license terms permit.
- Private-path candidates are filtered from public packs.
- Full raw upstream repositories are not committed to this GitHub repository.

## Candidate Metadata

Candidate records may include:

- `source_repo`
- `repo`
- `source_output_path_rel`
- `script_path_rel`
- `route_path_rel`
- `reference_candidate_id`

These fields are intended to preserve provenance and help users inspect original sources.

## Public Packs

The public packs are curated and private-filtered. They are not a substitute for reading the original source repository license.

Before redistributing a larger pack, run:

```bash
python scripts/check_private_paths.py --root .
```

