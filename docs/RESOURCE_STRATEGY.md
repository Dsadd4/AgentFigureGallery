# Resource Strategy

## Rule

Git should contain code, contracts, tiny examples, and manifests. Large visual assets should be downloaded on demand.

## Recommended Hosting

Use more than one host if needed:

- GitHub Releases: good for versioned `minimal` and medium preview packs.
- Hugging Face Datasets: best default for large public preview/image/index packs.
- Zenodo: good for frozen DOI snapshots.
- S3/R2/GCS: good for high-throughput mirrors if traffic grows.

## Pack Design

### `minimal`

Purpose: CI, README screenshots, smoke tests.

Contents:

- 5 to 10 candidates for each major plot type
- small candidate index
- a few source scripts with permissive licenses
- expected output screenshots

Target size: under 50 MB.

This pack can be committed to git when it stays reasonably small. The current Glike-derived development pack is about 73 MB because it preserves plot-type context from saved sessions while filtering private-path candidates.

### `public-preview`

Purpose: normal public use.

Contents:

- curated preview PNGs
- `reference_candidate_index.json`
- `reference_candidate_facets.json`
- source metadata and license metadata

Target size: preferably under 2 GB per versioned pack.

### `source-scripts`

Purpose: selected bundle export with code context.

Contents:

- script and notebook excerpts needed by candidate references
- original repo metadata
- license files when available

Target size: split by version or plot type if needed.

### `full-corpus`

Purpose: maintainers and research users.

Contents:

- downloaded upstream repositories
- extracted script catalog
- discovery metadata

Target size: no hard limit. This should not be required by the normal quickstart.

## Manifest Contract

Each pack entry should include:

- `pack`
- `url`
- `path`
- `sha256`
- `size_bytes`
- `description`

The downloader should support:

- skip existing verified files
- resume `.part` downloads when the server supports `Range`
- checksum verification
- dry-run mode

## One-Command Install Pattern

Public quickstart:

```bash
python scripts/download_assets.py --pack public-preview
```

Future packaged command:

```bash
agentfiguregallery assets download --pack public-preview
```
