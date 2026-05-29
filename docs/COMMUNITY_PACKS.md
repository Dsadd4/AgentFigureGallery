# Community Packs

Community packs are the long-term contribution path for AgentFigureGallery. The goal is to let users contribute excellent plotting code and visual references without turning the Git repository into a large asset dump.

The system has three layers:

1. `full-public`: the canonical 16k+ base pack maintained by Dsadd4.
2. `community_pool/`: a Git-reviewed staging pool for small, inspectable contribution packs.
3. Community asset releases: periodic, versioned packs built from accepted pool contributions and published through manifests.

Users can keep using the base pack, or selectively install community packs that match their domain, style, or plot type.

## Contribution Routes

### Route 1: Propose Sources

Open a Gallery Expansion or Community Pack issue when you have useful public repositories, papers, plotting galleries, or lab examples but have not packaged them yet.

Good proposals include:

- public source links
- expected plot types
- why the visual style is useful
- license or attribution notes
- whether the source can be rendered reproducibly

### Route 2: Submit a Community Pack PR

Open a PR under:

```text
community_pool/packs/<pack_name>/
```

Use the schema examples in `community_pool/` as the contract. A pack PR should contain small, reviewable files only. Large archives, raw upstream mirrors, and full datasets must be published as release assets or external pack entries instead of being committed to Git.

### Route 3: Maintainer Asset Release

Accepted pool contributions are periodically folded into community asset releases such as:

```text
community-2026-05
community-bio-2026-q2
community-spatial-2026-q2
```

The release process produces a resource manifest so users can install only the packs they want.

## Pack Layout

A community pack should use this shape:

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

`preview.png` is required. `render.py` and small source data are strongly preferred. If a candidate is visual-only, mark it explicitly in metadata.

## Candidate Contract

Each candidate must provide:

- stable `candidate_id`
- `plot_type`
- visible `preview_path`
- source code path or `visual_only: true`
- source repository, paper, author, or file attribution
- license metadata when available
- tags or style notes that help retrieval

Valid `plot_type` values:

- `bar_chart`
- `benchmark_performance`
- `box_violin_distribution`
- `embedding_plot`
- `heatmap_matrix`
- `line_chart`
- `microscopy_panel`
- `multi_panel_figure`
- `scatter_plot`
- `spatial_map`

## Quality Gates

A contribution is eligible for the public community pool only when:

- every accepted reference has a visible preview PNG
- stable candidate IDs are preserved across revisions
- source and license metadata are preserved
- private paths, tokens, and private repository names are absent
- large generated outputs are not committed to Git
- the pack can be inspected in the browser gallery
- the contribution improves scientific figure guidance rather than adding generic images

Rejected or weak references should not be silently mixed into the pool. Use the gallery preference loop to preserve negative feedback when it is useful.

## Private Packs

Users with internal plotting code can keep a private local pack. Private packs should stay out of public Git and may include lab-specific paths, local data, or unpublished results. They should still follow the same metadata contract so the browser gallery and agent bundle workflow can read them.

Do not submit private packs unless all data, figures, and licenses are cleared for public release.

## Installing Community Packs

Base install:

```bash
agentfiguregallery setup --pack full-public --manifest-url https://huggingface.co/datasets/dsadd4/AgentFigureGallery/resolve/main/resource_manifest.json
```

After a community manifest is published, install a selected community pack:

```bash
agentfiguregallery setup --pack community-latest --manifest-url <community_resource_manifest_url>
agentfiguregallery gallery --plot-type embedding_plot --limit 50 --serve
```

Domain-specific packs should be installable the same way:

```bash
agentfiguregallery setup --pack community-bio-2026-q2 --manifest-url <community_resource_manifest_url>
agentfiguregallery setup --pack community-spatial-2026-q2 --manifest-url <community_resource_manifest_url>
```

The current setup command installs one active pack from a manifest. Future pack-management commands can add listing, merging, validation, and selective overlay workflows without changing this contribution contract.

## Review Checklist

Before a community pack PR is reviewed, run:

```bash
agentfiguregallery doctor
python scripts/check_private_paths.py --root .
```

Also confirm:

- candidate metadata JSON files are valid
- pack YAML follows `community_pool/pack_schema.example.yaml`
- previews render in the browser gallery
- source and license metadata are present
- no raw upstream mirrors or large generated archives are committed
